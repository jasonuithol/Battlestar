import datetime

import pygame
from lib.sockets.sock_utils import NetworkId

ANGULAR_SPEED = 0.2
ACCELERATION_MAGNITUDE = 0.2

FighterColor = tuple[int, int ,int]

class Fighter:
    def __init__(self):
        self.network_id: NetworkId = None

        self.coords     = (0, 0)
        self.speed      = 0.0
        self.angle      = 0.0

        self.color: FighterColor = None
        self.radius: float       = 50.0
        self.thiccness: int      = 3

        self.last_calculated = datetime.datetime.now()

        __slots__ = ()
    
    def left(self):
        self.angle -= ANGULAR_SPEED
    def right(self):
        self.angle += ANGULAR_SPEED
    def forward(self):
        self.speed += ACCELERATION_MAGNITUDE
    def backward(self):
        self.speed -= ACCELERATION_MAGNITUDE

    def calculate(self):
        new_calculation_time = datetime.datetime.now()
        seconds_elapsed = (self.last_calculated - new_calculation_time).total_seconds()

        v2_offset = pygame.math.Vector2()
        v2_offset.from_polar((self.speed * seconds_elapsed, self.angle))

        v2_coord = pygame.math.Vector2(self.coords)
        v2_coord += v2_offset

        self.coords = int(v2_coord.x), int(v2_coord.y)

        self.last_calculated = new_calculation_time
