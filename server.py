import database
import util

import socket
import threading

SERVER_ADDRESS = socket.gethostbyname(socket.gethostname())
SERVER_PORT = 2802
DISCOVERY_PORT = 2410

def response_to_discovery_request():
    """This function listens for remote client discovery message and responses
    with the server address"""

    # Create the UDP discovery socket
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind(('', DISCOVERY_PORT))

    while True:
        # Listen for requests
        message, client_connection = s.recvfrom(1024)
        util.print_message(message)

        # Verify the discovery message
        command, _, _ = util.extract(message)
        if command == 'discover':
            s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            s.sendto(
                util.package('000', '', SERVER_ADDRESS),
                ('255.255.255.255', client_connection[1])
            )

class Server:
    def __init__(self):
        self.serving_functions = {
            'login': self.command_login
        }

        self.status_messages = {
            '000': 'OK',
            '100': 'Username or password not found'
        }

        self.db = database.Database('db/wether.db')

        # Background thread that listens and responses to discovery requests from remote clients
        self.thread_discovery = threading.Thread(target=response_to_discovery_request, daemon=True)
        self.thread_discovery.start()

        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((SERVER_ADDRESS, SERVER_PORT))
        self.server_socket.listen()

        while True:
            c, _ = self.server_socket.accept()
            m = c.recv(1024)
            command, option, data = util.extract(m)
            t = self.serving_functions[command](option, data)
            reply = util.package(t[0], self.status_messages[t[0]], t[1])
            util.print_message(reply)
            c.send(reply)
        
    def command_login(self, option, data):
        username, password = data.split(',', 1)
        result = self.db.authenticate(username, password)
        if len(result) == 1:
            return ('000', f'{username},{password},{result[0][2]}')
        return ('100', '')


server = Server()