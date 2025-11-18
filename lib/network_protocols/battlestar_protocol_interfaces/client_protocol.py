
import math

import pygame
from lib.network_protocols.battlestar_protocol import AccelerateRequest, ConnectRequest, FighterUpdate, RotateRequest
from lib.sockets.sock_utils import NetworkId
from state.fighter import IMPULSE_DURATION, Fighter

class ClientProtocol:

    def connect_request(self) -> ConnectRequest:
        return ConnectRequest()

    def create_fighter(self, fighter_update: FighterUpdate):
        fighter = Fighter()
        fighter.network_id = fighter_update.get_network_id()
        self.update_fighter(fighter, fighter_update)
        return fighter

    def update_fighter(self, fighter: Fighter, fighter_update: FighterUpdate):

        fighter.coords    = fighter_update.get_coords()
        fighter.velocity  = fighter_update.get_velocity()
        fighter.color     = fighter_update.get_color()
        fighter.angle     = fighter_update.angle
        fighter.radius    = fighter_update.radius
        fighter.thiccness = fighter_update.thiccness

    def rotate(self, network_id: NetworkId, angle_delta: float) -> RotateRequest:

        host, port = network_id

        message = RotateRequest(
            network_id_host = host,
            network_id_port = port,
            angle_delta     = angle_delta
        )

        return message

    def accelerate(self, network_id: NetworkId, fighter: Fighter, acceleration_magnitude: float) -> AccelerateRequest:

        host, port = network_id
        angle_degrees_math = math.degrees(fighter.angle)

        impulse = pygame.math.Vector2()
        impulse.from_polar((acceleration_magnitude * IMPULSE_DURATION, angle_degrees_math))

        velocity_delta = (
            impulse[0],
            impulse[1],
        )

        message = AccelerateRequest(
            network_id_host = host,
            network_id_port = port,
            velocity_delta  = velocity_delta
        )

        return message