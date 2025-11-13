import queue
import socket

from lib.thread_runner import ThreadRunner

from .sock_utils import BUFFER_SIZE, QUEUE_SIZE
from .socket_message_codec import MessageFormat, decode

class SocketReader(ThreadRunner):

    def __init__(self, sock: socket.socket):

        super().__init__(
            name = f"Socket reader {id(self)}",
            daemon = True,
            sleep = 0.01
        )

        # This socket is shared, so this class does NOT close it.
        self._sock     = sock

        self._incoming = queue.Queue(QUEUE_SIZE)

    def loop(self):
        try:
            message = self._sock.recv(BUFFER_SIZE)
            if message is None or len(message) == 0:
                print("(socket_reader) discarding empty message")
                return
            self._incoming.put(message)
        except socket.timeout:
            return

    def read(self) -> MessageFormat:
        assert self.handle.is_alive(), "Cannot read from a dead-threaded reader"
        if self._incoming.empty():
            return None
        return decode(self._incoming.get())