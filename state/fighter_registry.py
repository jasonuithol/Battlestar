
from lib.sockets.sock_utils import NetworkId

from .fighter import Fighter
from .spawn_slot import SpawnSlot

class FighterRegistry:

    def __init__(self, spawn_slots: list[SpawnSlot]):

        self._spawn_slots = spawn_slots

    def get_available_slot(self) -> SpawnSlot:
        for s in self._spawn_slots:
            if not s.fighter:
                return s
        return None

    def find_attached_slot(self, network_id: NetworkId) -> SpawnSlot:
        for s in self._spawn_slots:
            if s.fighter and s.fighter.network_id == network_id:
                return s
        return None

    def find_attached_fighter(self, network_id: NetworkId) -> Fighter:
        slot = self.find_attached_slot(network_id)
        if slot:
            return slot.fighter
        return None

    def get_attached_fighters(self) -> set[Fighter]:
        return {
            slot.fighter
            for slot in self._spawn_slots
            if slot.fighter
        }

