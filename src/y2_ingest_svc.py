import dataclasses
import datetime
import json
import os
import re
import time
from dataclasses import dataclass
from typing import List, Union

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

@dataclass()
class ImageScore:
    file: str
    room_type: dict[str, float]
    occupancy: dict[Union["empty", "full"], float] # TODO: fix typing

@dataclass()
class VectoredApartment(Apartment):
    scoredImages: List[ImageScore]

@dataclass
class ScoredApartment(VectoredApartment):
    guiScore: float


@dataclass
class IngestedApartment():
    data: ScoredApartment
    queryName: str

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
            print("Exception parsing apartament!")
            return None

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


    def fetch_and_parse_legacy(self, name: str, url: str, fetch=True) -> List[Apartment]: # TODO: should be reused by common code (?)
        if fetch:
            self.__save_raw_file__(name, url)

        source = self.__get_latest_json__(name)
        with open(source, "r") as f:
            data = f.read()
            svc = Y2IngestService(data)
            data = svc.transform_data()
            print(json.dumps(data, cls=EnhancedJSONEncoder))
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"parsed_{name}_{timestamp}.json"
            with open(filename, "w", encoding="utf-8") as f:
                f.write(json.dumps(data, cls=EnhancedJSONEncoder))
                print(f"Parsed JSON saved as: {filename}")

        parsed = self.__get_latest_json__('parsed')
        with open(parsed, "r") as f:
            res: List[Apartment] = [Apartment(**apt) for apt in json.loads(f.read())]
            return res


    def fetch_and_parse(self, name: str, url: str, fetch=True) -> None:
        if fetch:
            self.__save_raw_file__(name, url)

        source = self.__get_latest_json__(name)
        with open(source, "r") as f:
            data = f.read()
            svc = Y2IngestService(data)
            data = svc.transform_data()
            print(json.dumps(data, cls=EnhancedJSONEncoder))
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"parsed_{name}_{timestamp}.json"
            with open(filename, "w", encoding="utf-8") as f:
                f.write(json.dumps(data, cls=EnhancedJSONEncoder))
                print(f"Parsed JSON saved as: {filename}")


    def load_vectorised(self, name: str) -> List[VectoredApartment]:
        parsed = self.__get_latest_json__('parsed_vectorised')
        with open(parsed, "r") as f:
            res: List[VectoredApartment] = [VectoredApartment(**apt) for apt in json.loads(f.read())]
            return res