import gc
import time

from copy import copy

from state.state_bootstrapper import build_fighter_registry

from lib.sockets.sock_utils import NetworkId
from lib.sockets.server_socket import ServerSocket

import lib.network_protocols.battlestar_protocol

from lib.network_protocols.named_tuple_codec import MessageFormat, NamedTupleCodec
from lib.network_protocols.battlestar_protocol import AccelerateRequest, ConnectRequest, FighterUpdate, RotateRequest
from lib.network_protocols.battlestar_protocol_interfaces.server_protocol import ServerProtocol

class Server:

    def __init__(self):

        self.fighter_registry = build_fighter_registry()

        self.server_protocol = ServerProtocol()
        self.server_socket = ServerSocket(
            codec = NamedTupleCodec(lib.network_protocols.battlestar_protocol)
        )
        self.server_socket.start()

    def remove_dead_clients(self):

        # remove dead clients
        for dead_network_id in self.server_socket.dead_clients:

            # Free up the spawn slot
            self.fighter_registry.despawn_fighter(dead_network_id)

            # Remove the dead fighter from the "is dead" list - we're done killing it.
            self.server_socket.remove_dead_client(dead_network_id)

            print(f"(server) Removed fighter ({dead_network_id})")

    def handle_connect_request(self, network_id: NetworkId):

        if self.fighter_registry.has_available_slots():

            print(f"(server) Adding fighter to session")
            spawned_fighter = self.fighter_registry.spawn_fighter(network_id)

            print(f"(server) sending acceptance response")
            fighter_update = self.server_protocol.fighter_update(spawned_fighter.local_fighter)
            self.server_socket.write_to(network_id, fighter_update)

        else:
            print(f"(server) sending rejection response")
            self.server_socket.write_to(network_id, self.server_protocol.connect_reject("Server full"))

        gc.collect()

    def calculate_and_broadcast_updates(self):

        for spawned_fighter in self.fighter_registry.get_registered_fighters():
            spawned_fighter.local_fighter.calculate()
            if spawned_fighter.local_fighter.state_differs(spawned_fighter.remote_fighter):
                self.server_socket.broadcast(self.server_protocol.fighter_update(spawned_fighter.local_fighter))
                spawned_fighter.remote_fighter = copy(spawned_fighter.local_fighter)
            time.sleep(0.001)

    '''
    def handle_fighter_update(self, network_id: NetworkId, message: FighterUpdate):

        if message.get_network_id() != network_id:
            print("(server) someone is impersonating someone else, dropping message")
            return

        fighter = self.fighter_registry.find_attached_fighter(network_id)    

        if not fighter:
            print(f"(server) received update for unattached fighter: {network_id}")
            return

        #
        # TODO: Check that the client is allowed to do the things they say they do
        #
        print("(server) received fighter update")
        ???
        self.server_protocol.update_fighter(fighter, message)

        gc.collect()
    '''

    def handle_rotate_request(self, network_id: NetworkId, rotate_request: RotateRequest):
        spawned_fighter = self.fighter_registry.get_spawned_fighter(network_id)
        self.server_protocol.update_fighter_rotation(spawned_fighter.local_fighter, rotate_request)
        spawned_fighter.remote_fighter = copy(spawned_fighter.local_fighter)        

    def handle_accelerate_request(self, network_id: NetworkId, accelerate_request: AccelerateRequest):
        spawned_fighter = self.fighter_registry.get_spawned_fighter(network_id)
        self.server_protocol.update_fighter_acceleration(spawned_fighter.local_fighter, accelerate_request)        
        spawned_fighter.remote_fighter = copy(spawned_fighter.local_fighter)        

    def dispatch_message(self, server_message: MessageFormat):

        network_id, message = server_message
        print(f"(server) received message {message} from {network_id}")

        if message is None:
            print(f"(server) Dropping null message from {network_id}")
            return
        
#        assert network_id == message.get_network_id(), "Got corrupted network_id"

        if isinstance(message, ConnectRequest):
            self.handle_connect_request(network_id)

        elif isinstance(message, RotateRequest):
            self.handle_rotate_request(network_id, message)

        elif isinstance(message, AccelerateRequest):
            self.handle_accelerate_request(network_id, message)

            '''
        elif isinstance(message, FighterUpdate):
            self.handle_fighter_update(network_id, message)
            '''

        else:
            print(f"(server) received unknown message {message} from {network_id}")      


    #
    # MAIN LOOP
    #

    def launch(self):

        while True:

            self.remove_dead_clients()

            incoming_messages = self.server_socket.readall()

            if len(incoming_messages) > 0:
                print(f"(server) received {len(incoming_messages)} incoming messages")

            for server_message in incoming_messages:
                self.dispatch_message(server_message)

            self.calculate_and_broadcast_updates()
            time.sleep(0.01)

#
# MAIN
#
server = Server()
server.launch()

