
from lib.sockets.sock_utils import NetworkId
from state.fighter import Fighter, FighterColor

class SpawnSlot:

    def __init__(self, color: FighterColor, coords: tuple[int,int], angle: float):

        self.color  = color
        self.coords = coords
        self.angle  = angle

        self.fighter: Fighter = None

    def attach(self, network_id: NetworkId) -> Fighter:
        f = Fighter()
        f.network_id = network_id
        f.color      = self.color
        f.coords     = self.coords
        f.angle      = self.angle

        self.fighter = f
        return f

    def detach(self):
        self.fighter = None
