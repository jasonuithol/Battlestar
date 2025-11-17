import threading
import time
import pygame

import lib.network_protocols.chat_protocol

from prompt_toolkit import PromptSession
from prompt_toolkit.patch_stdout import patch_stdout
from lib.network_protocols.chat_protocol import chat_message, get_content
from lib.network_protocols.named_tuple_codec import NamedTupleCodec
from lib.sockets.client_socket import ClientSocket

pygame.init()

client_socket = ClientSocket(
    codec = NamedTupleCodec(lib.network_protocols.chat_protocol)
)
client_socket.start()

session = PromptSession()

received_server_quit = False
crashed = False

def background_output():
    global crashed
    global received_server_quit
    try:
        while not (crashed or received_server_quit):
            message = client_socket.read()
            if message:
                content = get_content(message)
                if content.upper() == "QUIT":
                    received_server_quit = True
                print(content)
            time.sleep(0.01)
    except Exception as e:
        crashed = True
        raise

threading.Thread(target=background_output, daemon=True).start()

with patch_stdout():
    while not (crashed or received_server_quit):
        text: str = session.prompt("> ")
        if len(text) > 0:

            message = chat_message(text)
            client_socket.write(message)

        if text.upper() == "QUIT":
            time.sleep(1.0)
        else:
            time.sleep(0.01)

