import util

import socket
import time

DISCOVERY_PORT = 2410
SERVER_PORT = 2802

def discover_server() -> socket.socket:
    """ This function mimics the behavior of a DNS client when it tries to
    find a DNS server on the same network. The client broadcasts a discovery message
    into the network using UDP, and if the server receives, it will reply with an
    acknowledgement message along with its IP address. The client then tries to create 
    a TCP connection to this address.
    If the protocol is carried out successfully, the function returns a new socket
    object for the newly-created TCP connection. Otherwise, None is returned.
    """

    # Create an UDP socket
    u = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # Broadcast the discovery message
    u.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    u.sendto(util.package('discover', '', ''), ('255.255.255.255', DISCOVERY_PORT))
    
    # Receive the acknowledgement message from the server
    message, _ = u.recvfrom(1024)
    util.print_message(message)

    # Extract the acknowledgement message
    e, _, _, addr = util.extract(message)

    if e == '000':
        # The UDP socket is completed
        u.close()

        # Create new TCP connection using the extracted server address
        t = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            t.connect((addr, SERVER_PORT))
            return t
        except ConnectionRefusedError:
            return None
    else:
        return None

class ConnectionError(Exception):
    pass

class Client:
    def __init__(self):
        self.s = discover_server()
        if self.s is None:
            raise ConnectionError('Unable to connect to server')
    
    def send(self, message):
        self.s.send(message)

    def receive(self):
        message = self.s.recv(2 ** 16)
        return message
    
    def receive2(self):
        self.socket_buffer = 1024

        message = self.s.recv(self.socket_buffer)
        _, _, size, _ = util.extract(message)

        # The number of the rest submessages need to receive
        r = size // self.socket_buffer - 1
        print(r)
        while r >= 0:
            message += self.s.recv(self.socket_buffer)
            r -= 1
        return message

    def test(self):
        data = ''
        self.send(util.package('kuso', '', data))
        m = self.receive2()
        status_code, status_message, size, data = util.extract(m)
        print(size)
        print(len(data))

    def login(self):
        self.username = input('Username: ')
        self.password = input('Password: ')
        self.send(util.package('login', '', f'{self.username},{self.password}'))
        status_code, status_message, _ = util.extract(self.receive())
        if status_code == 0:
            print('Logged in')
        else:
            print('Error:', status_message)

client = Client()
# client.login()
client.test()
