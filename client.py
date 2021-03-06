import datetime
import socket
import tkinter as tk
from tkinter import messagebox
from ttkbootstrap import Style

import app
import util
import widget

class ClientError(Exception):
    """Generic class for any error handled in client-side
    """
    pass

class Client(app.App):
    def __init__(self, root):
        """Create a new client app

        Parameters
        ----------
        root : tk.Tk
            The root window.

        Raises
        ------
        app.ConnectionError
            Errors in establishing connection to the server.
        """

        super().__init__()

        # The root window
        self.root = root

        # Setting style
        self.style = Style(theme='lumen')

        # User identity
        self.username = ''
        self.name = ''

        # tkinter's events
        self.BUTTON_1 = '<Button-1>'
        self.RETURN = '<Return>'
        self.COMBOBOX_SELECTED = '<<ComboboxSelected>>'

        # Create all the windows and widgets
        self.create_gui()
        self.root.report_callback_exception = self.report_callback_exception

    # ---------- Utility methods ---------

    def report_callback_exception(self, exc, val, tb):
        messagebox.showerror('Error', val)


    # ---------- GUI definition methods ------------

    def create_connect_to_server_window(self):
        # Create toplevel window
        self.w_connecttoserver = tk.Toplevel(self.root)
        self.w_connecttoserver.title('Connect to server')
        self.w_connecttoserver.resizable(False, False)

        # Create the frame
        self.f_connecttoserver = widget.ConnectToServer(self.w_connecttoserver)
        self.f_connecttoserver.pack()

        # Bind commands
        self.w_connecttoserver.protocol('WM_DELETE_WINDOW', self.command_wconnecttoserver_onclosing)
        self.f_connecttoserver.b_connect.configure(command=self.command_wconnecttoserver_bconnect)
        self.f_connecttoserver.l_autoconnect.bind(self.BUTTON_1, self.command_wconnnecttoserver_lautoconnect)

    def create_login_window(self):
        # Create the Login window as toplevel of root
        self.w_login = tk.Toplevel(master=self.root)
        self.w_login.title('Log in')

        # Create the layout
        self.f_login = widget.Login(self.w_login)

        # Bind commands
        self.f_login.b_login.configure(command=self.command_wlogin_blogin)
        self.f_login.l_adminlogin.bind(self.BUTTON_1, self.command_wlogin_ladminlogin)
        self.f_login.l_signup.bind(self.BUTTON_1, self.command_wlogin_lsignup)
        self.w_login.protocol('WM_DELETE_WINDOW', self.command_wlogin_onclosing)

        # Display
        self.f_login.pack()

    def create_signup_window(self):
        # Create the Signup window as a toplevel of root
        self.w_signup = tk.Toplevel(master=self.root)
        self.w_signup.title('Sign up')

        # Create the layout
        self.f_signup = widget.Signup(master=self.w_signup)

        # Bind commands
        self.w_signup.protocol('WM_DELETE_WINDOW', self.command_wsignup_onclosing)
        self.f_signup.b_signup.configure(command=self.command_wsignup_bsignup)
        self.f_signup.l_back.bind(self.BUTTON_1, self.command_wsignup_lback)

        # Display
        self.f_signup.pack()

    def create_main_window(self):
        # The main window has three frames
        
        # -------- The Welcome frame --------
        self.f_welcome = widget.Welcome(self.root)
        self.f_welcome.b_logout.configure(command=self.command_fwelcome_blogout)
        self.f_welcome.b_admintools.configure(command=self.command_fwelcome_badmintools)

        # -------- The Weather frame --------
        self.f_weather = widget.Weather(self.root)
        self.f_weather.s_day.configure(command=self.command_fweather_sday)

        # -------- The Forecast frame --------
        self.f_forecast = widget.Forecast(self.root)
        self.f_forecast.c_searchbar.bind(self.RETURN, self.command_fforecast_csearchbar_onreturn)
        self.f_forecast.c_searchbar.bind(
            self.COMBOBOX_SELECTED,
            self.command_fforecast_csearchbar_onselect
        )
    
        # Griding the frame
        self.f_welcome.grid(row=0, column=0, sticky='nsew')
        self.f_weather.grid(row=1, column=0, sticky='nsew')
        self.f_forecast.grid(row=2, column=0, sticky='nsew')

    def create_admintools_window(self):
        # Create the Admin Tools window as a toplevel window of the main window
        self.w_admintools = tk.Toplevel(self.root)
        self.w_admintools.title('Admin Tools')

        self.w_admintools.rowconfigure(0, weight=1, pad=7)
        self.w_admintools.columnconfigure(0, weight=1, pad=7)

        # Admin Tools window has one frame
        self.f_admintools = widget.AdminTools(self.w_admintools)
        self.f_admintools.rowconfigure(0, weight=1)
        self.f_admintools.rowconfigure(1, weight=1)
        self.f_admintools.columnconfigure(0, weight=1)

        # Bind commands
        self.f_admintools.b_add.configure(command=self.command_wadmintools_badd)
        self.f_admintools.b_update.configure(command=self.command_wadmintools_bupdate)

        # Display
        self.f_admintools.grid(row=0, column=0, sticky='nsew')

    def create_gui(self):
        self.create_connect_to_server_window()

        for i in range(0, 3):
            self.root.rowconfigure(i, pad=7, weight=1)
        self.root.columnconfigure(0, minsize=300, weight=1, pad=7)
        self.create_main_window()


    # ---------- Commands used by widgets ----------

    def command_wconnecttoserver_bconnect(self):
        server_address = self.f_connecttoserver.v_address.get()
        self.main_socket = self.connect(server_address)
        self.w_connecttoserver.destroy()
        self.create_login_window()

    def command_wconnnecttoserver_lautoconnect(self, event):
        self.main_socket = self.auto_connect()
        self.w_connecttoserver.destroy()
        self.create_login_window()

    def command_wconnecttoserver_onclosing(self):
        self.w_connecttoserver.destroy()
        self.root.destroy()

    def command_wlogin_onclosing(self):
        """Actions taken when closing the Login window
        """

        self.w_login.destroy()
        self.root.destroy()

    def command_wlogin_blogin(self):
        """Actions taken when hitting the "Login" button in the login window
        """

        u, p = self.f_login.v_username.get(), self.f_login.v_password.get()

        if len(p) == 0 or len(u) == 0:
            self.f_login.v_prompt.set('Username and password must not be empty')
        else:
            if self.f_login.login_type == 'ordinary':
                if util.check_username(u) is False:
                    self.f_login.v_prompt.set('Invalid username')
                    return
            else:
                if not u.isnumeric():
                    self.f_login.v_prompt.set('Not admin')
                    return

        # Log in according to the login type
        result = self.log_in(u, p) if self.f_login.login_type == 'ordinary' else self.log_in_as_admin(u, p)

        # On failure
        if type(result) is tuple:
            # Prompt the status message
            self.f_login.v_prompt.set(result[1])
            return
        
        self.username, self.name = result.split(',', 1)
        self.f_welcome.v_name.set(self.name)

        # Display or undisplay Admin Tools button
        if self.f_login.login_type == 'ordinary':
            self.f_welcome.b_admintools.grid_remove()
        else:
            self.f_welcome.b_admintools.grid()
        
        self.w_login.destroy()
        self.root.deiconify()

    def command_wlogin_ladminlogin(self, event):
        """Actions taken when hitting the "Log in as admin" label

        Parameters
        ----------
        event : Any
            Unused
        """

        if self.f_login.login_type == 'ordinary':
            self.f_login.v_logintype.set('Log in as admin')
            self.f_login.login_type = 'admin'
            self.f_login.l_adminlogin.configure(text='Log in as ordinary user')
        else:
            self.f_login.v_logintype.set('Log in')
            self.f_login.login_type = 'ordinary'
            self.f_login.l_adminlogin.configure(text='Log in as admin')

    def command_wlogin_lsignup(self, event):
        """Action taken when hitting the "Sign up" label

        Parameters
        ----------
        event : Any
            Unused
        """
        
        self.w_login.withdraw()
        self.create_signup_window()

    def command_wsignup_onclosing(self):
        """Actions taken when closing the Sign up window
        """

        # Exit the program anyway
        self.w_signup.destroy()
        self.w_login.destroy()
        self.root.destroy()

    def command_wsignup_bsignup(self):
        """Actions taken when hitting the "Sign up" button
        """

        u, p, pc, n = self.f_signup.v_username.get(),\
                      self.f_signup.v_password.get(),\
                      self.f_signup.v_passwordconfirm.get(),\
                      self.f_signup.v_name.get()
        
        if p != pc:
            self.f_signup.v_prompt.set('Unmatched password')
        elif not util.check_username(u):
            self.f_signup.v_prompt.set('Invalid username')
        elif not util.is_alnum_with_space(n):
            self.f_signup.v_prompt.set('Invalid name')
        else:
            result = self.sign_up(u, p, n)
            if result is None:
                self.w_signup.destroy()
                self.w_login.deiconify()
                self.f_login.v_prompt.set('Signed up successfully')

    def command_wsignup_lback(self, event):
        """Actions taken when hitting the "Back" label in the Sign up window

        Parameters
        ----------
        event : Any
            Unused
        """

        # Go back to the Login window
        self.w_signup.destroy()
        self.create_login_window()

    def command_fwelcome_blogout(self):
        """Actions taken when hitting the Logout button in the main window
        """

        result = self.log_out()
        if type(result) is tuple:
            raise ClientError(f'{result[1]}.\nError code: {result[0]}')
        else:
            self.root.withdraw()
            self.create_login_window()

    def command_fwelcome_badmintools(self):
        """Actions taken when hitting the Admin Tools button in the main window
        """

        self.create_admintools_window()

    def command_wadmintools_badd(self):
        """Actions taken when hitting the Add button in the Admin Tools window
        """

        a = self.f_admintools

        city_id, city_name, country_code, lat, lon = a.e_cityid1.get(),\
                                                     a.e_cityname.get(),\
                                                     a.e_country.get(),\
                                                     a.e_lat.get(),\
                                                     a.e_lon.get()

        if not util.is_alnum_with_space(city_name)\
           or not city_id.isdecimal()\
           or len(country_code) != 2\
           or not country_code.isalpha()\
           or not util.isfloat(lat)\
           or not util.isfloat(lon):
            a.v_status.set('Error')
        else:
            r = self.add_city(city_id, city_name, country_code, lat, lon)
            if r is None:
                a.v_status.set('Success')
            else:
                a.v_status.set(r[1])

    def command_wadmintools_bupdate(self):
        """Actions taken when hitting the Update button in the Admin Tools window
        """

        amt = self.f_admintools
        c, d, w, mind, maxd, pre = amt.e_cityid2.get(),\
                                   amt.e_date.get(),\
                                   amt.e_weather.get(),\
                                   amt.e_mindegree.get(),\
                                   amt.e_maxdegree.get(),\
                                   amt.e_precipitation.get()

        if not c.isdecimal() or\
           not util.validate_iso_date_format(d) or\
           not w.isdecimal() or\
           not (util.isfloat(mind) and float(mind) > -273.15) or\
           not (util.isfloat(maxd) and float(maxd) >= float(mind)) or\
           not (util.isfloat(pre) and float(pre) >= 0 and float(pre) <= 1):
            amt.v_status.set('Error')
        else:
            result = self.update_weather(c, d, w, mind, maxd, pre)
            if result is None:
                amt.v_status.set('Success')
            else:
                amt.v_status.set(result[1])

    def command_fweather_sday(self):
        """Actions taken when hitting the Date spinbox in the Weather frame

        Raises
        ------
        Exception
            [description]
        """

        date = self.f_weather.v_date.get()
        # Transform into ISO format
        temp = datetime.datetime.strptime(date, '%d-%m-%Y')
        day_iso = datetime.date(temp.year, temp.month, temp.day).isoformat()

        # Contact the server
        result = self.query_weather_by_date(day_iso)
        if type(result) is tuple:
            raise ClientError(f'{result[1]}.\nError code: {result[0]}')
        else:
            self.f_weather.t_weather.remove_all()
            numcity, cities = result.split('\n', 1)
            if numcity == '0':
                self.f_weather.t_weather.add_row(('No data',))
            else:
                for city in cities.splitlines():
                    _, city_name, country, _, weather_description, min_degree, max_degree, precipitation = city.split(',')
                    self.f_weather.t_weather.add_row((city_name, country, weather_description, min_degree, max_degree, precipitation))

    def command_fforecast_csearchbar_onreturn(self, event):
        """Actions taken when hitting return in the Search combobox in the Forecast frame

        Parameters
        ----------
        event : Any
            Unused
        """

        kw = self.f_forecast.c_searchbar.get()
        if len(kw) < 3:
            return
        
        result = self.search_city(kw)
        if type(result) is tuple:
            self.f_forecast.c_searchbar['values'] = ['(No result)']
        else:
            numcity, cities = result.split('\n', 1)
            if numcity == '0':
                self.f_forecast.c_searchbar['values'] = ['(No result)']
            else:
                self.f_forecast.recent_cities.clear()
                self.f_forecast.recent_cities = {}

                for city in cities.splitlines():
                    city_id, city_name, country_name = city.split(',', 2)
                    # Value to be put in the combobox
                    v = f'{city_name}, {country_name}'
                    if v in self.f_forecast.recent_cities:
                        v += ' *'
                    self.f_forecast.recent_cities[v] = city_id

                self.f_forecast.c_searchbar['values'] = list(self.f_forecast.recent_cities.keys())
            self.f_forecast.c_searchbar.event_generate(self.BUTTON_1)

    def command_fforecast_csearchbar_onselect(self, event):
        """Actions taken when selecting an option in the dropdown list of the Search combobox
        (in the Forecast frame)

        Parameters
        ----------
        event : Any
            Unused
        """

        city = self.f_forecast.c_searchbar.get()
        city_id = self.f_forecast.recent_cities[city]

        result = self.forecast(city_id)
        if type(result) is tuple:
            raise ClientError(f'{result[1]}.\nError code: {result[0]}')
        else:
            num_result, weather_info = result.split('\n', 1)
            if num_result == '0':
                self.f_forecast.t_forecast.add_row(('No data',))
            else:
                for d in weather_info.splitlines():
                    _, _, _, day, weather_description, min_degree, max_degree, precipitation = d.split(',')
                    self.f_forecast.t_forecast.add_row((day, weather_description, min_degree, max_degree, precipitation))


    # ---------- Methods to make requests to the server ----------

    def connect(self, server_address):
        """Attempt to establish a TCP connnection to the server at server_address

        Parameters
        ----------
        server_address : str
            The address of the server

        Returns
        -------
        socket.socket
            New socket that can be used to communicate with the server

        Raises
        ------
        app.ConnectionError
        """

        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(5.0)
            s.connect((server_address, self.SERVER_PORT))

            s.send(util.package('connect', '', ''))
            status_code, status_message, _, _ = util.extract(self.receive_from(s))
            if status_code != '000':
                s.close()
                raise app.ConnectionError(status_message)
            return s
        except ConnectionRefusedError:
            s.close()
            raise app.ConnectionError('Cannot connect to this address. Connection refused.')
        except OSError as e:
            s.close()
            raise app.ConnectionError(f'Network error.\nError: {e}')
        except socket.timeout:
            s.close()
            raise app.ConnectionError('Connection timed out.')
        except app.ConnectionError:
            s.close()
            raise
        except Exception:
            s.close()
            raise app.ConnectionError('Unknown error.')

    def auto_connect(self) -> socket.socket:
        """Find and attempt establishing a connection to the server in the same network.
        
        Returns
        -------
        socket.socket
            A TCP socket connected to the server

        Raises
        ------
        app.ConnectionError


        This function is inspired by the ARP protocol. It attempts to automate the task of connecting
        to the server, without having to explicitly input the server address. To find the server, the client
        first broadcasts a "discovery" message into the network using UDP on port DISCOVERY_PORT.
        The server, if listening, responses to the client a "discovery acknowledgement" message, along with its
        IP address. The client can then use this address to establish a TCP connection to the server.
        """

        # Create an UDP socket
        u = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        u.settimeout(5.0)

        # Broadcast the discovery message
        try:
            u.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            u.sendto(util.package('discover', '', ''), ('255.255.255.255', self.DISCOVERY_PORT))
        except OSError:
            raise app.ConnectionError('No connection')

        # Receive the acknowledgement message from the server
        try:
            message, _ = u.recvfrom(1024)
        except socket.timeout:
            raise app.ConnectionError('Connection timed out.')

        # Extract the acknowledgement message
        try:
            e, _, _, addr = util.extract(message)
        except Exception:
            # Catch exception here because we are broadcasting, there might be other broadcast
            # messages that intefere with our protocol.
            raise app.ConnectionError('Unknown error')
        u.close()

        if e == '000':
            return self.connect(addr)
        raise app.ConnectionError('Unknown error')

    def test(self):
        data = ''
        self.send(util.package('test', '', data))
        m = self.receive()
        status_code, status_message, size, data = util.extract(m)
        print(size)
        print(len(data))

    def log_in(self, username, password):
        """Log in with the given (already checked) username and password

        Parameters
        ----------
        username : str
            
        password : str
            

        Returns
        -------
        tuple
            A tuple of (status_code, status_message) on failure.
        str
            A formatted string of {username},{name} on success.
        """

        self.send(util.package('login', '', f'{username},{password}'))
        status_code, status_message, _, data = util.extract(self.receive())
        if status_code == '000':
            return data
        else:
            return status_code, status_message
    
    def log_in_as_admin(self, username, password):
        """Log in as admin with the given (already checked) username and password

        Parameters
        ----------
        username : str
            
        password : str
            

        Returns
        -------
        tuple
            A tuple of (status_code, status_message) on failure.
        str
            A formatted string of {username},{name} on success.
        """

        self.send(util.package('login', 'admin', f'{username},{password}'))
        status_code, status_message, _, data = util.extract(self.receive())
        if status_code == '000':
            return data
        else:
            return status_code, status_message

    def sign_up(self, username, password, name):
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
            On success.
        """

        command = 'signup'
        command_type = ''
        data = ','.join([name, username, password])

        self.send(util.package(command, command_type, data))
        status_code, status_message, _, _ = util.extract(self.receive())
        if status_code == '000':
            return None
        else:
            return status_code, status_message

    def log_out(self):
        """Log out

        Returns
        -------
        tuple
            A tuple of (status_code, status_message) on failure (yes, logging out can fail too).
        None
            On success.
        """

        command = 'logout'
        command_type = ''
        data = self.username

        self.send(util.package(command, command_type, data))
        status_code, status_message, _, _ = util.extract(self.receive())
        if status_code == '000':
            return None
        else:
            return status_code, status_message
    
    def search_city(self, keyword):
        """Search a list of cities with a given keyword

        Parameters
        ----------
        keyword : str

        Returns
        -------
        tuple
            A tuple of (status_code, status_message) on failure.
        str
           A string, containing multiple lines on success.
        """

        command = 'query'
        command_type = 'city'

        self.send(util.package(command, command_type, keyword))
        status_code, status_message, _, data = util.extract(self.receive())

        if status_code == '000':
            return data
        else:
            return status_code, status_message
    
    def query_weather_by_date(self, date):
        """Get weather information of all cities in a given date

        Parameters
        ----------
        day : str
            A date, in YYYY-MM-DD format.

        Returns
        -------
        tuple
            A tuple of (status_code, status_message) on failure.
        str
            Data expected on success.
        """

        command = 'query'
        command_type = 'weather'

        self.send(util.package(command, command_type, date))
        status_code, status_message, _, data = util.extract(self.receive())

        if status_code == '000':
            return data
        else:
            return status_code, status_message
    
    def forecast(self, city_id):
        """Obtain the 7-day weather forecast information of a given city with ID city_id

        Parameters
        ----------
        city_id : int

        Returns
        -------
        tuple
            A tuple of (status_code, status_message) on failure.
        str
        """
        command = 'query'
        command_type = 'forecast'

        self.send(util.package(command, command_type, city_id))
        status_code, status_message, _, data = util.extract(self.receive())

        if status_code == '000':
            return data
        else:
            return status_code, status_message

    def add_city(self, city_id, city_name, country_code, lat, lon):
        """Add a new city with given information (all of them are required)

        Parameters
        ----------
        city_id : int
            The ID of the city
        city_name : str
            The name of the city
        country_code : str
            A 2-letter string representing a country
        lat : float
            The latitude of the city
        lon : float
            The longitude of the city

        Returns
        -------
        tuple
            A tuple of (status_code, status_message) on failure.
        None
            On success.
        """

        command = 'update'
        command_type = 'city'

        data = ','.join([city_id, city_name, country_code, str(lat), str(lon)])
        self.send(util.package(command, command_type, data))
        status_code, status_message, *_ = util.extract(self.receive())
        if status_code == '000':
            return None
        else:
            return status_code, status_message

    def update_weather(self, city_id, date, weather_id, min_degree, max_degree, precipitation):
        """Add or update weather record of a city in a given date

        Parameters
        ----------
        city_id : int
            The ID of the city
        date : str
            In YYYY-MM-DD format
        weather_id : int
            
        min_degree : float
            A number greater than -273.15
        max_degree : float
            A number greater than or equal min_degree
        precipitation : float
            A number between 0 and 1

        Returns
        -------
        tuple
            A tuple of (status_code, status_message) on failure.
        None
            On success.
        """

        command = 'update'
        command_type = 'weather'
        data = ','.join([city_id, date, weather_id, min_degree, max_degree, precipitation])

        self.send(util.package(command, command_type, data))
        status_code, status_message, *_ = util.extract(self.receive())

        if status_code == '000':
            return None
        return status_code, status_message
        
if __name__ == '__main__':
    try:
        root = tk.Tk()
        root.title('Client')
        client = Client(root)
        root.withdraw()
        root.mainloop()
    except Exception as e:
        root.withdraw()
        messagebox.showerror('Error', e)
