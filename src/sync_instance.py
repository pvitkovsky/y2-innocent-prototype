from typing import List

from src.supa_client import SupaState
from src.y2_ingest_svc import Apartment


class SyncInstance():
    qname: str
    def __init__(self, qname):
        self.qname = qname

    def remove_archived(self, apartaments: List[Apartment], state: List[SupaState]):
        archivedDict = {apt.id for apt in state if apt.archived}
        return [apt for apt in apartaments if apt['token'] not in archivedDict]

    def check_missing(self, apartaments: List[Apartment], state: List[SupaState]):
        activeDict = {apt['token'] for apt in apartaments}
        return [apt.id for apt in state if apt.id not in activeDict]

    def printIds(self, apartaments: List[Apartment]):
        print(f"Total {len(apartaments)} objects")
        [print(f"{apt['token']}") for apt in apartaments]

    def sync(self, apartments, state):
        filtered = self.remove_archived(apartments, state)
        missing = self.check_missing(apartments, state)
        print(f"Syncing apartaments for {self.qname}")
        self.printIds(filtered)
        print(missing)
        return filtered