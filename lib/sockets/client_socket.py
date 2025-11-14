import socket

import pygame
from lib.sockets.sock_utils import LISTENER_PORT, create_timingout_socket, get_machine_address
from lib.sockets.socket_connection import SocketConnection
from lib.sockets.socket_message_codec import MessageFormat

class ClientSocket:
    def __init__(self):
        self._server_host = get_machine_address()
        self._quit_received = False

    def start(self):
        print("(client_socket) Connecting to server")

        unconnected = True
        while unconnected:
            try:
                self._sock = create_timingout_socket()
                self._sock_connection = SocketConnection(self._sock)
                self._sock.connect((self._server_host, LISTENER_PORT))
                unconnected = False

            except socket.timeout:

                print("(client_socket) Server not found, retrying.")

                for event in pygame.event.get():
                    if (event.type == pygame.QUIT) or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                        self._quit_received = True
                        return


        print("(client_socket) Established connection to server")
        self._sock_connection.start()

    def stop(self):
        self._sock_connection.stop(blocking = True)

    def read(self) -> MessageFormat:
        self._recreate_if_down()
        if self._quit_received:
            return None
        return self._sock_connection.read()

    def write(self, message: MessageFormat):
        self._recreate_if_down()
        if self._quit_received:
            return
        self._sock_connection.write(message)

    def quit_received(self) -> bool:
        return self._quit_received
        
    def _recreate_if_down(self):
        if self._sock_connection.is_down() and not self._quit_received:
            print("(client_socket) connection lost, recreating...")
            self.stop()
            self.start()

