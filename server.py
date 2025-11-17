import gc
import time

from state.state_bootstrapper import build_fighter_registry

from lib.sockets.sock_utils import NetworkId
from lib.sockets.server_socket import ServerSocket

import lib.network_protocols.battlestar_protocol

from lib.network_protocols.named_tuple_codec import NamedTupleCodec
from lib.network_protocols.battlestar_protocol import ConnectRequest, FighterUpdate, connect_reject, fighter_update, update_fighter

class Server:

    def __init__(self):

        self.fighter_registry = build_fighter_registry()

        self.server_socket = ServerSocket(
            codec = NamedTupleCodec(lib.network_protocols.battlestar_protocol)
        )
        self.server_socket.start()

    def remove_dead_clients(self):

        # remove dead clients
        for dead_network_id in self.server_socket.dead_clients:

            spawn_slot = self.fighter_registry.find_attached_slot(dead_network_id)

            # Free up the spawn slot
            spawn_slot.detach()

            # Remove the dead fighter from the "is dead" list - we're done killing it.
            self.server_socket.remove_dead_client(dead_network_id)

            print(f"(server) Removed fighter ({dead_network_id})")

    def handle_connect_request(self, network_id: NetworkId):

        available_slot = self.fighter_registry.get_available_slot()
        if available_slot:

            print(f"(server) Adding fighter to session")
            fighter = available_slot.attach(network_id)


            print(f"(server) sending acceptance response")
            self.server_socket.write_to(network_id, fighter_update(fighter))

        else:
            print(f"(server) sending rejection response")
            self.server_socket.write_to(network_id, connect_reject("Server full"))

        gc.collect()

    def calculate_and_broadcast_updates(self):

        for fighter in self.fighter_registry.get_attached_fighters():
            fighter.calculate()
            self.server_socket.broadcast(fighter_update(fighter))
            time.sleep(0.001)

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
        update_fighter(fighter, message)

        gc.collect()

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

                network_id, message = server_message
                print(f"(server) received message {message} from {network_id}")
                if message is None:
                    print(f"(server) Dropping null message from {network_id}")
                    continue

                if isinstance(message, ConnectRequest):
                    self.handle_connect_request(network_id)

                elif isinstance(message, FighterUpdate):
                    self.handle_fighter_update(network_id, message)

                else:
                    print(f"(server) received unknown message {message} from {network_id}")


            self.calculate_and_broadcast_updates()
            time.sleep(0.01)

#
# MAIN
#
server = Server()
server.launch()

