import datetime
import app
import widget
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

        self.frame_weather = widget.WeatherTable(self.root)
        self.frame_weather.pack()
        self.frame_weather.spinbox_day.configure(command=self.command_fweather_spinbox_day)

        self.frame_forecast = widget.Forecast(self.root)
        self.frame_forecast.pack()
        self.frame_forecast.combobox_searchbar.bind('<Return>', self.command_fforecast_combobox_searchbar)
        self.frame_forecast.combobox_searchbar.bind(
            '<<ComboboxSelected>>',
            self.command_fforecast_combobox_searchbar_onselect
        )
    
        
    def create_login_window(self):
        # Create the login window
        self.window_login = tk.Toplevel(master=self.root)

        # Create the layout
        self.frame_login = widget.Login(self.window_login)

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
        self.frame_signup = widget.Signup(master=self.window_signup)

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

    def command_fweather_spinbox_day(self):
        day = self.frame_weather.var_day.get()
        # Transform into ISO format
        temp = datetime.datetime.strptime(day, '%d-%m-%Y')
        day_iso = datetime.date(temp.year, temp.month, temp.day).isoformat()

        # Contact the server
        result = self.query_weather_by_day(day_iso)
        if type(result) is tuple:
            raise Exception(result[1])
        else:
            numcity, cities = result.split('\n', 1)
            if numcity == '0':
                self.frame_weather.place_nodata()
            else:
                self.frame_weather.remove_all()
                self.frame_weather.label_nodata.place_forget()
                for city in cities.splitlines():
                    self.frame_weather.insert(city.split(','))

    def command_fforecast_combobox_searchbar(self, event):
        kw = self.frame_forecast.combobox_searchbar.get()
        if len(kw) < 3:
            return
        result = self.search(kw)
        if type(result) is tuple:
            self.frame_forecast.combobox_searchbar['values'] = ['(No result)']
        else:
            numcity, cities = result.split('\n', 1)
            if numcity == '0':
                self.frame_forecast.combobox_searchbar['values'] = ['(No result)']
            else:
                self.frame_forecast.recent_cities.clear()
                self.frame_forecast.recent_cities = {}

                for city in cities.splitlines():
                    city_id, city_name, country_name = city.split(',', 2)
                    # Value to be put in the combobox
                    v = f'{city_name}, {country_name}'
                    if v in self.frame_forecast.recent_cities:
                        v += ' *'
                    self.frame_forecast.recent_cities[v] = city_id

                self.frame_forecast.combobox_searchbar['values'] = list(self.frame_forecast.recent_cities.keys())
            self.frame_forecast.combobox_searchbar.event_generate('<Button-1>')

    def command_fforecast_combobox_searchbar_onselect(self, event):
        city = self.frame_forecast.combobox_searchbar.get()
        city_id = self.frame_forecast.recent_cities[city]

        result = self.forecast(city_id)
        if type(result) is tuple:
            print(result)
        else:
            num_result, weather_info = result.split('\n', 1)
            if num_result == '0':
                print('0')
            else:
                for d in weather_info:
                    _, city_name, country_name, day, min_degree, max_degree, precipitation = d.split(',')
                    self.frame_forecast.table_forecast.add_entry((day, city_name, country_name, min_degree, max_degree, precipitation))

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
    
    def search(self, keyword):
        command = 'query'
        command_type = 'city'

        self.send(util.package(command, command_type, keyword))
        status_code, status_message, _, data = util.extract(self.receive())

        if status_code == '000':
            # num_city, result = data.split('\n', 1)
            # print(f'Found {num_city} matches')
            # for city in result.splitlines():
            #     print(city)
            return data
        else:
            return status_code, status_message
    
    def query_weather_by_day(self, day):
        """Get weather information of all cities in a given day

        Parameters
        ----------
        day : str
            A day, in YYYY-MM-DD format

        Returns
        -------
        str
            Data expected on success
        tuple
            A 2-tuple of (status_code, status_message) on failure
        """

        command = 'query'
        command_type = 'weather'

        self.send(util.package(command, command_type, day))
        status_code, status_message, _, data = util.extract(self.receive())

        if status_code == '000':
            return data
        else:
            return status_code, status_message
    
    def forecast(self, city_id):
        command = 'query'
        command_type = 'forecast'

        self.send(util.package(command, command_type, city_id))
        status_code, status_message, _, data = util.extract(self.receive())

        if status_code == '000':
            # num_result, weather_info = data.split('\n', 1)
            # print(f'Available forecast for {num_result} days')
            # for weather in weather_info.splitlines():
            #     print(weather)
            return data
        else:
            return status_code, status_message

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
