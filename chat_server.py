import time
import lib.network_protocols.chat_protocol

from lib.network_protocols.chat_protocol import ChatMessage, get_content
from lib.network_protocols.named_tuple_codec import NamedTupleCodec
from lib.sockets.server_socket import ServerSocket

server_socket = ServerSocket(codec = NamedTupleCodec(lib.network_protocols.chat_protocol))
server_socket.start()

flood = False

while True:
    messages = server_socket.readall()
    for message in messages:

        sender, formatted_content = message

        if formatted_content is None:
            print("Dropping null message")
        else:
            print(f"received '{formatted_content}' from '{sender}'")

            content = get_content(formatted_content)

            if content.upper() == "QUIT":
                server_socket.broadcast(ChatMessage("QUIT"))
                time.sleep(1.0)
                exit()

            if content.upper() == "FLOOD":
                flood = not flood
                print(f"FLOOD = {flood}")
                continue

            if flood:
                repeat = 100
            else:
                repeat = 1

            for _ in range(repeat):
                message = ChatMessage(f"[{sender}], {content}")
                server_socket.broadcast(message)
                time.sleep(0.001)

    time.sleep(0.01)
