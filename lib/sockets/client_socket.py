import socket
import time

from typing import Callable

from lib.network_protocols.named_tuple_codec import MessageFormat
from lib.network_protocols.network_codec import NetworkCodec
from lib.sockets.sock_utils import LISTENER_PORT, create_timingout_socket, get_machine_address
from lib.sockets.socket_connection import SocketConnection

class ClientSocket:

    def __init__(self, codec: NetworkCodec[MessageFormat]):
        self._server_host = get_machine_address()
        self._quit_received = False
        self._codec = codec

    def start(self, busy_loop_func: Callable[[]] = None) -> bool:
        print("(client_socket) Connecting to server")

        connected = False

        retries_remaining = 10
        while retries_remaining > 0:
            try:
                self._sock = create_timingout_socket()
                self._sock_connection = SocketConnection(self._sock, self._codec)
                self._sock.connect((self._server_host, LISTENER_PORT))
                connected = True
                break

            except socket.timeout:
                retries_remaining -= 1
                print(f"(client_socket) Server not found, retries remaining {retries_remaining}")

                # a check for a quit condition can go here, or anything you like really.
                if busy_loop_func:
                    busy_loop_func()

                time.sleep(1.0)

        if connected:
            print("(client_socket) Established connection to server")
            self._sock_connection.start()

        return connected

    def stop(self):
        self._sock_connection.stop(blocking = True)

    def read(self) -> list[MessageFormat]:
        self._recreate_if_down()
        if self._quit_received:
            print("(client_socket) quit received, abandoning read operation")
            return None
        return self._sock_connection.read()

    def write(self, message: MessageFormat):
        self._recreate_if_down()
        if self._quit_received:
            print("(client_socket) quit received, abandoning write operation")
            return
        self._sock_connection.write(message)

    def quit_received(self) -> bool:
        return self._quit_received
        
    def _recreate_if_down(self):
        if self._sock_connection.is_down() and not self._quit_received:
            print("(client_socket) connection lost, recreating...")
            self.stop()
            self.start()

