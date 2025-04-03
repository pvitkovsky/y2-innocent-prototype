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
from src.supa_client import SupaClient, SupaState
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


def remove_archived(apartaments: List[Apartment], state: List[SupaState]):
    archivedDict = {apt.id for apt in state if apt.archived}
    return [apt for apt in apartaments if apt['token'] not in archivedDict]


def check_missing(apartaments: List[Apartment], state: List[SupaState]):
    activeDict = {apt['token'] for apt in apartaments}
    return [apt.id for apt in state if apt.id not in activeDict]

def printIds(apartaments: List[Apartment]):
    print(f"Total {len(apartaments)} objects")
    [print(f"{apt['token']}") for apt in apartaments]


if __name__ == "__main__":

    client = SupaClient(
        supabase_url='https://kbbcllgitrzhwbyfgevc.supabase.co/rest/v1/apartaments_ii',
        supabase_key='eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImtiYmNsbGdpdHJ6aHdieWZnZXZjIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDI5Nzg1NzksImV4cCI6MjA1ODU1NDU3OX0.acHkhagTOFGU88812SKyZe39nG4SM_9MpSmEIBMIH6w'
    )
    state = client.get_state("dev_query");

    searches = [
        {
          "name": "Map", # print name
          "url": "https://gw.yad2.co.il/realestate-feed/rent/map?minPrice=4000&maxPrice=5000&minRooms=2&maxRooms=3&property=1&balcony=1&multiCity=8700,6400,6900,9700"
        }
        # TODO: more searches;
    ]

    #
    for search in searches:
        apartaments: List[Apartment] = fetch_and_parse(name=search['name'].lower(), url=search['url'], fetch=False, parse=False)
        filtered = remove_archived(apartaments, state)
        printIds(filtered)

        missing = check_missing(apartaments, state)
        print(missing)

    # dloader = ApartamentImageDownloader()
    # for search in searches:
    #    map: List[Apartment] = fetch_and_parse(name=search['name'].lower(), url=search['url'], fetch=True, parse=True)
    #    # for idx, apt in enumerate(map):
    #    #    dloader.download_all_images(apt)




    # client.deactivate_id("xqq864cf")
    # state = client.get_state("dev_query");
    # print(state)

    #TODO: function that dumps unneeded IDs from Supa (probably a request: deactivated: true)
    #TODO: function that before a search, gets hot IDs from Supa and voids them if search brings none?
    #  ^ is the above a one request? id + boolean dumped?
    #TODO: function that updates Supa

