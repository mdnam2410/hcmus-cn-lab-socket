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
            '102': 'Username already existed',
        }

        self.requests = {
            'test': self.test,
            'login': self.request_login,
            'signup': self.request_signup,
            'logout': self.request_logout,
            'query': self.request_query
        }

        # List of signed in users
        self.current_user = dict()

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
            try:
                # Accept connection from clients
                conn, _ = self.main_socket.accept()

                with conn:
                    while True:
                        # Extract request message
                        m = self.receive_from(conn)
                        command, command_type, _, data = util.extract(m)

                        # Do the request
                        t = self.requests[command](command_type, data)

                        # Response
                        response = util.package(t[0], self.status_messages[t[0]], t[1])
                        conn.send(response)
            except app.ConnectionError as e:
                print(e)

    def test(self, command_type, data):
        return ('000', 'vl' * 1000)

    def request_login(self, command_type, data):
        username, password = data.split(',', 1)
        user_info = self.db.authenticate(username, password)

        if len(user_info) == 1:
            # TODO: Add timestamp for user login time
            self.current_user[username] = ''

            # Get today's weather by default
            today_weather = self.db.today_weather()
            num_city = len(today_weather)

            # Pack everything into the data field
            result = f'{username},{user_info[0][1]}\n' + str(num_city) + '\n'
            for city in today_weather:
                result += ','.join([str(x) for x in city]) + '\n'
            return ('000', result)
        
        return ('100', '')

    def request_signup(self, command_type, data):
        username, password, name = data.split(',', 2)
        result = self.db.sign_up(username, password, name)
        if result:
            return ('000', '')
        return ('102', '')

    def request_logout(self, command_type, data):
        r = self.current_user.pop(data, None)
        # User is not currently logged in
        if r is None:
            # TODO: Determine status code
            return ('103', '')
        else:
            return ('000', '')

    def request_query(self, command_type, data):
        status_code = ''
        result = ''
        if command_type == 'city':
            # data contains the keyword to search
            r = self.db.search_city(data)
            num_city = len(r)

            result = str(num_city) + '\n'
            for city in r:
                result += ','.join([str(x) for x in city]) + '\n'
            status_code = '000'
        
        elif command_type == 'weather':
            # data contains the date in YYYY-MM-DD format
            r = self.db.weather_by_date(data)
            num_city = len(r)

            result = str(num_city) + '\n'
            for city in r:
                result += ','.join([str(x) for x in city]) + '\n'
            status_code = '000'
        
        elif command_type == 'forecast':
            # data contains the city id
            r = self.db.forecast(int(data))
            num_result = len(r)

            result = str(num_result) + '\n'
            for entry in r:
                result += ','.join([str(x) for x in entry]) + '\n'
            status_code = '000'
        
        return (status_code, result)
    
s = Server()
s.run()
