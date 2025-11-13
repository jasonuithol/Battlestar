import socket

from lib.sockets.socket_message_codec import MessageFormat

from .socket_reader import SocketReader
from .socket_writer import SocketWriter

class SocketConnection:

    def __init__(self, sock: socket.socket):
        self._sock   = sock
        self._reader = SocketReader(sock)
        self._writer = SocketWriter(sock)
        __slots__ = ()

    def start(self):
        self._reader.start()
        self._writer.start()

    def stop(self):
        self._reader.stop()
        self._writer.stop()
        self._sock.close()

    def read(self) -> MessageFormat:
        return self._reader.read()
    
    def write(self, message: MessageFormat):
        self._writer.write(message)
