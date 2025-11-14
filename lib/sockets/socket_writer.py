import socket
import traceback
from .socket_wrapper import SocketWrapper
from .socket_message_codec import MessageFormat, encode

class SocketWriter(SocketWrapper):

    def __init__(self, sock: socket.socket):

        super().__init__(
            sock = sock,
            thread_name = f"Socket writer {id(self)}"
        )

    def write(self, message: MessageFormat):
        assert self.handle.is_alive(), "Cannot write to a dead-threaded writer"
        assert message and len(message) > 0, "Cannot send an empty message"
        self._queue.put(message, block = False)

    def loop(self):
        try:
            while not self._queue.empty():
                message = self._queue.get()
                self._sock.send(encode(message))
        except socket.timeout:
            return
        except Exception as e:
            print(f"(socket_writer) received error {e}\n{traceback.print_exc()}")
            self._error_state = e
            self.is_alive = False
