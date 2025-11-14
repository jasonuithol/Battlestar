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

#        self._dead_clients_lock = Lock()
        self._dead_clients = set[NetworkId]()

    def start(self):
        self._sock.bind((self._host, LISTENER_PORT))
        self._sock.listen()
        super().start()

    # Internal Worker thread
    def loop(self):
        try:
            client_sock, network_id = self._sock.accept()
        except socket.timeout:
            return
        
        print(f"(server_socket) got client connection: {network_id}")
        socket_connection = SocketConnection(client_sock)
        socket_connection.start()
        self._add_client(network_id, socket_connection)

    def broadcast(self, message: MessageFormat):
        for network_id in self.clients.keys():
            self.write_to(network_id, message)

    def readall(self) -> list[tuple[NetworkId, MessageFormat]]:
        messages = []
        for network_id in self.clients.keys():
            message = self.read_from(network_id)
            if message:
                messages.append((network_id, message))
        return messages

    def read_from(self, network_id: NetworkId) -> MessageFormat:
        client = self._get_client(network_id)
        if client:
            if client.is_down():
                self._reap_dead_client(network_id)
                return None
            message = client.read()
            return message
        else:
            print(f"(server_socket) returning None for read from unknown network_id: {network_id}")
            return None

    def write_to(self, network_id: NetworkId, message: MessageFormat):
        client = self._get_client(network_id)
        if client:
            if client.is_down():
                self._reap_dead_client(network_id)
            else:
                client.write(message)
        else:
            print(f"(server_socket) ignoring write to unknown network_id: {network_id}")

    def _add_client(self, network_id: NetworkId, client_connection: SocketConnection):
        with self._clients_lock:
            self._clients[network_id] = client_connection

    def _remove_client(self, network_id: NetworkId):
        with self._clients_lock:
            del self._clients[network_id]

    def _get_client(self, network_id: NetworkId):
        with self._clients_lock:
            return self._clients.get(network_id, None)

    @property
    def clients(self) -> dict[NetworkId, SocketConnection]:
        with self._clients_lock:
            return dict(self._clients)

    def _add_dead_client(self, network_id: NetworkId):
        assert isinstance(network_id, tuple), f"bad network_id: {network_id}"
        self._dead_clients.add(network_id)

    def remove_dead_client(self, network_id: NetworkId):
        assert isinstance(network_id, tuple), f"bad network_id: {network_id}"
        self._dead_clients.remove(network_id)

    @property
    def dead_clients(self) -> set[NetworkId]:
        return set(self._dead_clients)

    def stop(self):
        super().stop()
        self._sock.close()

        for client_connection in self.clients.values():
            client_connection.stop(blocking = True)

    def _reap_dead_client(self, network_id: NetworkId):
        assert isinstance(network_id, tuple), f"bad network_id: {network_id}"
        print(f"(server_socket) connection to client lost, reaping: network_id={network_id}")
        client_connection = self._get_client(network_id)
        if client_connection:
            client_connection.stop(blocking = False)
            self._remove_client(network_id)
            self._add_dead_client(network_id)
        else:
            print(f"(server_socket) nothing to reap: network_id={network_id}")

