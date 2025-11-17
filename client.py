import gc
import time
import pygame

from state.fighter import Fighter

from lib.sockets.client_socket import ClientSocket
from lib.sockets.sock_utils import NetworkId

import lib.network_protocols.battlestar_protocol

from lib.network_protocols.named_tuple_codec import MessageFormat, NamedTupleCodec
from lib.network_protocols.battlestar_protocol import FighterUpdate, connect_request, create_fighter, fighter_update, update_fighter

from view.display import Display

class Client:

    def __init__(self):

        self.client_socket = ClientSocket(codec = NamedTupleCodec(lib.network_protocols.battlestar_protocol))

        self.local_fighter  = Fighter()
        self.remote_fighter = Fighter()

        self.other_fighters = dict[NetworkId, Fighter]()        

        self.display = Display()

    def launch(self):

        self.display.init()

        self.client_socket.start()

        leftover_messages = self._join_server()

        pygame.key.set_repeat(50, 50) # delay, repeat (milliseconds)
        self.running = True

        # finished initialising, tidy up.
        gc.collect()

        self._main_loop(leftover_messages)
        self.stop()

        print("(client) stopped")

    def stop(self):

        print("(client) stopping")

        self.client_socket.stop()
        self.display.stop()

    def _join_server(self) -> list[MessageFormat]:

        print("(client) joining session")

        self.client_socket.write(connect_request())

        print("(client) waiting for response from server")

        connected = False
        leftover_messages = list[MessageFormat]()

        while not connected:

            for message in self.client_socket.read():

                if self.client_socket.quit_received():
                    exit()

                if isinstance(message, FighterUpdate):
                    self.local_fighter  = create_fighter(message)
                    self.remote_fighter = create_fighter(message)

                    self.display.add_fighter(self.local_fighter)
                    connected = True
                    print(f"(client) successfully joined server as: {message.get_network_id()} ")
                    break

                else:
                    print(f"(client) delaying processing of unexpected message: {message}")
                    leftover_messages.append(message)

            time.sleep(0.1)

        return leftover_messages

    def _main_loop(self, leftover_messages: list[MessageFormat]):

        print(f"(client) started with {len(leftover_messages)} leftover messages")

        if self.client_socket.quit_received():
            print("(client) client socket received quit signal")
            exit()            

        self._network_sync(leftover_messages)

        self.display.draw()

        while self.running:
            for event in pygame.event.get():
                if self._dispatch_event(event):
                    outgoing = fighter_update(self.local_fighter)
                    print(f"(client) Sending outgoing: {outgoing}")
                    self.client_socket.write(outgoing)

            self._network_sync(self.client_socket.read())

            for fighter in self.other_fighters.values():
                fighter.calculate()

            self.local_fighter.calculate()

            self.display.draw()
            self.display.render()

    def _dispatch_event(self, event: pygame.event.Event) -> bool:

        if event.type == pygame.QUIT:
            self.running = False
            return

        if event.type != pygame.KEYDOWN:
            return

        if event.key == pygame.K_ESCAPE:
            self.running = False
            return

        if event.key == pygame.K_LEFT:
            self.local_fighter.left()
        elif event.key == pygame.K_RIGHT:
            self.local_fighter.right()
        elif event.key == pygame.K_UP:
            self.local_fighter.forward()
        elif event.key == pygame.K_DOWN:
            self.local_fighter.backward()
        else:
            return False
        
        # moved, so update the server
        return True

    def _network_sync(self, messages: list[MessageFormat]):

        for message in messages:

            if not isinstance(message, FighterUpdate):
                print(f"(client) dropping unexpected message {message!r}")
                continue

            print(f"(client) received message: {message!r}")

            assert message.get_network_id() is not None, "Cannot process a message without a network_id"

            if message.get_network_id() == self.local_fighter.network_id:
                # It's MEEEEE
                update_fighter(self.remote_fighter, message)
                self.local_fighter.coords = self.remote_fighter.coords
                print(f"(client) received remote update on self: {message!r}")
                continue

            other_fighter: Fighter = self.other_fighters.get(message.get_network_id(), None)

            if other_fighter:
                print(f"(client) received remote update on other player: {message!r}")
                update_fighter(other_fighter, message)

            else:
                other_fighter = create_fighter(message)
                self.display.add_fighter(other_fighter)
                print(f"(client) another player joined the server: {other_fighter.network_id}")

                self.other_fighters[other_fighter.network_id] = other_fighter



#
# MAIN
#

client = Client()
client.launch()
