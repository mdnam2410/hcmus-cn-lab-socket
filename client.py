from datetime import date
import app
import login
import util

import socket
import tkinter as tk

class Client(app.App):
    def __init__(self, root):
        app.App.__init__(self)
        self.root = root

        self.main_socket = self.discover_server()
        if self.main_socket is None:
            raise app.ConnectionError('Unable to connect to server')
        
        # Check if the maximum number of clients the server can serve is reached
        status_code, status_message, _, _ = util.extract(self.receive())
        if status_code != '000':
            self.main_socket.close()
            raise app.ConnectionError(status_message)

        self.username = ''
        self.name = ''

        self.create_login_window()
        
    def create_login_window(self):
        # Create the login window
        self.window_login = tk.Toplevel(master=self.root)

        # Create the layout
        self.frame_login = login.Login(self.window_login)

        # Bind commands
        self.frame_login.button_login.configure(command=self.command_wlogin_button_login)
        self.frame_login.label_adminlogin.bind('<Button-1>', self.command_wlogin_label_adminlogin)
        self.frame_login.label_signup.bind('<Button-1>', self.command_wlogin_label_signup)

        # Bind the delete window protocol
        self.window_login.protocol('WM_DELETE_WINDOW', self.wlogin_onclosing)

        # Display
        self.frame_login.pack()


    # Widgets' commands

    def wlogin_onclosing(self):
        self.window_login.destroy()
        self.root.destroy()

    def command_wlogin_button_login(self):
        """Action taken when user hits the "Login" button in the login window
        """

        u, p = self.frame_login.var_username.get(), self.frame_login.var_password.get()
        result = self.login(u, p) if self.frame_login.login_option == 'ordinary' else self.login_admin(u, p)
        if type(result) is tuple:
            self.frame_login.var_prompt.set(result[1])
            return
        self.window_login.destroy()
        self.root.deiconify()

    def command_wlogin_label_adminlogin(self, event):
        if self.frame_login.login_option == 'ordinary':
            self.frame_login.var_login_button_text.set('Log in as admin')
            self.frame_login.login_option = 'admin'
            self.frame_login.label_adminlogin.configure(text='Log in as ordinary user')
        else:
            self.frame_login.var_login_button_text.set('Log in')
            self.frame_login.login_option = 'ordinary'
            self.frame_login.label_adminlogin.configure(text='Log in as admin')

    def command_wlogin_label_signup(self, event):
        """Action taken when user clicks the "Sign up" label

        Parameters
        ----------
        event : Any
            Unused
        """
        # Hide the login window
        self.window_login.withdraw()

        # Create the sign up window
        self.window_signup = tk.Toplevel(master=self.root)

        # Create the layout
        self.frame_signup = login.Signup(master=self.window_signup)

        # Bind the delete window protocol
        self.window_signup.protocol('WM_DELETE_WINDOW', self.wsingup_onclosing)

        # Bind commands
        self.frame_signup.button_signup.configure(command=self.command_wsignup_button_signup)

        # Displaying
        self.frame_signup.pack()

    def wsingup_onclosing(self):
        self.window_signup.destroy()
        self.window_login.destroy()
        self.root.destroy()

    def command_wsignup_button_signup(self):
        """Action taken when user hits the "Sign up" button
        """

        u, p, pc, n = self.frame_signup.var_signup_name.get(),\
                      self.frame_signup.var_signup_password.get(),\
                      self.frame_signup.var_signup_password_confirm.get(),\
                      self.frame_signup.var_signup_name.get()
        
        if p != pc:
            self.frame_signup.var_prompt.set('Unmatched password')
        elif not util.check_username(u):
            self.frame_signup.var_prompt.set('Invalid username')
        else:
            result = self.signup(u, p, n)
            if result is None:
                self.window_signup.destroy()
                self.window_login.deiconify()
                self.frame_login.var_prompt.set('Signed up successfully')

    # Client requests

    def discover_server(self) -> socket.socket:
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
        u.sendto(util.package('discover', '', ''), ('255.255.255.255', self.DISCOVERY_PORT))

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
                t.connect((addr, self.SERVER_PORT))
                return t
            except ConnectionRefusedError:
                return None
        else:
            return None

    def test(self):
        data = ''
        self.send(util.package('test', '', data))
        m = self.receive()
        status_code, status_message, size, data = util.extract(m)
        print(size)
        print(len(data))

    def login(self, username, password):
        """Log in with the given (already checked) username and password

        Parameters
        ----------
        username : str
            
        password : str
            

        Returns
        -------
        tuple
            A tuple of (status_code, status_message) on failure.
        Any
            Return the data expected by the function on success.
        """

        self.send(util.package('login', '', f'{username},{password}'))
        status_code, status_message, _, data = util.extract(self.receive())
        if status_code == '000':
            return data
        else:
            return status_code, status_message
    
    def login_admin(self, username, password):
        """Log in as admin with the given (already checked) username and password

        Parameters
        ----------
        username : str
            
        password : str
            

        Returns
        -------
        tuple
            A tuple of (status_code, status_message) on failure.
        Any
            Return the data expected by the function on success.
        """

        self.send(util.package('login', 'admin', f'{username},{password}'))
        status_code, status_message, _, data = util.extract(self.receive())
        if status_code == '000':
            return data
        else:
            return status_code, status_message

    def signup(self, username, password, name):
        """Sign up with the given (already checked) username, password, name

        Parameters
        ----------
        username : str
            
        password : str
            
        name : str
            

        Returns
        -------
        tuple
            A tuple of (status_code, status_message) on failure.
        None
            Successfully signed up.
        """

        command = 'signup'
        command_type = ''
        data = username + ',' + password + ',' + name

        self.send(util.package(command, command_type, data))
        status_code, status_message, _, _ = util.extract(self.receive())
        if status_code == '000':
            return None
        else:
            return status_code, status_message

    def logout(self):
        command = 'logout'
        command_type = ''
        data = self.username

        self.send(util.package(command, command_type, data))
        status_code, status_message, _, _ = util.extract(self.receive())
        if status_code == '000':
            print('Logged out successfully')
        else:
            print(status_message)
    
    def search(self):
        command = 'query'
        command_type = 'city'
        keyword = input('Enter city name: ')

        self.send(util.package(command, command_type, keyword))
        status_code, status_message, _, data = util.extract(self.receive())

        if status_code == '000':
            num_city, result = data.split('\n', 1)
            print(f'Found {num_city} matches')
            for city in result.splitlines():
                print(city)
        else:
            print(status_message)
    
    def query_weather_by_day(self):
        command = 'query'
        command_type = 'weather'
        day = input('Enter day in YYYY-MM-DD format: ')

        if not util.validate_iso_date_format(day):
            print('Date not in correct format')
            return
        
        self.send(util.package(command, command_type, day))
        status_code, status_message, _, data = util.extract(self.receive())

        if status_code == '000':
            num_city, cities = data.split('\n', 1)
            print(f'Number of cities: {num_city}')
            print(cities)
        else:
            print(status_message)
    
    def forecast(self):
        command = 'query'
        command_type = 'forecast'
        city_id = input('Enter city id: ')

        self.send(util.package(command, command_type, city_id))
        status_code, status_message, _, data = util.extract(self.receive())

        if status_code == '000':
            num_result, weather_info = data.split('\n', 1)
            print(f'Available forecast for {num_result} days')
            for weather in weather_info.splitlines():
                print(weather)
        else:
            print(status_message)

    def add_city(self):
        command = 'update'
        command_type = 'city'

        city_id = input('City ID: ')
        city_name = input('City name: ')
        country_code = input('Country code: ')
        lat = float(input('Latitude: '))
        lon = float(input('Longitude: '))

        data = ','.join([city_id, city_name, country_code, str(lat), str(lon)])
        self.send(util.package(command, command_type, data))
        status_code, status_message, *_ = util.extract(self.receive())
        if status_code == '000':
            print('OK')
        else:
            print(status_message)

    def update_weather(self):
        # city_id = self.search_city()
        # weather_id = local_db.get_weather()
        # day
        # min degree, max degree
        # precipitation
        pass
        
if __name__ == '__main__':
    root = tk.Tk()
    root.title('Client')
    client = Client(root)
    root.withdraw()
    root.mainloop()
