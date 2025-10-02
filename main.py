import dataclasses
from dataclasses import dataclass, asdict
from typing import List

from src.supa_client import SupaClient, ApartamentQuery, SupaState
from src.sync_instance import SyncInstance
from src.y2_ingest_svc import Apartment, Y2Fetcher, IngestedApartment, ScoredApartment, VectoredApartment


# TODO: debug 4cqlio72, z3odafio - why they got up here?
def add_scores(apartment: VectoredApartment)-> ScoredApartment:
    valid_scores = []

    for img in apartment.scoredImages:
        room_probs = img["room_type"]
        if room_probs.get("living room") >= 0.66 or room_probs.get("bedroom") >= 0.66 or room_probs.get("kitchen") >= 0.66:
            empty_score = img["occupancy"]["empty"]
            valid_scores.append(empty_score)

    if not valid_scores:
        return ScoredApartment(**asdict(apartment), guiScore= 0)

    avg_empty = sum(valid_scores) / len(valid_scores)
    return ScoredApartment(**asdict(apartment), guiScore= avg_empty)


def gpu_filter(apartments: List[VectoredApartment]) -> List[ScoredApartment]:
    scored = [add_scores(apt) for apt in apartments]
    res = [scoredApt for scoredApt in scored if scoredApt.guiScore > 0.51]
    return res


def update_portal(searches: List[dict], fetch = True):

    client = SupaClient(
        queries_url='https://zysuftctsbaahhbcpfkp.supabase.co/rest/v1/queries',
        supabase_url='https://zysuftctsbaahhbcpfkp.supabase.co/rest/v1/apartaments_ii',
        supabase_key='eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inp5c3VmdGN0c2JhYWhoYmNwZmtwIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDk3MTY1NzQsImV4cCI6MjA2NTI5MjU3NH0.Xd4XRqDCtxPivH_ilyB8EiG9UTR1Npi8xzYFO1OA9_I'
    )
    fetcher = Y2Fetcher()


    for search in searches:
        query_name = search['key']
        state = client.get_state(query_name)
        apartments: List[VectoredApartment] = fetcher.load_vectorised(name=search['name'].lower())
        # scores: ScoredApartament (?)
        apartments = gpu_filter(apartments)
        # needs filtering;
        synchronizer = SyncInstance(query_name)
        ingested = synchronizer.sync(apartments, state)
        client.delete(query_name)
        client.ingest_values(ingested)

        # TODO: whatever next in terms of client synchro comes, IDK;
        # missing: List[SupaState] = synchronizer.check_missing(apartments, state)
        # favs_missing = list(filter(lambda a: a.score is not None, missing))
        # print(f"Missing apartaments {len(missing)}, "
        #                    f" favourites missing: {len(favs_missing)}")
        # if len(favs_missing) > 0:
        #     synchronizer.extended_print(favs_missing)

    client.ingest_queries([ApartamentQuery(search['key'], search['name'], search['url']) for search in searches])


# WORKFLOW:
# 1) Run img_ingester on these searches, optionally with fetching latest JSONs too
# 2) copy result jsons (parsed_local - up to ...) into pretrained apt classifier, run it
# 3) copy parsed_vector... into here, run main
if __name__ == "__main__":


    searches: List[dict] = [
        {
            "key": "dev_query_7k",
            "name": "Local - Up To 7K",
            "url": "https://gw.yad2.co.il/realestate-feed/rent/map?minPrice=6000&maxPrice=7000&minRooms=2&maxRooms=3&property=1&balcony=1&multiCity=8700,6400,6900,9700"
        },
    ]

    update_portal(searches, False)