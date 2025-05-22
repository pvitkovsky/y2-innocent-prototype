from typing import List

from src.supa_client import SupaState
from src.y2_ingest_svc import Apartment, IngestedApartament

class SyncInstance():
    qname: str
    def __init__(self, qname):
        self.qname = qname

    def get_ingested(self, apt: Apartment, score: int) -> IngestedApartament:
        res = IngestedApartament(apt['coords'], apt['price'], apt['token'], apt['squareMeter'], apt['pricePerMeter'],
                                 apt['roomsCount'], apt['metadata'], self.qname, score)
        return res

    def remove_archived(self, apartaments: List[Apartment], state: List[SupaState]) -> List[IngestedApartament]:
        archivedDict = {apt.id for apt in state if apt.archived}
        scoreDict = {apt.id : apt.score for apt in state if apt.score is not None}
        return [self.get_ingested(apt, scoreDict.get(apt['token'])) for apt in apartaments if apt['token'] not in archivedDict]

    def check_missing(self, apartaments: List[Apartment], state: List[SupaState]):
        activeDict = {apt['token'] for apt in apartaments}
        return [apt.id for apt in state if apt.id not in activeDict]

    # def printIds(self, apartaments: List[Apartment]):
    #     print(f"Total {len(apartaments)} objects")
    #     [print(f"{apt['token']}") for apt in apartaments]

    def sync(self, apartments, state) -> List[IngestedApartament]:
        filtered = self.remove_archived(apartments, state)
        return filtered