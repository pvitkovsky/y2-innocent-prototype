from dataclasses import dataclass, asdict
from typing import List

from src.supa_client import SupaClient, ApartamentQuery, SupaState
from src.sync_instance import SyncInstance
from src.y2_ingest_svc import Apartment, Y2Fetcher, IngestedApartament, ScoredApartament


def add_scores(apartment: Apartment)-> ScoredApartament:
    return ScoredApartament(**asdict(apartment), gui_score = 1)


def gpu_filter(apartments: List[Apartment]) -> List[Apartment]:
    scored = [add_scores(apt) for apt in apartments]
    res = [scoredApt for scoredApt in scored if scoredApt.gui_score > 0.5]
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
        apartments: List[Apartment] = fetcher.fetch_and_parse(name=search['name'].lower(), url=search['url'], fetch=fetch)
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


if __name__ == "__main__":


    searches: List[dict] = [
        {
            "key": "dev_query_7k",
            "name": "Local - Up To 7K",
            "url": "https://gw.yad2.co.il/realestate-feed/rent/map?minPrice=6000&maxPrice=7000&minRooms=2&maxRooms=3&property=1&balcony=1&multiCity=8700,6400,6900,9700"
        },
        {
            "key": "dev_query_6k",
            "name": "Local - Up To 6K",
            "url": "https://gw.yad2.co.il/realestate-feed/rent/map?minPrice=5000&maxPrice=6000&minRooms=2&maxRooms=3&property=1&balcony=1&multiCity=8700,6400,6900,9700"
        },
        # {
        #     "key": "dev_query_5k",
        #     "name": "Local - Up To 5K",
        #     "url": "https://gw.yad2.co.il/realestate-feed/rent/map?minPrice=4000&maxPrice=5000&minRooms=2&maxRooms=3&property=1&balcony=1&multiCity=8700,6400,6900,9700"
        # },
        # {
        #     "key": "dev_query_4k",
        #     "name": "Local - Up To 4K",
        #     "url": "https://gw.yad2.co.il/realestate-feed/rent/map?minPrice=3000&maxPrice=4000&minRooms=2&maxRooms=3&property=1&balcony=1&multiNeighborhood=1462&multiCity=8600,6300"
        # },


        # {
        #     "key": "rg_query_7k",
        #     "name": "Ramat Gan - Up To 7K",
        #     "url": "https://gw.yad2.co.il/realestate-feed/rent/map?minPrice=6000&maxPrice=7000&minRooms=2&maxRooms=3&property=1&balcony=1&multiNeighborhood=1462&multiCity=8600,6300"
        # },
        # {
        #     "key": "rg_query_6k",
        #     "name": "Ramat Gan - Up To 6K",
        #     "url": "https://gw.yad2.co.il/realestate-feed/rent/map?minPrice=5000&maxPrice=6000&minRooms=2&maxRooms=3&property=1&balcony=1&multiNeighborhood=1462&multiCity=8600,6300"
        # },
        # {
        #     "key": "rg_query_5k",
        #     "name": "Ramat Gan - Up To 5K",
        #     "url": "https://gw.yad2.co.il/realestate-feed/rent/map?minPrice=4000&maxPrice=5000&minRooms=2&maxRooms=3&property=1&balcony=1&multiNeighborhood=1462&multiCity=8600,6300"
        # },
        {
            "key": "rg_query_4k",
            "name": "Ramat Gan - Up To 4K",
            "url": "https://gw.yad2.co.il/realestate-feed/rent/map?minPrice=3000&maxPrice=4000&minRooms=2&maxRooms=3&property=1&balcony=1&multiNeighborhood=1462&multiCity=8600,6300"
        }
    ]

    # UNCOMMENT TO UPDATE PORTAL
    update_portal(searches, False) # TODO: fix supa calls; sth off;



    # TODO: consider having at least launch args to fetch or dry run; as well, cron job on my gaming pc to sync;
    # TODO: consider if can do w Curl and not selenium to make this deployed
    # TODO: consider getting the descriptions;