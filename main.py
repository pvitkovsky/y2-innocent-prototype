
from typing import List

from src.supa_client import SupaClient
from src.sync_instance import SyncInstance
from src.y2_ingest_svc import Apartment, Y2Fetcher

if __name__ == "__main__":

    client = SupaClient(
        supabase_url='https://kbbcllgitrzhwbyfgevc.supabase.co/rest/v1/apartaments_ii',
        supabase_key='eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImtiYmNsbGdpdHJ6aHdieWZnZXZjIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDI5Nzg1NzksImV4cCI6MjA1ODU1NDU3OX0.acHkhagTOFGU88812SKyZe39nG4SM_9MpSmEIBMIH6w'
    )
    fetcher = Y2Fetcher()

    searches = [
        {
          "key": "dev_query_5k",
          "name": "Up To 5K", # print name
          "url": "https://gw.yad2.co.il/realestate-feed/rent/map?minPrice=4000&maxPrice=5000&minRooms=2&maxRooms=3&property=1&balcony=1&multiCity=8700,6400,6900,9700"
        },
        {
            "key": "dev_query_4k",
            "name": "Up To 4K",  # print name
            "url": "https://gw.yad2.co.il/realestate-feed/rent/map?minPrice=3000&maxPrice=4000&minRooms=2&maxRooms=3&property=1&balcony=1&multiCity=8700,6400,6900,9700"
        }
    ]

    # Fetch and Parse:
    for search in searches:
        query_name = search['key']
        state = client.get_state(query_name)
        apartments: List[Apartment] = fetcher.fetch_and_parse(name=search['name'].lower(), url=search['url'], fetch=False, parse=True)
        synchronizer = SyncInstance(query_name)
        filtered = synchronizer.sync(apartments, state)
        client.delete(query_name)
        client.ingest_values(filtered) # TODO: should hard update stuff; delete + insert, not upsert!


    # FOR THE IMAGES; needs archive functionality;
    # dloader = ApartamentImageDownloader()
    # for search in searches:
    #    map: List[Apartment] = fetcher.fetch_and_parse(name=search['name'].lower(), url=search['url'], fetch=True, parse=True)
    #    # for idx, apt in enumerate(map):
    #    #    dloader.download_all_images(apt)


    # client.deactivate_id("xqq864cf")
    # state = client.get_state("dev_query");
    # print(state)

    # TODO: dev and prod envs;
    # TODO: next supa table with the list of queries, how does it get updated?
    # TODO: update the project to use tabs; think first;

