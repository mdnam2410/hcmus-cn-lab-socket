"""Client and server widgets
"""

import datetime
import threading
import tkinter as tk
import tkinter.font
import tkinter.ttk as ttk
from ttkbootstrap import Style

BOLD14 = {'font': 'Helvetica 14 bold'}
BOLD12 = {'font': 'Helvetica 12 bold'}

# ------------ Client widgets ------------

class ConnectToServer(ttk.Frame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.master = master

        self.l_connect = ttk.Label(self, text='Server address')
        self.v_address = tk.StringVar()
        self.e_address = ttk.Entry(self, textvariable=self.v_address, width=35)
        self.b_connect = ttk.Button(self, text='Connect')
        self.l_autoconnect = ttk.Label(self, text='Connect automatically', style='info.TLabel')

        self.display()

    def display(self):
        for i in range(0, 3):
            self.rowconfigure(i, pad=7)
        self.columnconfigure(1, weight=1, minsize=80, pad=7)
        
        self.l_connect.grid(row=0, column=0, sticky='w')
        self.e_address.grid(row=0, column=1)
        self.b_connect.grid(row=1, column=1)
        self.l_autoconnect.grid(row=2, column=0, columnspan=2)


class Login(ttk.Frame):
    """Define the layout of the Login
    """

    def __init__(self, master):
        super().__init__(master)
        self.master = master
        self.login_type = 'ordinary'

        # Username and password entry
        self.v_username = tk.StringVar()
        self.e_username = ttk.Entry(self, textvariable=self.v_username, width=35)
        self.v_password = tk.StringVar()
        self.e_password = ttk.Entry(self, textvariable=self.v_password, show='*', width=35)

        # Label to display message
        self.v_prompt = tk.StringVar()
        self.l_prompt = ttk.Label(self, textvariable=self.v_prompt, style='danger.TLabel')

        # Login button
        self.v_logintype = tk.StringVar(value='Log in')
        self.b_login = ttk.Button(self, textvariable=self.v_logintype)

        # Alternative options
        self.l_signup = ttk.Label(self, text='Sign up', style='info.TLabel')
        self.l_adminlogin = ttk.Label(self, text='Log in as admin', style='info.TLabel')

        self.display()

    def display(self):
        """Define the layout of the widgets
        """
        
        for i in range(0, 5):
            self.rowconfigure(i, pad=7)
        for j in range(0, 2):
            self.columnconfigure(j, pad=7)
        self.rowconfigure(2, pad=2)

        ttk.Label(master=self, text='Username').grid(row=0, column=0, sticky='w')
        self.e_username.grid(row=0, column=1)
        ttk.Label(master=self, text='Password').grid(row=1, column=0, sticky='w')
        self.e_password.grid(row=1, column=1)
        self.l_prompt.grid(row=2, column=1)
        self.b_login.grid(row=3, column=1)

        self.l_signup.grid(row=4, column=0)
        self.l_adminlogin.grid(row=4, column=1)
        

class Signup(ttk.Frame):
    """Define the layout of the Signup window
    """

    def __init__(self, master):
        super().__init__(master)
        self.master = master

        # Text variables
        self.v_username = tk.StringVar()
        self.v_password = tk.StringVar()
        self.v_passwordconfirm = tk.StringVar()
        self.v_name = tk.StringVar()
        self.v_prompt = tk.StringVar()

        # Entries
        self.e_username = ttk.Entry(self, textvariable=self.v_username)
        self.e_password = ttk.Entry(self, textvariable=self.v_password, show='*')
        self.e_passwordconfirm = ttk.Entry(self, textvariable=self.v_passwordconfirm, show='*')
        self.e_name = ttk.Entry(self, textvariable=self.v_name)

        # Sign up button
        self.b_signup = ttk.Button(self, text='Sign up')

        # Back label
        self.l_back = ttk.Label(self, text='Back', style='info.TLabel')

        self.display()

    def display(self):
        for i in range(0, 6):
            self.rowconfigure(i, pad=7)
        for j in range(0, 2):
            self.columnconfigure(j, pad=7)
        self.rowconfigure(4, pad=2)

        ttk.Label(self, text='Username').grid(row=0, column=0, sticky='w')
        self.e_username.grid(row=0, column=1)
        ttk.Label(self, text='Password').grid(row=1, column=0, sticky='w')
        self.e_password.grid(row=1, column=1)
        ttk.Label(self, text='Confirm password').grid(row=2, column=0, sticky='w')
        self.e_passwordconfirm.grid(row=2, column=1)
        ttk.Label(self, text='Name').grid(row=3, column=0, sticky='w')
        self.e_name.grid(row=3, column=1)
        ttk.Label(self, textvariable=self.v_prompt, foreground='red').grid(row=4, column=1)
        self.l_back.grid(row=5, column=0, sticky='w')
        self.b_signup.grid(row=5, column=1)


class Welcome(ttk.Frame):
    """Define the layout of the Welcome frame in the main window
    """

    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.master = master

        # Labels
        self.l_welcome = ttk.Label(self, text='Welcome,', style='secondary.TLabel')
        self.v_name = tk.StringVar(value='name')
        self.l_name = ttk.Label(self, textvariable=self.v_name, **BOLD14)

        # Buttons
        self.b_logout = ttk.Button(self, text='Log out')
        self.b_admintools = ttk.Button(self, text='Admin tools')

        self.display()
    
    def display(self):
        for i in range(0, 2):
            self.rowconfigure(i, pad=7)
        self.columnconfigure(0, pad=7, weight=1, minsize=40)
        self.l_welcome.grid(row=0, column=0, sticky='w')
        self.l_name.grid(row=1, column=0, sticky='w')
        self.b_admintools.grid(row=0, column=1, rowspan=2)
        self.b_logout.grid(row=0, column=2, rowspan=2)


class Table(ttk.Treeview):
    """Convenience class that defines the layout and implements necessary operations of a table
    using tkinter.Treeview
    """

    def __init__(self, master, headings, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.master = master
        self.headings = headings

        self['columns'] = ['#' + str(x) for x in range(1, len(headings) + 1)]
        self['show'] = 'headings'

        self.s = ttk.Style(self)
        self.f = tkinter.font.Font(self, font=self.s.lookup(self['style'], 'font'), weight='bold')
        self.max_column_widths = [0] * len(self.headings)

        # Show headings
        for i, t in enumerate(self.headings):
            self.heading('#' + str(i + 1), text=t)
            self.max_column_widths[i] = self.f.measure(self.heading('#' + str(i + 1), 'text'))
            self.column('#' + str(i + 1), width=self.max_column_widths[i] + 12)
        
        self.iid = -1

    def auto_resize(self):
        for i, t in enumerate(self.headings):
            x = len(t)
            self.column('#' + str(i + 1), width=10 * x + 8)

    
    def add_row(self, values):
        """Add a new row at the bottom of the table

        Parameters
        ----------
        values : tuple
            A tuple of strings of cells in the row.
        """

        self.iid += 1
        self.insert('', 'end', self.iid, values=values)
        for i, t in enumerate(values):
            col_id = '#' + str(i + 1)
            x = self.f.measure(t)
            if x > self.max_column_widths[i]:
                self.max_column_widths[i] = x
                self.column(col_id, width=x + 12)

    def remove_all(self):
        """Empty the table
        """

        while self.iid != -1:
            self.delete(self.iid)
            self.iid -= 1


class Weather(ttk.Frame):
    """Defines the layout of the Weather frame in the main window
    """

    def __init__(self, master):
        super().__init__(master)
        self.master = master

        # Label
        self.l_weather = ttk.Label(self, text='Weather', **BOLD14)

        # Day spinbox
        self.today = datetime.date.today()
        self.date_range = [(self.today + datetime.timedelta(i)).strftime('%d-%m-%Y') for i in range(-6, 1)]
        self.v_date = tk.StringVar()
        self.s_day = ttk.Spinbox(self,
            textvariable=self.v_date,
            values=self.date_range,
        )

        # Weather table
        self.HEADINGS = ['City', 'Country', 'Weather', 'Min degree', 'Max degree', 'Precipitation']
        self.t_weather = Table(self, self.HEADINGS)

        self.display()

    def display(self):
        self.columnconfigure(0, weight=1, pad=7)

        self.l_weather.grid(row=0, column=0, sticky='w')
        ttk.Label(self, text='Day').grid(row=0, column=1, sticky='e')
        self.s_day.grid(row=0, column=2)
        self.t_weather.grid(row=1, column=0, columnspan=3, sticky='nsew')


class Forecast(ttk.Frame):
    """Define the layout of the Forecast frame in the main window
    """

    def __init__(self, master):
        super().__init__(master)
        self.master = master

        # Hold the result of the last city search. A dict mapping from "city_name, country_name" to city_id
        self.recent_cities = {}

        # Label
        self.l_forecast = ttk.Label(master=self, text='Forecast', **BOLD14)

        # Search bar
        self.v_searchkeyword = tk.StringVar()
        self.c_searchbar = ttk.Combobox(master=self, textvariable=self.v_searchkeyword)
        
        # Forecast table
        self.HEADINGS = ['Day', 'Weather', 'Min degree', 'Max degree', 'Precipitation']
        self.t_forecast = Table(master=self, headings=self.HEADINGS)

        self.display()

    def display(self):
        self.columnconfigure(0, weight=1, pad=7)
        self.l_forecast.grid(row=0, column=0, sticky='w')
        ttk.Label(self, text='Search city').grid(row=0, column=1, sticky='e')
        self.c_searchbar.grid(row=0, column=2)
        self.t_forecast.grid(row=1, column=0, columnspan=3, sticky='nsew')
        self.t_forecast.auto_resize()


class AdminTools(ttk.Frame):
    """Define the layout of the Admin Tools window
    """

    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.master = master

        # The Admin Tools frame contains two smaller frames
        self.f_addcity = tk.LabelFrame(self, text='Add city', **BOLD12)
        self.f_editweather = tk.LabelFrame(self, text='Edit weather information', **BOLD12)

        # ---------- Add City frame's widgets ----------
        # Entries
        self.e_cityid1 = ttk.Entry(self.f_addcity, width=35)
        self.e_cityname = ttk.Entry(self.f_addcity, width=35)
        self.e_country = ttk.Entry(self.f_addcity, width=35)
        self.e_lat = ttk.Entry(self.f_addcity, width=35)
        self.e_lon = ttk.Entry(self.f_addcity, width=35)

        # Buttons
        self.b_add = ttk.Button(self.f_addcity, text='Add')
        

        # ----------- Edit Weather frame's widgets ----------
        # Entries
        self.e_cityid2 = ttk.Entry(self.f_editweather, width=35)
        self.e_date = ttk.Entry(self.f_editweather, width=35)
        self.e_weather = ttk.Entry(self.f_editweather, width=35)
        self.e_mindegree = ttk.Entry(self.f_editweather, width=35)
        self.e_maxdegree = ttk.Entry(self.f_editweather, width=35)
        self.e_precipitation = ttk.Entry(self.f_editweather, width=35)

        # Buttons
        self.b_update = ttk.Button(self.f_editweather, text='Update')

        # ---------- Common label for displaying command's status ----------
        self.v_status = tk.StringVar()
        self.l_status = ttk.Label(self, textvariable=self.v_status)

        self.display()

    def display(self):
        self.rowconfigure(0, weight=1, pad=7)
        self.rowconfigure(1, weight=1, pad=7)
        self.columnconfigure(0, weight=1, pad=7)

        self.f_addcity.grid(row=0, column=0, sticky='nsew')
        self.f_editweather.grid(row=1, column=0, sticky='nsew')
        self.l_status.grid(row=2, column=0, sticky='w')

        # ----------- Add city -----------
        for i in range(0, 6):
            self.f_addcity.rowconfigure(i, pad=7)
        
        self.f_addcity.columnconfigure(0, pad=7)
        self.f_addcity.columnconfigure(1, weight=1, pad=7, minsize=100)

        labels1 = ['City ID', 'City name', 'Country code', 'Latitude', 'Longitude']
        addcity_entries = [
            self.e_cityid1, self.e_cityname, self.e_country, self.e_lat, self.e_lon
        ]
        for i in range(0, len(labels1)):
            ttk.Label(self.f_addcity, text=labels1[i]).grid(row=i, column=0, sticky='w')
            addcity_entries[i].grid(row=i, column=1, sticky='nsew')
        
        self.b_add.grid(row=5, column=1, sticky='e')
        
        # ----------- Edit weather ----------
        for i in range(0, 7):
            self.f_editweather.rowconfigure(i, pad=7)
        
        self.f_editweather.columnconfigure(0, pad=7)
        self.f_editweather.columnconfigure(1, weight=1, pad=7, minsize=100)

        labels2 = ['City ID', 'Date (YYYY-MM-DD)', 'Weather ID', 'Min degree', 'Max degree', 'Precipitation']
        editweather_entries = [
            self.e_cityid2, self.e_date, self.e_weather,
            self.e_mindegree, self.e_maxdegree, self.e_precipitation
        ]
        for i in range(0, len(labels2)):
            ttk.Label(self.f_editweather, text=labels2[i]).grid(row=i, column=0, sticky='w')
            editweather_entries[i].grid(row=i, column=1, sticky='nsew')
        self.b_update.grid(row=6, column=1, sticky='e')


# ------------- Server widgets ------------

class UserActivities(ttk.Frame):
    """Define the layout of the User Activities frame in the server main window
    """

    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.master = master

        # Title
        self.l_activeusers = ttk.Label(self, text='User Activities', **BOLD14)

        # Table
        self.HEADINGS = ['Client', 'Activity Type', 'Time']
        self.t_activities = Table(self, self.HEADINGS, height=5)

        self.display()

    def display(self):
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        self.l_activeusers.grid(row=0, column=0, sticky='w')
        self.t_activities.grid(row=1, column=0, sticky='nsew')


class Statistics(ttk.Frame):
    """Define the layout of the Statistics frame in the server main window
    """

    def __init__(self, master, **kwargs):
        super().__init__(master)
        self.master = master

        self.v_totalconnections = tk.IntVar(value=0)
        self.v_activeusers = tk.IntVar(value=0)
        self.v_requestsmade = tk.IntVar(value=0)

        self.l_totalconnections = ttk.Label(self, textvariable=self.v_totalconnections, **BOLD12)
        self.l_activeusers = ttk.Label(self, textvariable=self.v_activeusers, **BOLD12)
        self.l_requestsmade = ttk.Label(self, textvariable=self.v_requestsmade, **BOLD12)

        self.display()

    def inc_totalconnections(self):
        self.v_totalconnections.set(self.v_totalconnections.get() + 1)

    def dec_totalconnections(self):
        self.v_totalconnections.set(self.v_totalconnections.get() - 1)

    def inc_activeusers(self):
        self.v_activeusers.set(self.v_activeusers.get() + 1)

    def dec_activeusers(self):
        self.v_activeusers.set(self.v_activeusers.get() - 1)

    def inc_requestsmade(self):
        self.v_requestsmade.set(self.v_requestsmade.get() + 1)

    def dec_requestsmade(self):
        self.v_requestsmade.set(self.v_requestsmade.get() - 1)

    def display(self):
        for i in range(0, 2):
            self.columnconfigure(i, weight=1)

        ttk.Label(self, text='Total Connections').grid(row=0, column=0, columnspan=2)
        self.l_totalconnections.grid(row=1, column=0, columnspan=2)
        ttk.Label(self, text='Active Users').grid(row=2, column=0)
        self.l_activeusers.grid(row=3, column=0)
        ttk.Label(self, text='Requests Made').grid(row=2, column=1)
        self.l_requestsmade.grid(row=3, column=1)


class ServerWindow(threading.Thread):
    """The class represent the main UI of the server (need to inherit from Thread due to
    the multithreaded nature in the Server class)
    """

    def __init__(self, callback):
        """Create the thread

        Parameters
        ----------
        callback : function
            Callback function used when exiting the main window
        """
        
        super().__init__()
        self.callback = callback

    def run(self):
        self.root = tk.Tk()
        self.root.title('Server')
        self.root.geometry('500x300')
        self.root.protocol('WM_DELETE_WINDOW', self.callback)

        self.style = Style(theme='lumen')

        self.root.rowconfigure(0, weight=1)
        self.root.rowconfigure(1, weight=1)
        self.root.columnconfigure(0, weight=1)

        self.f_useractivities = UserActivities(self.root)
        self.f_stat = Statistics(self.root)

        self.f_useractivities.grid(row=0, column=0, sticky='nsew')
        self.f_stat.grid(row=1, column=0, sticky='nsew')
        self.root.mainloop()

if __name__ == '__main__':
    root = tk.Tk()
    c = ConnectToServer(root)
    c.pack()
    root.mainloop()

    