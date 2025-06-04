from dataclasses import dataclass
import dataclasses
import datetime
import json
import os
import re
import time
from dataclasses import dataclass
from typing import List

from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from src.selenuim.base_page import BasePage


@dataclass
class Coords():
    lon: float
    lat: float

@dataclass
class Metadata():
    coverImage: str
    images: List[str]
    squareMeterBuild: float

@dataclass
class Apartment():
    coords: Coords
    price: float
    token: str
    squareMeter: float
    pricePerMeter: float
    roomsCount: int
    metadata: Metadata

@dataclass
class IngestedApartament():
    data: Apartment
    query_name: str

class Y2IngestService:
    def __init__(self, source_json: str):
        self.source_json = source_json

    def transform_data(self) -> List[Apartment]:
        try:
            data = json.loads(self.source_json)
            apartments = [self.process(apt) for apt in data['data']['markers']]
            filtered_apartaments = [apt for apt in apartments if apt is not None]
            sorted_apartments = sorted(filtered_apartaments, key=lambda x: x.pricePerMeter)
            return sorted_apartments
        except json.JSONDecodeError:
            raise "'Error: Invalid JSON input'"

    def process(self, apt):
        try:
                return Apartment(
                coords=Coords(apt['address']['coords']['lon'], apt['address']['coords']['lat']),
                price=apt['price'],
                token=apt['token'],
                squareMeter=apt['additionalDetails']['squareMeter']  if apt['additionalDetails'].get(
                    'squareMeter') else 1,
                pricePerMeter=apt['price'] / apt['additionalDetails']['squareMeter'] if apt['additionalDetails'].get(
                    'squareMeter') else 0,
                roomsCount=apt['additionalDetails']['roomsCount'],
                metadata=Metadata(
                    coverImage=apt['metaData']['coverImage'] if apt['metaData']['coverImage'] else None,
                    images=apt['metaData']['images'],
                    squareMeterBuild=apt['metaData']['squareMeterBuild'] if apt['metaData'].get(
                    'squareMeterBuild') else 1
                )
            )
        except Exception:
            return None

# Example usage (assuming you have sourceJson and a function setTransformedJson):
# sourceJson = '{"data": {"markers": [{"address": {"coords": {"lon": 34.8, "lat": 32.1}}, "price": 1500000, "token": "abc1", "additionalDetails": {"squareMeter": 100, "roomsCount": 3}, "metaData": {"coverImage": "img1.jpg", "images": ["img1.jpg", "img2.jpg"], "squareMeterBuild": 120}}, {"address": {"coords": {"lon": 34.9, "lat": 32.2}}, "price": 1200000, "token": "def2", "additionalDetails": {"squareMeter": 80, "roomsCount": 2}, "metaData": {"coverImage": "img3.jpg", "images": ["img3.jpg"], "squareMeterBuild": 90}}]}}'
# def setTransformedJson(json_str):
#     print(f"Transformed JSON: {json_str}")
#
# ingest_service = Y2IngestService(sourceJson, setTransformedJson)
# sorted_apartments = ingest_service.transform_data()
# if sorted_apartments:
#     print("\nSorted Apartments:")
#     for apartment in sorted_apartments:
#         print(apartment)

class EnhancedJSONEncoder(json.JSONEncoder):
    def default(self, o):
        if dataclasses.is_dataclass(o):
            return dataclasses.asdict(o)
        return super().default(o)

class Y2Fetcher():

    def __save_raw_file__(self, name: str, url: str):
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


    def __get_latest_json__(self, name: str) -> str:
        files = [f for f in os.listdir('.') if f.startswith(name) and f.endswith('.json')]
        if not files:
            raise FileNotFoundError(f"No files found for name: {name}")

        latest_file = max(files, key=os.path.getmtime)  # Get the most recently modified file
        print(f"Latest JSON file: {latest_file}")
        return latest_file

    def fetch_and_parse(self, name: str, url: str, fetch=True, parse=True) -> List[Apartment]:
        if fetch:
            self.__save_raw_file__(name, url)

        source = self.__get_latest_json__(name)
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

        parsed = self.__get_latest_json__('parsed')
        with open(parsed, "r") as f:
            res: List[Apartment] = json.loads(f.read())
            return res