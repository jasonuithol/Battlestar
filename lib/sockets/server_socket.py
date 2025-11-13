import socket
from threading import Lock

from lib.sockets.socket_message_codec import MessageFormat
from lib.thread_runner import ThreadRunner

from .socket_connection import SocketConnection
from .sock_utils import LISTENER_PORT, NetworkId, create_timingout_socket, get_machine_address

class ServerSocket(ThreadRunner):
    def __init__(self):
        super().__init__(
            name   = "Server Listener",
            daemon = True,
            sleep = 1.0
        )

        self._host = get_machine_address()
        self._sock = create_timingout_socket()

        self._clients_lock = Lock()
        self._clients = dict[NetworkId, SocketConnection]()

    def start(self):
        self._sock.bind((self._host, LISTENER_PORT))
        self._sock.listen()
        super().start()

    def loop(self):
        try:
            client_sock, client_address = self._sock.accept()
        except socket.timeout:
            return
        
        print(f"(server_socket) got client connection: {client_address}")
        socket_connection = SocketConnection(client_sock)
        socket_connection.start()
        self._add_client(client_address, socket_connection)

    def broadcast(self, message: MessageFormat):
        for client in self.clients.values():
            client.write(message)

    def write_to(self, client_address: NetworkId, message: MessageFormat):
        client = self._get_client(client_address)
        client.write(message)

    def readall(self) -> list[tuple[NetworkId, MessageFormat]]:
        messages = []
        for address, client in self.clients.items():
            message = client.read()
            if message:
                messages.append((address, message))
        return messages

    def _add_client(self, client_address: NetworkId, socket_connection: SocketConnection):
        with self._clients_lock:
            self._clients[client_address] = socket_connection

    def _get_client(self, client_address: NetworkId):
        with self._clients_lock:
            return self._clients[client_address]

    @property
    def clients(self) -> dict[NetworkId, SocketConnection]:
        with self._clients_lock:
            return dict(self._clients)

    def stop(self):
        super().stop()
        self._sock.close()

        for socket_connection in self.clients.values():
            socket_connection.stop()
