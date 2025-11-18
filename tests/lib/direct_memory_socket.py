import queue
import socket
from typing import Self

class DirectMemorySocket:

    def __init__(self, queue_size: int = 100, timeout: float = 1.0, client: Self = None):
        self._queue = queue.Queue(queue_size)
        self._timeout = timeout

        self._buffer: bytes = b""
        self._alive = True
        self._client = client

    def bind(self, address: tuple[str, int]):
        pass

    def listen(self):
        pass

    def recv(self, buffer_size: int) -> bytes:
        if self._alive:
            try:
                return self._queue.get(timeout = self._timeout)
            except TimeoutError:
                raise socket.timeout
            
        else:
            return None

    def fileno(self) -> int:
        if self._alive:
            return 123
        else:
            return -1
    
    def send(self, message: bytes) -> int:
        self._queue.put(message)

    def close(self):
        self._alive = False

    def accept(self) -> Self:
        return self._client
