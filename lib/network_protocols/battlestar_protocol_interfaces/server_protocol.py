from lib.network_protocols.battlestar_protocol import AccelerateRequest, ConnectError, ConnectReject, FighterUpdate, RotateRequest
from state.fighter import Fighter

class ServerProtocol:

    def connect_reject(self, reason: str) -> ConnectReject:
        return ConnectReject(reason)

    def connect_error(self, reason: str) -> ConnectError:
        return ConnectError(reason)

    def fighter_update(self, fighter: Fighter) -> FighterUpdate:

        assert fighter.network_id, "Cannot send a fighter_update without a network_id"
        assert isinstance(fighter.network_id, tuple), f"network_id got unexpected value {fighter.network_id!r}"

        host, port = fighter.network_id
        r, g, b    = fighter.color
        x, y       = fighter.coords
        vx, vy     = fighter.velocity

        message = FighterUpdate(
            network_id_host = host,
            network_id_port = port,

            color_r = r,
            color_g = g,
            color_b = b,

            coord_x = x,
            coord_y = y,

            velocity_x = vx,
            velocity_y = vy,

            angle      = fighter.angle,
            radius     = fighter.radius,
            thiccness  = fighter.thiccness
        )

        return message
    
    def update_fighter_rotation(self, fighter: Fighter, rotate_request: RotateRequest):
        fighter.angle += rotate_request.angle_delta

    def update_fighter_acceleration(self, fighter: Fighter, accelerate_request: AccelerateRequest):
        fighter.velocity += accelerate_request.velocity_delta
