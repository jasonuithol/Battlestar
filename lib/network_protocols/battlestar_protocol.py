from typing import NamedTuple
from lib.sockets.sock_utils import NetworkId

from state.fighter import Fighter, FighterColor

def _network_id(self) -> NetworkId:
    return self.network_id_host, self.network_id_port

def _color(self) -> FighterColor:
    return self.color_r, self.color_g, self.color_b

def _coords(self) -> tuple[int,int]:
    return self.coord_x, self.coord_y

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

    angle:   float
    radius:  float
    thiccness: int

    get_network_id = _network_id
    get_color = _color
    get_coords = _coords

class RotateRequest(NamedTuple):
    network_id_host: str
    network_id_port: int

    angle_delta: float

    get_network_id = _network_id

class AccelerateRequest(NamedTuple):
    network_id_host: str
    network_id_port: int

    velocity_delta: float

    get_network_id = _network_id

def connect_request() -> ConnectRequest:
    return ConnectRequest()

def connect_reject(reason: str) -> ConnectReject:
    return ConnectReject(reason)

def connect_error(reason: str) -> ConnectError:
    return connect_error(reason)

def fighter_update(fighter: Fighter) -> FighterUpdate:

    assert fighter.network_id, "Cannot send a fighter_update without a network_id"
    assert isinstance(fighter.network_id, tuple), f"network_id got unexpected value {fighter.network_id!r}"

    host, port = fighter.network_id
    r, g, b    = fighter.color
    x, y       = fighter.coords

    message = FighterUpdate(
        network_id_host = host,
        network_id_port = port,

        color_r = r,
        color_g = g,
        color_b = b,

        coord_x = x,
        coord_y = y,

        angle      = fighter.angle,
        radius     = fighter.radius,
        thiccness  = fighter.thiccness
    )

    return message

def create_fighter(fighter_update: FighterUpdate):
    fighter = Fighter()
    fighter.network_id = fighter_update.get_network_id()
    update_fighter(fighter, fighter_update)
    return fighter

def update_fighter(fighter: Fighter, fighter_update: FighterUpdate):
    fighter.coords    = fighter_update.get_coords()
    fighter.color     = fighter_update.get_color()
    fighter.angle     = fighter_update.angle
    fighter.radius    = fighter_update.radius
    fighter.thiccness = fighter_update.thiccness

def rotate(network_id: NetworkId, angle_delta: float) -> RotateRequest:

    host, port = network_id

    message = RotateRequest(
        network_id_host = host,
        network_id_port = port,
        angle_delta     = angle_delta
    )

    return message

def accelerate(network_id: NetworkId, velocity_delta: float) -> AccelerateRequest:

    host, port = network_id

    message = AccelerateRequest(
        network_id_host = host,
        network_id_port = port,
        velocity_delta  = velocity_delta
    )

    return message

