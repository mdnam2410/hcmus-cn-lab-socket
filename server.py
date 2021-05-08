import app
import database
import util

import socket
import threading

class Server(app.App):
    def __init__(self):
        super().__init__()

        self.SERVER_ADDRESS = socket.gethostbyname(socket.gethostname())

        # Main database
        self.db = database.Database('db/wether.db')

        # Dictionary to translate status codes to status messages
        self.status_messages = {
            '000': 'OK',
            '100': 'Username or password not found',
            '102': 'Username already existed'
        }

        self.requests = {
            'test': self.test,
            'login': self.request_login,
            'signup': self.request_signup
        }

        self.main_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.main_socket.bind((self.SERVER_ADDRESS, self.SERVER_PORT))

        # Background thread that listens and responses to discovery requests from remote clients
        self.thread_discovery = threading.Thread(target=self.response_to_discovery_request, daemon=True)
    
    def response_to_discovery_request(self):
        """This function listens for remote client discovery message and responses
        with the server address"""

        # Create the UDP discovery socket
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.bind(('', self.DISCOVERY_PORT))

        while True:
            # Listen for requests
            message, client_connection = s.recvfrom(1024)
            # util.print_message(message)

            # Verify the discovery message
            command, *_ = util.extract(message)
            if command == 'discover':
                s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
                s.sendto(
                    util.package('000', '', self.SERVER_ADDRESS),
                    ('255.255.255.255', client_connection[1])
                )
    
    def run(self):
        self.main_socket.listen()
        self.thread_discovery.start()

        while True:
            # Accept connection from clients
            conn, _ = self.main_socket.accept()

            while True:
                # Extract request message
                m = self.receive_from(conn)
                command, command_type, _, data = util.extract(m)

                # Do the request
                t = self.requests[command](command_type, data)

                # Response
                response = util.package(t[0], self.status_messages[t[0]], t[1])
                conn.send(response)
    
    def test(self, command_type, data):
        return ('000', 'vl' * 1000)

    def request_login(self, command_type, data):
        username, password = data.split(',', 1)
        result = self.db.authenticate(username, password)
        if len(result) == 1:
            return ('000', f'{username},{password},{result[0][1]}')
        return ('100', '')
    
    def request_signup(self, command_type, data):
        username, password, name = data.split(',', 2)
        result = self.db.sign_up(username, password, name)
        if result:
            return ('000', '')
        return ('102', '')

s = Server()
s.run()
