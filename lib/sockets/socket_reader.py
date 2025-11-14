import socket
import traceback

from .socket_wrapper import SocketWrapper
from .sock_utils import BUFFER_SIZE
from .socket_message_codec import MessageFormat, decode

class SocketReader(SocketWrapper):

    def __init__(self, sock: socket.socket):

        super().__init__(
            sock = sock,
            thread_name = f"Socket reader {id(self)}"
        )

    def loop(self):
        try:
            message = self._sock.recv(BUFFER_SIZE)
            if message is None or len(message) == 0:
                print("(socket_reader) received empty message - peer disconnected - closing connection")
                self.is_alive = False
                return
            self._queue.put(message)
        except socket.timeout:
            return
        except Exception as e:
            print(f"(socket_reader) received error {e}\n{traceback.print_exc()}")
            self._error_state = e
            self.is_alive = False

    def read(self) -> MessageFormat:
        assert self.handle.is_alive(), "Cannot read from a dead-threaded reader"
        if self._queue.empty():
            return None
        return decode(self._queue.get())
    