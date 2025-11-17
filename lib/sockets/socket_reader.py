import socket
import traceback

from lib.network_protocols.named_tuple_codec import MessageFormat
from lib.network_protocols.network_codec import NetworkCodec

from .socket_wrapper import SocketWrapper
from .sock_utils import BUFFER_SIZE

class SocketReader(SocketWrapper):

    def __init__(self, sock: socket.socket, codec: NetworkCodec[MessageFormat]):

        super().__init__(
            sock = sock,
            thread_name = f"Socket reader {id(self)}"
        )

        self._codec = codec

    def loop(self):
        try:
            message = self._sock.recv(BUFFER_SIZE)
            if message is None or len(message) == 0:
                print("(socket_reader) received empty message - dropping message")
#                print("(socket_reader) received empty message - peer disconnected - closing connection")
#                self.is_alive = False
                return
            decoded = self._codec.decode(message)
            for decoded in self._codec.decode(message):
                print(f"(socket_reader) received message: {decoded}")
                self._queue.put(decoded)
        except socket.timeout:
            return
        except Exception as e:
            print(f"(socket_reader) received error {e}\n{traceback.print_exc()}")
            self._error_state = e
            self._alive = False

    def read(self) -> list[MessageFormat]:
        assert self.handle.is_alive(), "Cannot read from a dead-threaded reader"
        messages = []
        while not self._queue.empty():
            message = self._queue.get()
            messages.append(message)
        return messages
    