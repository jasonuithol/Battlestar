import math
from .fighter_registry import FighterRegistry
from .spawn_slot       import SpawnSlot

def build_fighter_registry() -> FighterRegistry:

    #
    # NOTE: All values in the registry are in screen co-ordinates i.e. the Y-axis is flipped so that top-left is (0,0)
    #

    BLUE   = (000, 000, 255)
    RED    = (255, 000, 000)
    YELLOW = (255, 255, 000)
    PINK   = (255, 192, 203)

    TOP_LEFT     = (250, 250)
    BOTTOM_RIGHT = (750, 750)
    TOP_RIGHT    = (750, 250)
    BOTTOM_LEFT  = (250, 750)

    #
    # Make the angles negative to allow for the flipping of the Y axis when converting from pure math co-ordinates to screen-coordinates.
    # 
    full_circle = math.pi * -2

    o_clock     = full_circle / 12

    FROM_TOP_LEFT_TO_CENTRE     =  4 * o_clock
    FROM_BOTTOM_RIGHT_TO_CENTRE = 10 * o_clock
    FROM_TOP_RIGHT_TO_CENTRE    =  8 * o_clock
    FROM_BOTTOM_LEFT_TO_CENTRE  =  2 * o_clock

    fighter_registry = FighterRegistry(
        spawn_slots = [
            SpawnSlot(color = BLUE,   coords = TOP_LEFT    , angle = FROM_TOP_LEFT_TO_CENTRE    ),
            SpawnSlot(color = RED,    coords = BOTTOM_RIGHT, angle = FROM_BOTTOM_RIGHT_TO_CENTRE),
            SpawnSlot(color = YELLOW, coords = TOP_RIGHT   , angle = FROM_TOP_RIGHT_TO_CENTRE   ),
            SpawnSlot(color = PINK,   coords = BOTTOM_LEFT , angle = FROM_BOTTOM_LEFT_TO_CENTRE )
        ]
    )

    return fighter_registry



