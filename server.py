import datetime
import socket
import threading

import app
import database
import util
import widget


class Server(app.App):
    def __init__(self):
        super().__init__()

        self.DATABASE_PATH = 'db/weather.db'
        self.SERVER_ADDRESS = socket.gethostbyname(socket.gethostname())
        self.MAX_CLIENT_THREADS = 2

        # Dictionary ranslating status codes to status messages
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

        # Dictionary translating from command to the corresponding handle methods
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
        self.thread_discovery = threading.Thread(target=self.request_discovery, daemon=True)

        # Thread maintaining the main window
        self.main_window = widget.ServerWindow(self.exit)


    # ----------- Utility methods ----------

    def update_request_statistics(self, conn, command):
        """Update the statistics in the main window (including adding new row in the
        Activities table and increasing Requests Made)

        Parameters
        ----------
        conn : socket.socket
            The socket connected to the client. Needed this to get the client's address.
        command : str
            The command requested by the client.
        """

        if self.main_window.is_alive():
            with self.lock:
                self.main_window.f_useractivities.t_activities.add_row((
                    conn.getpeername()[0],
                    command,
                    datetime.datetime.now().isoformat()
                ))
                self.main_window.f_stat.inc_requestsmade()

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

    def current_thread_has_user_logged_in(self):
        """Check if user has logged in in the current thread

        Returns
        -------
        bool
        """

        return self.clients[threading.current_thread().ident] != ('', '', '')

    # ----------- Starting and exiting methods ----------

    def run(self):
        """Start the server
        """

        self.thread_discovery.start()
        self.main_window.start()

        with self.main_socket:
            self.main_socket.listen()
            while self.system_on:
                try:    
                    # Accept connection from clients
                    conn, _ = self.main_socket.accept()

                    # Reached maximum connection allowed
                    if len(self.clients) == self.MAX_CLIENT_THREADS:
                        # Notify the client that the maximum has reached
                        conn.send(util.package('001', self.status_messages['001'], ''))
                        conn.close()
                        continue
                    else:
                        # Otherwise, accept the client
                        conn.send(util.package('000', '', ''))
                    
                    with self.lock:
                        self.main_window.f_stat.inc_totalconnections()

                    # Start a thread for each accepted client
                    thread = threading.Thread(target=self.slave, args=(conn,))
                    thread.start()

                    # Initialize the user identification associated with the thread
                    self.clients[thread.ident] = ('', '', '')

                except socket.timeout:
                    continue
                except Exception:
                    with self.lock:
                        self.system_on = False

    def exit(self):
        """Close the server
        """

        self.main_window.root.destroy()
        with self.lock:
            self.system_on = False


    # ---------- Slave method used by threads ----------

    def slave(self, conn: socket.socket):
        """Target function for threads that communicate with client
        
        Parameters
        ----------
        conn : socket.socket
            The TCP socket that is communicating with the client
        """
        
        try:
            with conn:
                while self.system_on:
                    # Extract request message
                    m = self.receive_from(conn)
                    command, command_type, _, data = util.extract(m)

                    # Update the request statistics
                    self.update_request_statistics(conn, command)

                    # Do the request
                    t = self.requests[command](command_type, data)

                    # Response
                    response = util.package(t[0], self.status_messages[t[0]], t[1])
                    conn.send(response)

        # Connection to client is terminated    
        except app.ConnectionError:
            with self.lock:
                if self.main_window.is_alive():
                    self.main_window.f_stat.dec_totalconnections()
                    if self.current_thread_has_user_logged_in():
                        self.main_window.f_stat.dec_activeusers()

            # Remove the thread
            self.clients.pop(threading.current_thread().ident)
        

    # ---------- Methods handling requests from clients ----------

    def test(self, command_type, data):
        return ('000', 'vl' * 1000)

    def request_discovery(self):
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

    def request_login(self, command_type, request_data):
        """Handle the login command

        Parameters
        ----------
        command_type : str
            
        data : str
        
        Returns
        -------
        tuple
            A tuple of (status_code, response_data)
        """

        status_code = ''
        response_data = ''

        username, password = request_data.split(',', 1)
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
                if self.main_window.is_alive():
                    self.main_window.f_stat.inc_activeusers()
                
                response_data = f'{username},{user_info[0][1]}\n'                
                status_code = '000'
            else:
                status_code = '100'
        return (status_code, response_data)

    def request_signup(self, command_type, request_data):
        """Handle the signup command

        Parameters
        ----------
        command_type : str
            
        request_data : str
            

        Returns
        -------
        tuple
            A tuple of (status_code, response_data)
        """

        name, username, password = request_data.split(',', 2)
        with database.Database(self.DATABASE_PATH) as db:
            response_data = db.sign_up(username, password, name)
            if response_data:
                return ('000', '')
            return ('102', '')

    def request_logout(self, command_type, request_data):
        """Handle the logout command

        Parameters
        ----------
        command_type : str
            
        request_data : str
            

        Returns
        -------
        tuple
            A tuple of (status_code, response_data)
        """

        # User is not currently logged in
        if not self.current_thread_has_user_logged_in():
            return ('103', '')
        else:
            # Remove the user info associated with the thread
            self.clients[threading.current_thread().ident] = ('', '', '')
            
            # Decrease active users
            if self.main_window.is_alive():
                self.main_window.f_stat.dec_activeusers()
            return ('000', '')

    def request_query(self, command_type, request_data):
        """Handle the query command

        Parameters
        ----------
        command_type : str
            
        request_data : str
            

        Returns
        -------
        tuple
            A tuple of (status_code, response_data)
        """

        status_code = ''
        response_data = ''
        with database.Database(self.DATABASE_PATH) as db:
            if command_type == 'city':
                # data contains the keyword to search
                r = db.search_city(request_data)
                num_city = len(r)

                response_data = str(num_city) + '\n'
                for city in r:
                    response_data += ','.join([str(x) for x in city]) + '\n'
                status_code = '000'
            
            elif command_type == 'weather':
                # data contains the date in YYYY-MM-DD format
                r = db.query_weather_by_date(request_data)
                num_city = len(r)

                response_data = str(num_city) + '\n'
                for city in r:
                    response_data += ','.join([str(x) for x in city]) + '\n'
                status_code = '000'
            
            elif command_type == 'forecast':
                # data contains the city id
                r = db.forecast(int(request_data))
                num_result = len(r)

                response_data = str(num_result) + '\n'
                for entry in r:
                    response_data += ','.join([str(x) for x in entry]) + '\n'
                status_code = '000'
        
        return (status_code, response_data)

    def request_update(self, command_type, request_data):
        """Handle the update command

        Parameters
        ----------
        command_type : str
            
        request_data : str
            

        Returns
        -------
        tuple
            A tuple of (status_code, response_data)
        """

        # Check user's priviledge
        if self.clients[threading.current_thread().ident][1] != 'admin':
            return ('300', '')

        status_code = ''
        response_data = ''
        with self.lock:
            with database.Database(self.DATABASE_PATH) as db:
                if command_type == 'city':
                    s = request_data.split(',', 4)
                    s[3] = float(s[3])
                    s[4] = float(s[4])
                    s = tuple(s)
                    status_code = '000' if db.add_city(s) else '301'
                elif command_type == 'weather':
                    city_id, date, rest = request_data.split(',', 2)
                    status_code = '000' if db.update_weather(city_id, date, tuple(rest.split(','))) else '301'

        return (status_code, response_data)

if __name__ == '__main__':
    s = Server()
    s.run()
