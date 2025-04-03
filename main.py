import dataclasses
import datetime
import json
import os
import time
import re
from typing import List

from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from src.apartament_img import ApartamentImageDownloader
from src.selenuim.base_page import BasePage
from src.y2_ingest_svc import Y2IngestService, Apartment


class EnhancedJSONEncoder(json.JSONEncoder):
    def default(self, o):
        if dataclasses.is_dataclass(o):
            return dataclasses.asdict(o)
        return super().default(o)

def save_raw_file(name: str, url: str):
    options = Options()
    driver = webdriver.Chrome(options=options)
    try:
        page = BasePage(driver)
        page.open(url)
        time.sleep(1)
        match = re.search("{.*}", driver.page_source)
        if match:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{name}_{timestamp}.json"
            with open(filename, "w", encoding="utf-8") as f:
                f.write(match.group(0))
            print(f"Page saved as: {filename}")
    finally:
        driver.quit()


def get_latest_json(name: str) -> str:
    files = [f for f in os.listdir('.') if f.startswith(name) and f.endswith('.json')]
    if not files:
        raise FileNotFoundError(f"No files found for name: {name}")

    latest_file = max(files, key=os.path.getmtime)  # Get the most recently modified file
    print(f"Latest JSON file: {latest_file}")
    return latest_file


def fetch_and_parse(name: str, url: str, fetch=True, parse=True):
    if fetch:
        save_raw_file(name, url)

    source = get_latest_json(name)
    if parse:
        with open(source, "r") as f:
            data = f.read()
            svc = Y2IngestService(data)
            print(json.dumps(svc.transform_data(), cls=EnhancedJSONEncoder))
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"parsed_{name}_{timestamp}.json"
            with open(filename, "w", encoding="utf-8") as f:
                f.write(json.dumps(svc.transform_data(), cls=EnhancedJSONEncoder))
                print(f"Parsed JSON saved as: {filename}")

    parsed = get_latest_json('parsed')
    with open(parsed, "r") as f:
        res: List[Apartment] = json.loads(f.read())
        return res


if __name__ == "__main__":

    searches = [
        { 
          "name": "Map", # print name
          "url": "https://gw.yad2.co.il/realestate-feed/rent/map?minPrice=4000&maxPrice=5000&minRooms=2&maxRooms=3&property=1&balcony=1&multiCity=8700,6400,6900,9700"
        }
        # TODO: more searches;
    ]

    dloader = ApartamentImageDownloader()
    for search in searches:
       map: List[Apartment] = fetch_and_parse(name=search['name'].lower(), url=search['url'], fetch=True, parse=True)
       # for idx, apt in enumerate(map):
       #    dloader.download_all_images(apt)

    #TODO: function that dumps unneeded IDs from Supa (probably a request: deactivated: true)
    #TODO: function that before a search, gets hot IDs from Supa and voids them if search brings none?
    #  ^ is the above a one request? id + boolean dumped?
    #TODO: function that updates Supa
