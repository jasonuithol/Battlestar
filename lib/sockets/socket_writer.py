import queue
import socket

from lib.thread_runner import ThreadRunner

from .sock_utils import QUEUE_SIZE
from .socket_message_codec import MessageFormat, encode

class SocketWriter(ThreadRunner):

    def __init__(self, sock: socket.socket):

        super().__init__(
            name = f"Socket writer {id(self)}",
            daemon = True,
            sleep = 0.01
        )

        # This socket is shared, so this class does NOT close it.
        self._sock     = sock

        self._outgoing = queue.Queue(QUEUE_SIZE)

    def write(self, message: MessageFormat):
        assert self.handle.is_alive(), "Cannot write to a dead-threaded writer"
        assert message and len(message) > 0, "Cannot send an empty message"
        self._outgoing.put(message, block = False)

    def loop(self):
        try:
            while not self._outgoing.empty():
                message = self._outgoing.get()
                self._sock.send(encode(message))
        except socket.timeout:
            return
