import time
from lib.sockets.server_socket import ServerSocket

server_socket = ServerSocket()
server_socket.start()

while True:
    messages = server_socket.readall()
    for message in messages:
        sender, content = message
        if content is None:
            print("Dropping null message")
        else:
            print(f"received '{content}' from '{sender}'")

            if content.upper() == "QUIT":
                server_socket.broadcast("QUIT")
                time.sleep(1.0)
                exit()

            server_socket.broadcast(f"[{sender}], {content}")

    time.sleep(0.01)
