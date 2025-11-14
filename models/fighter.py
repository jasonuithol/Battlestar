import datetime
import math

import pygame
from lib.sockets.sock_utils import NetworkId

ANGULAR_SPEED = 0.1
ACCELERATION_MAGNITUDE = 3.0

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
        seconds_elapsed = (new_calculation_time - self.last_calculated).total_seconds()

        angle_degrees = math.degrees(self.angle)

        v2_offset = pygame.math.Vector2()
        v2_offset.from_polar((self.speed * seconds_elapsed, angle_degrees))

        self.coords = (
            int(self.coords[0] + v2_offset.x),
            int(self.coords[1] + v2_offset.y)
        )

        self.last_calculated = new_calculation_time
