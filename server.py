import time

from threading import Lock

from lib.sockets.server_socket import ServerSocket
from lib.sockets.sock_utils import NetworkId

from models.fighter import Fighter
from models.network_protocol import ConnectRequest, FighterUpdate, connect_reject, fighter_update, receive_message, update_fighter

server_socket = ServerSocket()
server_socket.start()

#connected_fighters_lock = Lock()
connected_fighters = dict[NetworkId, Fighter]()

BLUE   = (000, 000, 255)
RED    = (255, 000, 000)
YELLOW = (255, 255, 000)
PINK   = (255, 192, 203)

spawn_slots = [
    (BLUE,   (250, 250)),
    (RED,    (750, 750)),
    (YELLOW, (750, 250)),
    (PINK,   (250, 750)),
]

while True:

    # read all incoming messages
    messages = server_socket.readall()

    for server_message in messages:

        network_id, raw_message = server_message
        
        print(f"(server) received message {server_message} from {network_id}")

        if raw_message is None or len(raw_message) == 0:
            print(f"Dropping null message from {network_id}")
            continue

        message = receive_message(raw_message)

        if isinstance(message, ConnectRequest):

            num_clients = len(connected_fighters)
            if num_clients == len(spawn_slots):
                server_socket.write_to(network_id, connect_reject("Server full"))
            else:                
                print(f"(server) Adding fighter {num_clients + 1} to session")
                connected_fighter = Fighter()
                color, coords = spawn_slots[num_clients]

                connected_fighter.network_id = network_id
                connected_fighter.color      = color
                connected_fighter.coords     = coords

                server_socket.write_to(network_id, fighter_update(connected_fighter))
                connected_fighters[network_id] = connected_fighter

        elif isinstance(message, FighterUpdate):
            
            if message.get_network_id() != network_id:
                print("(server) someone is impersonating someone else, dropping message")
                continue

            elif message.get_network_id() in connected_fighters.keys():

                connected_fighter = connected_fighters[network_id]

                #
                # TODO: Check that the client is allowed to do the things they say they do
                #

                update_fighter(connected_fighter, message)

                server_socket.broadcast(fighter_update(connected_fighter))

    time.sleep(0.001)
