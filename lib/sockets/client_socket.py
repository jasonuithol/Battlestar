from lib.sockets.sock_utils import LISTENER_PORT, create_timingout_socket, get_machine_address
from lib.sockets.socket_connection import SocketConnection
from lib.sockets.socket_message_codec import MessageFormat

class ClientSocket:
    def __init__(self):
        self._server_host = get_machine_address()
        self._sock = create_timingout_socket()
        self._sock_connection = SocketConnection(self._sock)

    def start(self):
        self._sock.connect((self._server_host, LISTENER_PORT))
        print("(client_socket) Connected to server")
        self._sock_connection.start()

    def stop(self):
        self._sock_connection.stop()

    def read(self) -> MessageFormat:
        return self._sock_connection.read()

    def write(self, message: MessageFormat):
        return self._sock_connection.write(message)

