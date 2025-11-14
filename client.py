import gc
from threading import Lock
import time
import pygame

from lib.sockets.client_socket import ClientSocket

from lib.sockets.sock_utils import NetworkId
from models.fighter import Fighter
from models.network_protocol import FighterUpdate, connect_request, create_fighter, fighter_update, receive_message, update_fighter

from view.display import Display

class Client:

    def __init__(self):

        self.client_socket = ClientSocket()

        self.local_fighter  = Fighter()
        self.remote_fighter = Fighter()

        self.other_fighters_lock = Lock()
        self.other_fighters = dict[NetworkId, Fighter]()        

        self.display = Display()

    def launch(self):

        self.display.init()

        self.client_socket.start()

        print("(client) joining session")

        self._join_server()

        pygame.key.set_repeat(300, 50)  # Start repeating after 300ms, repeat every 50ms
        self.running = True

        # finished initialising, tidy up.
        gc.collect()

        self._main_loop()
        self.stop()

        print("(client) stopped")

    def stop(self):

        print("(client) stopping")

        self.client_socket.stop()
        self.display.stop()

    def _join_server(self):

        self.client_socket.write(connect_request())
        while (raw_message := self.client_socket.read()) is None:
            pass

        message = receive_message(raw_message)

        if isinstance(message, FighterUpdate):
            self.local_fighter = create_fighter(message)
            self.remote_fighter = create_fighter(message)

            self.display.add_fighter(self.local_fighter)

            print(f"(client) successfully joined server as: {message.get_network_id()} ")

        else:
            print(f"(client) dropping unexpected message: {message}")

        time.sleep(0.1)

    def _main_loop(self):

        print("(client) started")

        self.display.draw()

        while self.running:
            for event in pygame.event.get():
                if self._dispatch_event(event):
                    outgoing = fighter_update(self.local_fighter)
                    print(f"(client) Sending outgoing: {outgoing}")
                    self.client_socket.write(outgoing)
                    self.display.draw()

            if self._network_sync():
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

    def _network_sync(self) -> bool:

        updated_state = False

        while raw_message := self.client_socket.read():

            message = receive_message(raw_message)

            if not isinstance(message, FighterUpdate):
                print(f"(client) dropping unexpected message {message!r}")
                continue

            print(f"(client) received message: {message!r}")

            if message.get_network_id() == self.local_fighter.network_id:
                # It's MEEEEE
                update_fighter(self.remote_fighter, message)
                update_fighter(self.local_fighter, message)
                print(f"(client) received remote update on self: {message!r}")
                updated_state = True
                continue

            with self.other_fighters_lock:
                other_fighter: Fighter = self.other_fighters.get(message.get_network_id(), None)

            if other_fighter:
                print(f"(client) received remote update on other player: {message!r}")
                update_fighter(other_fighter, message)

            else:
                other_fighter = create_fighter(message)
                self.display.add_fighter(other_fighter)
                print(f"(client) another player joined the server: {other_fighter.network_id}")

                with self.other_fighters_lock:
                    self.other_fighters[other_fighter.network_id] = other_fighter

            updated_state = True

        return updated_state

#
# MAIN
#

client = Client()
client.launch()
