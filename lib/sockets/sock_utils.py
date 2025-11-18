import ipaddress
import socket

LISTENER_PORT = 5000
SOCK_TIMEOUT  = 1.0
QUEUE_SIZE    = 100
BUFFER_SIZE   = 1024
EMTPY_MESSAGE_LIMIT = 3

NetworkId = tuple[str, int]

def create_timingout_socket() -> socket.socket:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Socket options
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
    sock.settimeout(SOCK_TIMEOUT)
    return sock

def get_machine_address() -> str:
    hostname = socket.gethostname()
    ip_address = socket.gethostbyname(hostname)
    ip = ipaddress.ip_address(ip_address)
    if ip.is_loopback:
        print("(socket_utils) Falling back to DGRAM method for obtaining machine address")
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            # doesn't need to be reachable, just used to pick an interface
            s.connect(("8.8.8.8", 80))
            ip_address = s.getsockname()[0]
        finally:
            s.close()
    print(f"(socket_utils) obtained machine ip address: {ip_address}")
    return ip_address


    
