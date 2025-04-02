import json
from dataclasses import dataclass
from typing import NamedTuple, List, Any


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

class Y2IngestService:
    def __init__(self, source_json: str):
        self.source_json = source_json

    def transform_data(self) -> List[Apartment]:
        try:
            data = json.loads(self.source_json)
            apartments = [self.process(apt) for apt in data['data']['markers']]
            
            sorted_apartments = sorted(apartments, key=lambda x: x.pricePerMeter)
            return sorted_apartments
        except json.JSONDecodeError:
            raise "'Error: Invalid JSON input'"

    def process(self, apt):
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
                coverImage=apt['metaData']['coverImage'],
                images=apt['metaData']['images'],
                squareMeterBuild=apt['metaData']['squareMeterBuild'] if apt['metaData'].get(
                'squareMeterBuild') else 1
            )
        )

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