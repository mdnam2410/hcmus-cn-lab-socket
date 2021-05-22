import app
import database
import util
import widget

import datetime
import socket
import threading

class Server(app.App):
    def __init__(self):
        super().__init__()

        self.DATABASE_PATH = 'db/wether.db'
        self.SERVER_ADDRESS = socket.gethostbyname(socket.gethostname())
        self.MAX_CLIENT_THREAD = 2

        # Main database
        # self.db = database.Database('db/wether.db')

        # Dictionary to translate status codes to status messages
        self.status_messages = {
            '000': 'OK',
            '001': 'Reached maximum client',
            '100': 'Username or password not found',
            '101': 'Already logged in',
            '102': 'Username already existed',
            '103': 'Already logged out',
            '104': 'Not admin',
            '300': 'Permission denied',
            '301': 'Error in adding city'
        }

        self.requests = {
            'test': self.test,
            'login': self.request_login,
            'signup': self.request_signup,
            'logout': self.request_logout,
            'query': self.request_query,
            'update': self.request_update
        }

        # List of clients
        self.clients = dict()

        # Flag to signal the threads that the server is going down
        self.system_on = True

        # Lock
        self.lock = threading.Lock()

        self.main_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.main_socket.settimeout(1.0)
        self.main_socket.bind((self.SERVER_ADDRESS, self.SERVER_PORT))

        # Background thread that listens and responses to discovery requests from remote clients
        self.thread_discovery = threading.Thread(target=self.response_to_discovery_request, daemon=True)

        # A thread maintaining GUI
        self.interface = widget.ServerInterface(self.exit)

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
        self.thread_discovery.start()
        self.interface.start()

        with self.main_socket:
            self.main_socket.listen()
            while self.system_on:
                try:    
                    # Accept connection from clients
                    conn, _ = self.main_socket.accept()

                    # Reached maximum connection allowed
                    if len(self.clients) == self.MAX_CLIENT_THREAD:
                        # Notify the client that the maximum has reached
                        conn.send(util.package('001', self.status_messages['001'], ''))

                        # Close the connection
                        conn.close()
                        continue
                    else:
                        # It's OK
                        conn.send(util.package('000', '', ''))
                    
                    with self.lock:
                        self.interface.frame_stat.inc_totalconnections()

                    # Start a thread for the accepted client
                    thread = threading.Thread(target=self.serve, args=(conn,))
                    thread.start()
                    # thread.join()

                    # Initialize the user identification associated with the thread
                    self.clients[thread.ident] = ('', '', '')
                except socket.timeout:
                    continue
                except Exception:
                    self.system_on = False

    def exit(self):
        self.interface.root.destroy()
        with self.lock:
            print('Here')
            self.system_on = False
            print('At here')

    def update_record(self, conn, command):
        self.interface.frame_useractivities.table.add_entry((
            conn.getpeername()[0],
            command,
            datetime.datetime.now().isoformat()
        ))
        self.interface.frame_stat.inc_requestsmade()

    def serve(self, conn: socket.socket):
        """Target function for threads that communicate with client
        
        Parameters
        ----------
        conn : socket.socket
            The TCP socket that is communicating with the client
        
        Returns
        -------
        None
        """
        
        try:
            with conn:
                while self.system_on:
                    # Extract request message
                    m = self.receive_from(conn)
                    command, command_type, _, data = util.extract(m)

                    # Update the GUI statistics
                    self.update_record(conn, command)

                    # Do the request
                    t = self.requests[command](command_type, data)


                    # Response
                    response = util.package(t[0], self.status_messages[t[0]], t[1])
                    conn.send(response)
        except app.ConnectionError:
            with self.lock:
                self.interface.frame_stat.dec_totalconnections()
            # Remove the thread
            self.clients.pop(threading.current_thread().ident)
        

    def test(self, command_type, data):
        return ('000', 'vl' * 1000)

    def logged_in(self, username) -> bool:
        """Check if the username has already logged in (in the current thread or other thread)

        Returns
        -------
        bool
            True if the client has already logged in, False otherwise
        """
        for v in self.clients.values():
            if username in v:
                return True
        return False
    
    def request_login(self, command_type, data):
        status_code = ''
        result = ''

        username, password = data.split(',', 1)
        if self.logged_in(username):
            return ('101', '')

        with database.Database(self.DATABASE_PATH) as db:
            admin = False
            if command_type == 'admin':
                admin = True
                if len(username) != 3 or not username.isnumeric():
                    return ('104', '')

            user_info = db.authenticate(username, password)

            if len(user_info) == 1:
                # Record user login time
                self.clients[threading.current_thread().ident] = (
                    username,
                    'admin' if admin else 'ordinary',
                    datetime.datetime.now()
                )

                # Increase active users
                self.interface.frame_stat.inc_activeusers()
                
                result = f'{username},{user_info[0][1]}\n'                
                status_code = '000'
            else:
                status_code = '100'
        return (status_code, result)

    def request_signup(self, command_type, data):
        name, username, password = data.split(',', 2)
        with database.Database(self.DATABASE_PATH) as db:
            result = db.sign_up(username, password, name)
            if result:
                return ('000', '')
            return ('102', '')

    def request_logout(self, command_type, data):
        # Get user info corresponding to the thread
        r = self.clients[threading.current_thread().ident]

        # User is not currently logged in
        if r == ('', '', ''):
            return ('103', '')
        else:
            self.clients[threading.current_thread().ident] = ('', '', '')
            
            # Decrease active users
            self.interface.frame_stat.dec_activeusers()
            return ('000', '')

    def request_query(self, command_type, data):
        status_code = ''
        result = ''
        with database.Database(self.DATABASE_PATH) as db:
            if command_type == 'city':
                # data contains the keyword to search
                r = db.search_city(data)
                num_city = len(r)

                result = str(num_city) + '\n'
                for city in r:
                    result += ','.join([str(x) for x in city]) + '\n'
                status_code = '000'
            
            elif command_type == 'weather':
                # data contains the date in YYYY-MM-DD format
                r = db.weather_by_date(data)
                num_city = len(r)

                result = str(num_city) + '\n'
                for city in r:
                    result += ','.join([str(x) for x in city]) + '\n'
                status_code = '000'
            
            elif command_type == 'forecast':
                # data contains the city id
                r = db.forecast(int(data))
                num_result = len(r)

                result = str(num_result) + '\n'
                for entry in r:
                    result += ','.join([str(x) for x in entry]) + '\n'
                status_code = '000'
        
        return (status_code, result)

    def request_update(self, command_type, data):
        # Check user's priviledge
        if self.clients[threading.current_thread().ident][1] != 'admin':
            return ('300', '')

        status_code = ''
        result = ''
        with self.lock:
            with database.Database(self.DATABASE_PATH) as db:
                if command_type == 'city':
                    status_code = '000' if db.add_city(data) else '301'
                elif command_type == 'weather':
                    status_code = '000' if db.update_weather_by_city() else '301'

        return (status_code, result)

if __name__ == '__main__':
    s = Server()
    s.run()
