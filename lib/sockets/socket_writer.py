import socket
import traceback

from lib.network_protocols.named_tuple_codec import MessageFormat
from lib.network_protocols.network_codec import NetworkCodec
from .socket_wrapper import SocketWrapper

class SocketWriter(SocketWrapper):

    def __init__(self, sock: socket.socket, codec: NetworkCodec[MessageFormat]):

        super().__init__(
            sock = sock,
            thread_name = f"Socket writer {id(self)}"
        )

        self._codec = codec

    def write(self, message: MessageFormat):
        assert self.handle.is_alive(), "Cannot write to a dead-threaded writer"
        assert not message is None, "Cannot send None as a message"
        self._queue.put(message, block = False)

    def loop(self):
        try:
            while not self._queue.empty():
                message = self._queue.get()
                print(f"(socket_writer) sending message: {message}")
                encoded = self._codec.encode(message)
                self._sock.send(encoded)
        except socket.timeout:
            return
        except Exception as e:
            print(f"(socket_writer) received error {e}\n{traceback.print_exc()}")
            self._error_state = e
            self._alive = False
