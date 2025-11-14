import queue
import socket

from lib.thread_runner import ThreadRunner
from .sock_utils import QUEUE_SIZE

class SocketWrapper(ThreadRunner):

    def __init__(self, sock: socket.socket, thread_name: str):

        super().__init__(
            name   = thread_name,
            daemon = True,
            sleep  =  0.01
        )
    
        # This socket is shared, so this class does NOT close it.
        self._sock = sock

        self._queue = queue.Queue(QUEUE_SIZE)
        self._error_state: Exception = None
    
    def connection_is_open(self):
        return self._sock.fileno() != -1
    
    def error_state(self) -> Exception:
        return self._error_state
    