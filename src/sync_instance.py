from typing import List

from src.supa_client import SupaState
from src.y2_ingest_svc import Apartment, IngestedApartament

class SyncInstance():
    qname: str
    def __init__(self, qname):
        self.qname = qname

    def get_ingested(self, apt: Apartment) -> IngestedApartament:
        res = IngestedApartament(apt, self.qname)
        return res

    # def check_missing(self, apartaments: List[Apartment], state: List[SupaState]):
    #     activeDict = {apt['token'] for apt in apartaments}
    #     return [apt for apt in state if apt.id not in activeDict and apt.score is not None]

    def extended_print(self, apartaments: List[SupaState]):
        [print(f"     {apt.id}, with price: {apt.data['price']}, meters: {apt.data['squareMeter']}") for apt in apartaments]

    def sync(self, apartments, state) -> List[IngestedApartament]:
        ingested = [self.get_ingested(apt) for apt in apartments]
        return ingested