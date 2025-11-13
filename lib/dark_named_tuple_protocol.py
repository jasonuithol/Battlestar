
from typing import NamedTuple
from lib.sockets.socket_message_codec import MessageFormat

class DarkNamedTupleProtocol:

    # Let's actually take advantage of the UTF-8 encoding.
    DELIMITER = "¦"
    NULL = "¨"

    def __init__(self, protocol_format_module):
        self._protocol_format_module = protocol_format_module

    def encode(self, message: NamedTuple) -> MessageFormat:
        return self._to_string(message)

    def decode(self, data: MessageFormat) -> NamedTuple:
        return self._from_string(data)

    def _to_string(self, message: NamedTuple) -> str:
        name = type(message).__name__  # keep consistent
        values = []
        for f in message._fields:
            value = getattr(message, f)
            if value is None:
                values.append(self.NULL)
            else:
                values.append(str(value))
        return self.DELIMITER.join([name] + values)

    def _from_string(self, message_string: str) -> NamedTuple:
        parts = message_string.split(self.DELIMITER)
        name, values = parts[0], parts[1:]
        cls: NamedTuple = getattr(self._protocol_format_module, name, None)
        if cls is None:
            raise ValueError(f"Unknown message type: {name}")
        if len(values) != len(cls._fields):
            raise ValueError(f"Field count mismatch for {name}: expected {len(cls._fields)}, got {len(values)}")
        casted = []
        for f, v in zip(cls._fields, values):
            typ = cls.__annotations__[f]
            if v == self.NULL:
                casted.append(None)
            else:
                casted.append(typ(v))
        return cls(*casted)