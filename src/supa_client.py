import json
from dataclasses import dataclass

import requests

@dataclass
class SupaState():
    id: str
    archived: bool

class SupaClient:


    def __init__(self, supabase_url: str, supabase_key: str):
        self.url = supabase_url
        self.token = supabase_key
        self.headers = {
            "apikey": self.token,
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }

    def get_state(self, qName: str):
        api_url = f"{self.url}?select=id,archived"
        params = {"query_name": f"eq.{qName}"}
        try:
            response = requests.get(api_url, headers=self.headers, params=params)
            response.raise_for_status()
            return [SupaState(**item) for item in response.json()]
        except requests.exceptions.RequestException as e:
            print(f"Error during GET request: {e}")
            return None

    def deactivate_id(self, id_value: str):
        api_url = f"{self.url}?id=eq.{id_value}"
        payload = {"archived": "TRUE"}
        try:
            response = requests.patch(api_url, headers=self.headers, json=payload)
            response.raise_for_status()  # Raise HTTPError for bad responses
            return True
        except requests.exceptions.RequestException as e:
            print(f"Error during PATCH request: {e}")
            return False

    # TODO: post;
