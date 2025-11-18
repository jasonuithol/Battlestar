import socket
import traceback

from lib.network_protocols.named_tuple_codec import MessageFormat
from lib.network_protocols.network_codec import NetworkCodec

from .socket_wrapper import SocketWrapper
from .sock_utils import BUFFER_SIZE, EMTPY_MESSAGE_LIMIT

class SocketReader(SocketWrapper):

    def __init__(self, sock: socket.socket, codec: NetworkCodec[MessageFormat]):

        super().__init__(
            sock = sock,
            thread_name = f"Socket reader {id(self)}"
        )

        self._codec = codec
        self._empty_message_count = 0

    def loop(self):
        try:
            message = self._sock.recv(BUFFER_SIZE)
            if message is None or len(message) == 0:
                self._empty_message_count += 1
                print(f"(socket_reader) received empty message #{self._empty_message_count} - dropping message. Limit = {EMTPY_MESSAGE_LIMIT}")
                if self._empty_message_count >= EMTPY_MESSAGE_LIMIT:
                    self._alive = False
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
    