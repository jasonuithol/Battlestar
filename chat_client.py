import threading
import time

from prompt_toolkit import PromptSession
from prompt_toolkit.patch_stdout import patch_stdout
from lib.sockets.client_socket import ClientSocket

client_socket = ClientSocket()
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
                if message.upper() == "QUIT":
                    received_server_quit = True
                print(message)
            time.sleep(0.01)
    except Exception as e:
        crashed = True
        raise

threading.Thread(target=background_output, daemon=True).start()

with patch_stdout():
    while not (crashed or received_server_quit):
        text: str = session.prompt("> ")
        if len(text) > 0:
            client_socket.write(text)
        if text.upper() == "QUIT":
            time.sleep(1.0)
        else:
            time.sleep(0.01)

