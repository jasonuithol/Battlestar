from typing import NamedTuple
from lib.sockets.sock_utils import NetworkId

from state.fighter import FighterColor

def _network_id(self) -> NetworkId:
    return self.network_id_host, self.network_id_port

def _color(self) -> FighterColor:
    return self.color_r, self.color_g, self.color_b

def _coords(self) -> tuple[int,int]:
    return self.coord_x, self.coord_y

def _velocity(self) -> tuple[float,float]:
    return self.velocity_x, self.velocity_y

class ConnectRequest(NamedTuple):
    pass

class ConnectReject(NamedTuple):
    reason: str

class ConnectError(NamedTuple):
    reason: str

class FighterUpdate(NamedTuple):
    network_id_host: str
    network_id_port: int

    color_r: int
    color_g: int
    color_b: int

    coord_x: int
    coord_y: int

    velocity_x: float
    velocity_y: float

    angle:   float
    radius:  float
    thiccness: int

    get_network_id = _network_id
    get_color      = _color
    get_coords     = _coords
    get_velocity   = _velocity

class RotateRequest(NamedTuple):
    network_id_host: str
    network_id_port: int

    angle_delta: float

    get_network_id = _network_id

class AccelerateRequest(NamedTuple):
    network_id_host: str
    network_id_port: int

    velocity_delta: tuple[float, float]

    get_network_id = _network_id


