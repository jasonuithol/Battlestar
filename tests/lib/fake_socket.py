from typing import Self


class FakeSocket:

    def __init__(self, output: list[bytes] = [], fileno: int = 123, fake_clients: list[tuple[tuple[str, int], Self]] = []):
        self._output = output
        self._fake_clients = fake_clients
        self._fileno = fileno

        self._input = list[bytes]()

    def bind(self, address: tuple[str, int]):
        pass

    def listen(self):
        pass

    def recv(self, buffer_size: int) -> bytes:
        return self._output.pop()

    def fileno(self) -> int:
        return self._fileno
    
    def send(self, message: bytes) -> int:
        self._input.append(message)

    def accept(self):
        return self._fake_clients.pop()
    
