import time
from lib.sockets.server_socket import ServerSocket
from tests.lib.fake_socket import FakeSocket

def test_client_connect():
    # setup
    c = FakeSocket()

    ss = ServerSocket(codec = None)
    a = "192.168.1.0", 12345
    ss._sock = FakeSocket(fake_clients=[(c,a)])
    
    # execute
    ss.start()
    time.sleep(0.01)

    # assert
    assert len(ss.clients) == 1, f"expected 1 client, got {len(ss.clients)}"
    assert a in ss.clients.keys(), f"expected address {a} to be in list of client network_ids"

