
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
          "key": "dev_query",
          "name": "Map", # print name
          "url": "https://gw.yad2.co.il/realestate-feed/rent/map?minPrice=4000&maxPrice=5000&minRooms=2&maxRooms=3&property=1&balcony=1&multiCity=8700,6400,6900,9700"
        }
        # TODO: more searches;
    ]

    for search in searches:
        state = client.get_state(search['key']);
        apartments: List[Apartment] = fetcher.fetch_and_parse(name=search['name'].lower(), url=search['url'], fetch=True, parse=True)
        synchronizer = SyncInstance(search['key'])
        filtered = synchronizer.sync(apartments, state)
        client.ingest_values(filtered) # TODO: should hard update stuff;


    # FOR THE IMAGES; needs archive functionality;
    # dloader = ApartamentImageDownloader()
    # for search in searches:
    #    map: List[Apartment] = fetcher.fetch_and_parse(name=search['name'].lower(), url=search['url'], fetch=True, parse=True)
    #    # for idx, apt in enumerate(map):
    #    #    dloader.download_all_images(apt)


    # client.deactivate_id("xqq864cf")
    # state = client.get_state("dev_query");
    # print(state)

    #TODO: function that dumps unneeded IDs from Supa (probably a request: deactivated: true)
    #TODO: function that before a search, gets hot IDs from Supa and voids them if search brings none?
    #  ^ is the above a one request? id + boolean dumped?
    #TODO: function that updates Supa

