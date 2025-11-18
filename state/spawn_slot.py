
from typing import NamedTuple
from state.fighter import FighterColor

class SpawnSlot(NamedTuple):

    color:  FighterColor
    coords: tuple[int,int]
    angle:  float
