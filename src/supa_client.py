import dataclasses
import json
from dataclasses import dataclass
from typing import List, Union

import requests

from src.y2_ingest_svc import Apartment, IngestedApartament, EnhancedJSONEncoder


@dataclass
class SupaState():
    id: str
    query_name: str
    # created_at: str
    data: Apartment



@dataclass
class ApartamentQuery:
    id: str
    name: str
    query_string: str


class SupaClient:


    def __init__(self, queries_url: str, supabase_url: str, supabase_key: str):
        self.queries_url = queries_url
        self.apts_url = supabase_url
        self.token = supabase_key
        self.headers = {
            "apikey": self.token,
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }

    def get_state(self, qName: str) -> List[SupaState]:
        api_url = f"{self.apts_url}?select=id,query_name,data"
        params = {"query_name": f"eq.{qName}"}
        try:
            response = requests.get(api_url, headers=self.headers, params=params)
            response.raise_for_status()
            res = []
            for item in response.json():
                parsed = SupaState(**item)
                parsed.data = json.loads(item['data'])
                res.append(parsed)
            return res
        except requests.exceptions.RequestException as e:
            print(f"Error during GET request: {e}")
            return []

    def deactivate_id(self, id_value: str):
        api_url = f"{self.apts_url}?id=eq.{id_value}"
        payload = {"archived": "TRUE"}
        try:
            response = requests.patch(api_url, headers=self.headers, json=payload)
            response.raise_for_status()  # Raise HTTPError for bad responses
            return True
        except requests.exceptions.RequestException as e:
            print(f"Error during PATCH request: {e}")
            return False

    def delete(self, query_name: str):
        try:
            api_url = f"{self.apts_url}?query_name=eq.{query_name}"
            response = requests.delete(api_url, headers=self.headers)
            response.raise_for_status()
            return True
        except requests.exceptions.RequestException as e:
            print(f"Error during DELETE request: {e}")
            return False

    def ingest_values(self, apartments: List[IngestedApartament]):
        print(f"Ingesting {len(apartments)}")
        api_url = f"{self.apts_url}"
        payload = [
            {
                'id': apt.data['token'],
                'data': json.dumps(apt.data, cls=EnhancedJSONEncoder),
                'query_name': apt.query_name
            }
        for apt in apartments]

        upsert_headers = {**self.headers, **{"Prefer" : "resolution=merge-duplicates"}}
        try:
            response = requests.post(api_url, headers=upsert_headers, json=payload) # TODO: add query_name
            response.raise_for_status()  # Raise HTTPError for bad responses
            return True
        except requests.exceptions.RequestException as e:
            print(f"Error during PATCH request: {e}")
            return False



    def ingest_queries(self, queries: List[ApartamentQuery]):
        api_url = f"{self.queries_url}"
        payload = [dataclasses.asdict(x) for x in queries]
        headers = {**self.headers, **{"Prefer" : "resolution=merge-duplicates"}}
        try:
            response = requests.post(api_url, headers=headers, json=payload) # TODO: add query_name
            response.raise_for_status()  # Raise HTTPError for bad responses
            return True
        except requests.exceptions.RequestException as e:
            print(f"Error during PATCH request: {e}")
            return False
