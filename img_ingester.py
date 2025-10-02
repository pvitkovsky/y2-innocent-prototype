
from typing import List

from src.apartament_img import ApartamentImageDownloader
from src.supa_client import SupaClient, ApartamentQuery, SupaState
from src.sync_instance import SyncInstance
from src.y2_ingest_svc import Apartment, Y2Fetcher, IngestedApartment

searches: List[dict] = [
    {
        "key": "dev_query_7k",
        "name": "Local - Up To 7K",
        "url": "https://gw.yad2.co.il/realestate-feed/rent/map?minPrice=6000&maxPrice=7000&minRooms=2&maxRooms=3&property=1&balcony=1&multiCity=8700,6400,6900,9700"
    },
    # {
    #     "key": "dev_query_6k",
    #     "name": "Local - Up To 6K",
    #     "url": "https://gw.yad2.co.il/realestate-feed/rent/map?minPrice=5000&maxPrice=6000&minRooms=2&maxRooms=3&property=1&balcony=1&multiCity=8700,6400,6900,9700"
    # },
    # {
    #     "key": "rg_query_4k",
    #     "name": "Ramat Gan - Up To 4K",
    #     "url": "https://gw.yad2.co.il/realestate-feed/rent/map?minPrice=3000&maxPrice=4000&minRooms=2&maxRooms=3&property=1&balcony=1&multiNeighborhood=1462&multiCity=8600,6300"
    # }
]

# # UNCOMMENT TO GET IMGS
fetcher = Y2Fetcher()
dloader = ApartamentImageDownloader()

for search in searches:
   map: List[Apartment] = fetcher.fetch_and_parse_legacy(name=search['name'].lower(), url=search['url'], fetch=True)
   for idx, apt in enumerate(map):
      dloader.download_all_images(apt) #apt.head for dry runs

