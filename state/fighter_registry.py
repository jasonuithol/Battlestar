
from copy import copy
from lib.sockets.sock_utils import NetworkId

from .fighter    import Fighter
from .spawn_slot import SpawnSlot

class SpawnedFighter:
    def __init__(self, local_fighter: Fighter):
        self.local_fighter  = local_fighter
        self.copy_to_remote()

    def copy_to_remote(self):
        self.remote_fighter = copy(self.local_fighter)

class FighterRegistry:

    def __init__(self, spawn_slots: list[SpawnSlot]):

        self._available_spawn_slots = spawn_slots
        self._attached_spawn_slots = list[SpawnSlot]()

        self._registered_fighters    = dict[NetworkId, SpawnedFighter]()

    def spawn_fighter(self, network_id: NetworkId) -> SpawnedFighter:

        spawn_slot = self._obtain_spawn_slot()

        f = Fighter()
        f.color      = spawn_slot.color
        f.angle      = spawn_slot.angle
        f.coords     = spawn_slot.coords
        f.network_id = network_id
        
        spawned_fighter = SpawnedFighter(f)
        self._registered_fighters[network_id] = spawned_fighter

        return spawned_fighter

    def despawn_fighter(self, network_id: NetworkId):
        self._recycle_spawn_slot(network_id)
        del self._registered_fighters[network_id]

    def get_spawned_fighter(self, network_id: NetworkId) -> SpawnedFighter:
        return self._registered_fighters.get(network_id, None)

    def get_registered_fighters(self) -> list[SpawnedFighter]:
        return list(self._registered_fighters.values())

    def has_available_slots(self) -> bool:
        return len(self._available_spawn_slots) > 0

    def _obtain_spawn_slot(self) -> SpawnSlot:
        spawn_slot = self._available_spawn_slots.pop()
        self._attached_spawn_slots.append(spawn_slot)

    def _recycle_spawn_slot(self, network_id: NetworkId):
        pet_slot = self._get_attached_spawn_slot(network_id)
        self._attached_spawn_slots.remove(pet_slot)
        self._available_spawn_slots.append(pet_slot)

    def _get_attached_spawn_slot(self, network_id: NetworkId) -> SpawnSlot:
        # this is a bit cute but there's no reason it shouldn't work
        fighter_color = self._registered_fighters[network_id].local_fighter.color
        assoc_slots = [
            slot
            for slot in self._attached_spawn_slots
            if slot.color == fighter_color
        ]
        if len(assoc_slots) == 0:
            return None
        assert len(assoc_slots) < 2, "Somehow have multiple attached spawn slots with the same color"
        return assoc_slots[0]


