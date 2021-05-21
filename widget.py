"""Client and server widgets
"""

import datetime
import tkinter as tk
import tkinter.ttk as ttk

class Login(ttk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.master = master
        self.login_option = 'ordinary'

        # Username and password entry
        self.var_username = tk.StringVar()
        self.entry_username = ttk.Entry(self, textvariable=self.var_username)
        self.var_password = tk.StringVar()
        self.entry_password = ttk.Entry(self, textvariable=self.var_password)

        # Label to display message
        self.var_prompt = tk.StringVar()
        self.label_prompt = ttk.Label(self, textvariable=self.var_prompt, foreground='red')

        # Login button
        self.var_login_button_text = tk.StringVar(value='Log in')
        self.button_login = ttk.Button(self, textvariable=self.var_login_button_text)

        # Alternative options
        self.label_signup = ttk.Label(self, text='Sign up', underline=1)
        self.label_adminlogin = ttk.Label(self, text='Log in as admin', underline=1)

        # Display
        ttk.Label(master=self, text='Username').pack(anchor=tk.W)
        self.entry_username.pack()
        ttk.Label(master=self, text='Password').pack(anchor=tk.W)
        self.entry_password.pack()
        self.label_prompt.pack()
        self.button_login.pack()

        self.label_signup.pack()
        self.label_adminlogin.pack()


class Signup(ttk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.master = master

        # Text variables
        self.var_signup_username = tk.StringVar()
        self.var_signup_password = tk.StringVar()
        self.var_signup_password_confirm = tk.StringVar()
        self.var_signup_name = tk.StringVar()
        self.var_prompt = tk.StringVar()

        # Entries
        self.entry_signup_username = ttk.Entry(self, textvariable=self.var_signup_username)
        self.entry_signup_password = ttk.Entry(self, textvariable=self.var_signup_password)
        self.entry_signup_password_confirm = ttk.Entry(self, textvariable=self.var_signup_password_confirm)
        self.entry_signup_name = ttk.Entry(self, textvariable=self.var_signup_name)

        # Sign up button
        self.button_signup = ttk.Button(self, text='Sign up')

        # Displaying
        ttk.Label(self, text='Username').pack()
        self.entry_signup_username.pack()
        ttk.Label(self, text='Password').pack()
        self.entry_signup_password.pack()
        ttk.Label(self, text='Confirm password').pack()
        self.entry_signup_password_confirm.pack()
        ttk.Label(self, text='Name').pack()
        self.entry_signup_name.pack()
        ttk.Label(self, textvariable=self.var_prompt, foreground='red').pack()
        self.button_signup.pack()

class Table(ttk.Treeview):
    def __init__(self, master, headings, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.master = master
        self.headings = headings

        self['columns'] = ['#' + str(x) for x in range(1, len(headings) + 1)]
        self['show'] = 'headings'

        # Show headings
        for i, t in enumerate(self.headings):
            self.heading('#' + str(i + 1), text=t)

        self.iid = -1
    
    def add_entry(self, values):
        self.iid += 1
        self.insert('', 'end', self.iid, values=values)

    def remove_all(self):
        while self.iid != -1:
            self.delete(self.iid)
            self.iid -= 1



class WeatherTable(ttk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.master = master

        # Label
        self.label_weather = ttk.Label(self, text='Weather')

        # Day spinbox
        self.today = datetime.date.today()
        self.day_range = [(self.today + datetime.timedelta(i)).strftime('%d-%m-%Y') for i in range(-6, 1)]
        self.var_day = tk.StringVar()
        self.spinbox_day = ttk.Spinbox(self,
            textvariable=self.var_day,
            values=self.day_range,
        )

        # Weather table
        self.HEADINGS = ['City', 'Country', 'Weather', 'Min degree', 'Max degree', 'Precipitation']
        self.table_weather = ttk.Treeview(
            master=self,
            height=10,
            columns=['#' + str(x) for x in range(1, len(self.HEADINGS) + 1)],
            show='headings'
        )

        for i, t in enumerate(self.HEADINGS):
            self.table_weather.heading('#' + str(i + 1), text=t)
        
        self.iid = -1

        # Display
        self.label_weather.pack()
        self.spinbox_day.pack()
        self.table_weather.pack()
    
    def place_nodata(self):
        if self.iid == -1:
            self.insert(('No data',))
    
    def insert(self, values):
        """Insert a new weather information at the end of the table

        Parameters
        ----------
        values : tuple
            A 6-tuple of (city_name, country_name, weather_description, min_degree, max_degree, precipitation)
        """

        self.iid += 1
        self.table_weather.insert(
            parent='',
            index='end',
            iid=self.iid,
            values=values
        )

    def remove_all(self):
        """Remove all instances in the weather table
        """

        while self.iid != -1:
            self.table_weather.delete(self.iid)
            self.iid -= 1


class Forecast(ttk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.master = master

        # Hold the result of the last city search. A dict mapping from "city_name, country_name" to city_id
        self.recent_cities = {}

        # Label
        self.label_forecast = ttk.Label(master=self, text='Forecast')

        # Search bar
        self.var_searchkeyword = tk.StringVar()
        self.combobox_searchbar = ttk.Combobox(master=self, textvariable=self.var_searchkeyword)
        #self.combobox_searchbar.bind('<Return>', self.get_values)
        
        # Forecast table
        self.HEADINGS = ['Day', 'City', 'Country', 'Weather', 'Min degree', 'Max degree', 'Precipitation']
        self.table_forecast = Table(master=self, headings=self.HEADINGS)

        # Display
        self.label_forecast.pack()
        self.combobox_searchbar.pack()
        self.table_forecast.pack()
