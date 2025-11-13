from threading import Lock
import time
import pygame

from lib.sockets.client_socket import ClientSocket

from lib.sockets.sock_utils import NetworkId
from models.fighter import Fighter
from models.network_protocol import FighterUpdate, connect_request, fighter_update, receive_message, update_fighter

from view.display import Display

def _join_server():

    client_socket.write(connect_request())
    while (raw_message := client_socket.read()) is None:
        pass
    message = receive_message(raw_message)
    if isinstance(message, FighterUpdate):
        local_fighter.network_id = message.get_network_id()
        remote_fighter.network_id = message.get_network_id()
        update_fighter(local_fighter, message)
        update_fighter(remote_fighter, message)
    else:
        print(f"(client) dropping unexpected message: {message}")
    time.sleep(0.1)

def _dispatch_event(event: pygame.event.Event) -> bool:
    global running

    if event.type == pygame.QUIT:
        running = False
        return

    if event.type != pygame.KEYDOWN:
        return

    if event.key == pygame.K_LEFT:
        local_fighter.left()
    elif event.key == pygame.K_RIGHT:
        local_fighter.right()
    elif event.key == pygame.K_UP:
        local_fighter.forward()
    elif event.key == pygame.K_DOWN:
        local_fighter.backward()
    else:
        return False
    
    # moved, so update the server
    return True

def _network_sync():

    while raw_message := client_socket.read():

        message = receive_message(raw_message)

        if not isinstance(message, FighterUpdate):
            print(f"(client) dropping unexpected message {message!r}")

        with other_fighters_lock:
            other_fighter: Fighter = other_fighters.get(message.get_network_id(), None)
            if not other_fighter:
                other_fighter = Fighter()
                other_fighters[message.get_network_id()] = other_fighter
                display.add_fighter(other_fighter)
            elif other_fighter.network_id == message.get_network_id():
                # It's MEEEEE
                update_fighter(remote_fighter, message)
                update_fighter(local_fighter, message)
                continue

        update_fighter(other_fighter, message)

        display.draw()

#
# MAIN
#

client_socket = ClientSocket()
client_socket.start()

local_fighter  = Fighter()
remote_fighter = Fighter()

other_fighters_lock = Lock()
other_fighters = dict[NetworkId, Fighter]()

print("(client) joining session")

_join_server()

display = Display()
display.init()

running = True

print("(client) started")

while running:
    for event in pygame.event.get():
        if _dispatch_event(event):
            outgoing = fighter_update(local_fighter)
            print(f"Sending outgoing: {outgoing}")
            client_socket.write(outgoing)
        _network_sync()
    display.render()

print("(client) stopping")

client_socket.stop()
display.stop()

print("(client) stopped")
