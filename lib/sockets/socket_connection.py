import socket

from lib.network_protocols.named_tuple_codec import MessageFormat
from lib.network_protocols.network_codec import NetworkCodec

from .socket_reader import SocketReader
from .socket_writer import SocketWriter

class SocketConnection:

    def __init__(self, sock: socket.socket, codec: NetworkCodec[MessageFormat]):
        self._sock   = sock
        self._reader = SocketReader(sock, codec)
        self._writer = SocketWriter(sock, codec)
        __slots__ = ()

    def start(self):
        self._reader.start()
        self._writer.start()

    def stop(self, blocking: bool):
        self._reader.stop(blocking)
        self._writer.stop(blocking)
        self._sock.close()

    def read(self) -> list[MessageFormat]:
        return self._reader.read()
    
    def write(self, message: MessageFormat):
        self._writer.write(message)

    def is_alive(self) -> bool:
        return self._reader.is_alive and self._writer.is_alive

    def has_error_state(self) -> bool:
        return self._reader.error_state() or self._writer.error_state()
    
    def is_open(self) -> bool:
        return self._reader.connection_is_open() and self._writer.connection_is_open()
    
    def is_down(self) -> bool:
        return (
            self.has_error_state() 
            or 
            (not self.is_alive()) 
            or 
            (not self.is_open())
        )
 