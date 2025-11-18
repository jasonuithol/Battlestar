import datetime
from lib.sockets.sock_utils import NetworkId

ANGULAR_SPEED = 0.1
ACCELERATION_MAGNITUDE = 3.0
IMPULSE_DURATION: float = 50.0 / 1000

FighterColor = tuple[int, int ,int]

class Fighter:
    
    def __init__(self):

        self.network_id:  NetworkId    = None
        self.color:       FighterColor = None

        self.coords: tuple[int, int] = None
        self.angle:  float           = None

        self.velocity:  tuple[float, float] = (0.0, 0.0)
        self.radius:    float = 50.0
        self.thiccness: int   = 3

        self.last_calculated = datetime.datetime.now()

        __slots__ = ()

    def state_differs(self, remote: Fighter) -> bool:
        return (
            self.coords   != remote.coords
            or
            self.angle    != remote.angle
            or
            self.velocity != remote.velocity
        )

    '''
    def left(self):
        self.angle -= ANGULAR_SPEED
        self.angle %= math.pi * 2
    def right(self):
        self.angle += ANGULAR_SPEED
        self.angle %= math.pi * 2
    def forward(self):
        self._apply_acceleration(+ACCELERATION_MAGNITUDE)
    def backward(self):
        self._apply_acceleration(-ACCELERATION_MAGNITUDE)

    def _apply_acceleration(self, acceleration_magnitude: float):
        angle_degrees_math = math.degrees(self.angle)

        impulse = pygame.math.Vector2()
        impulse.from_polar((acceleration_magnitude * IMPULSE_DURATION, angle_degrees_math))

        self.velocity = (
            self.velocity[0] + impulse[0],
            self.velocity[1] + impulse[1],
        )

    '''
    def calculate(self):
        new_calculation_time = datetime.datetime.now()
        seconds_elapsed = (new_calculation_time - self.last_calculated).total_seconds()

        self.coords = (
            int(self.coords[0] + (self.velocity[0] * seconds_elapsed)),
            int(self.coords[1] + (self.velocity[1] * seconds_elapsed))
        )

        self.last_calculated = new_calculation_time
