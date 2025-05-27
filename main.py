
from typing import List

from src.supa_client import SupaClient, ApartamentQuery
from src.sync_instance import SyncInstance
from src.y2_ingest_svc import Apartment, Y2Fetcher

if __name__ == "__main__":

    client = SupaClient(
        queries_url='https://kbbcllgitrzhwbyfgevc.supabase.co/rest/v1/queries',
        supabase_url='https://kbbcllgitrzhwbyfgevc.supabase.co/rest/v1/apartaments_ii',
        supabase_key='eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImtiYmNsbGdpdHJ6aHdieWZnZXZjIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDI5Nzg1NzksImV4cCI6MjA1ODU1NDU3OX0.acHkhagTOFGU88812SKyZe39nG4SM_9MpSmEIBMIH6w'
    )
    fetcher = Y2Fetcher()

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
        {
            "key": "dev_query_5k",
            "name": "Local - Up To 5K",
            "url": "https://gw.yad2.co.il/realestate-feed/rent/map?minPrice=4000&maxPrice=5000&minRooms=2&maxRooms=3&property=1&balcony=1&multiCity=8700,6400,6900,9700"
        },
        {
            "key": "dev_query_4k",
            "name": "Local - Up To 4K",
            "url": "https://gw.yad2.co.il/realestate-feed/rent/map?minPrice=3000&maxPrice=4000&minRooms=2&maxRooms=3&property=1&balcony=1&multiNeighborhood=1462&multiCity=8600,6300"
        },


        {
            "key": "rg_query_7k",
            "name": "Ramat Gan - Up To 7K",
            "url": "https://gw.yad2.co.il/realestate-feed/rent/map?minPrice=6000&maxPrice=7000&minRooms=2&maxRooms=3&property=1&balcony=1&multiNeighborhood=1462&multiCity=8600,6300"
        },
        {
            "key": "rg_query_6k",
            "name": "Ramat Gan - Up To 6K",
            "url": "https://gw.yad2.co.il/realestate-feed/rent/map?minPrice=5000&maxPrice=6000&minRooms=2&maxRooms=3&property=1&balcony=1&multiNeighborhood=1462&multiCity=8600,6300"
        },
        {
            "key": "rg_query_5k",
            "name": "Ramat Gan - Up To 5K",
            "url": "https://gw.yad2.co.il/realestate-feed/rent/map?minPrice=4000&maxPrice=5000&minRooms=2&maxRooms=3&property=1&balcony=1&multiNeighborhood=1462&multiCity=8600,6300"
        },
        {
            "key": "rg_query_4k",
            "name": "Ramat Gan - Up To 4K",
            "url": "https://gw.yad2.co.il/realestate-feed/rent/map?minPrice=3000&maxPrice=4000&minRooms=2&maxRooms=3&property=1&balcony=1&multiNeighborhood=1462&multiCity=8600,6300"
        }
    ]

    for search in searches:
        query_name = search['key']
        state = client.get_state(query_name)
        apartments: List[Apartment] = fetcher.fetch_and_parse(name=search['name'].lower(), url=search['url'], fetch=False)
        synchronizer = SyncInstance(query_name)
        ingested = synchronizer.sync(apartments, state)
        client.delete(query_name)
        client.ingest_values(ingested)

        missing = synchronizer.check_missing(apartments, state)
        synchronizer.print(missing, "Missing apartaments")


    client.ingest_queries([ApartamentQuery(search['key'], search['name'], search['url']) for search in searches])

    # TODO: consider if can do w Curl and not selenium to make this deployed
    # TODO: consider getting the descriptions;

