"""Client and server widgets
"""

import datetime
import threading
import tkinter as tk
import tkinter.ttk as ttk

class Login(ttk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.master = master
        self.login_option = 'ordinary'

        # Username and password entry
        self.var_username = tk.StringVar()
        self.entry_username = ttk.Entry(self, textvariable=self.var_username, width=35)
        self.var_password = tk.StringVar()
        self.entry_password = ttk.Entry(self, textvariable=self.var_password, show='*', width=35)

        # Label to display message
        self.var_prompt = tk.StringVar()
        self.label_prompt = ttk.Label(self, textvariable=self.var_prompt, foreground='red')

        # Login button
        self.var_login_button_text = tk.StringVar(value='Log in')
        self.button_login = ttk.Button(self, textvariable=self.var_login_button_text)

        # Alternative options
        self.label_signup = ttk.Label(self, text='Sign up', underline=1)
        self.label_adminlogin = ttk.Label(self, text='Log in as admin', underline=1)

        self.display()

    def display(self):
        for i in range(0, 5):
            self.rowconfigure(i, pad=7)
        for j in range(0, 2):
            self.columnconfigure(j, pad=7)
        self.rowconfigure(2, pad=2)

        ttk.Label(master=self, text='Username').grid(row=0, column=0, sticky='w')
        self.entry_username.grid(row=0, column=1)
        ttk.Label(master=self, text='Password').grid(row=1, column=0, sticky='w')
        self.entry_password.grid(row=1, column=1)
        self.label_prompt.grid(row=2, column=1)
        self.button_login.grid(row=3, column=1)

        self.label_signup.grid(row=4, column=0)
        self.label_adminlogin.grid(row=4, column=1)
        


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
        self.entry_signup_password = ttk.Entry(self, textvariable=self.var_signup_password, show='*')
        self.entry_signup_password_confirm = ttk.Entry(self, textvariable=self.var_signup_password_confirm, show='*')
        self.entry_signup_name = ttk.Entry(self, textvariable=self.var_signup_name)

        # Sign up button
        self.button_signup = ttk.Button(self, text='Sign up')

        # Back label
        self.label_back = ttk.Label(self, text='< Back')

        self.display()

    def display(self):
        for i in range(0, 6):
            self.rowconfigure(i, pad=7)
        for j in range(0, 2):
            self.columnconfigure(j, pad=7)
        self.rowconfigure(4, pad=2)

        ttk.Label(self, text='Username').grid(row=0, column=0, sticky='w')
        self.entry_signup_username.grid(row=0, column=1)
        ttk.Label(self, text='Password').grid(row=1, column=0, sticky='w')
        self.entry_signup_password.grid(row=1, column=1)
        ttk.Label(self, text='Confirm password').grid(row=2, column=0, sticky='w')
        self.entry_signup_password_confirm.grid(row=2, column=1)
        ttk.Label(self, text='Name').grid(row=3, column=0, sticky='w')
        self.entry_signup_name.grid(row=3, column=1)
        ttk.Label(self, textvariable=self.var_prompt, foreground='red').grid(row=4, column=1)
        self.label_back.grid(row=5, column=0, sticky='w')
        self.button_signup.grid(row=5, column=1)


class Welcome(ttk.Frame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.master = master

        # Labels
        self.label_welcome = ttk.Label(self, text='Welcome')
        self.var_name = tk.StringVar(value='name')
        self.label_name = ttk.Label(self, textvariable=self.var_name)

        # Buttons
        self.button_logout = ttk.Button(self, text='Log out')
        self.button_admintools = ttk.Button(self, text='Admin tools')

        self.display()
    
    def display(self):
        for i in range(0, 2):
            self.rowconfigure(i, pad=7)
        self.columnconfigure(0, pad=7, weight=1, minsize=40)
        self.label_welcome.grid(row=0, column=0, sticky='w')
        self.label_name.grid(row=1, column=0, sticky='w')
        self.button_admintools.grid(row=0, column=1, rowspan=2)
        self.button_logout.grid(row=0, column=2, rowspan=2)


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

    def auto_resize(self):
        for i, t in enumerate(self.headings):
            x = len(t)
            self.column('#' + str(i + 1), width=10 * x + 8)

    
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
        self.table_weather = Table(self, self.HEADINGS)

        self.display()

    def display(self):
        self.columnconfigure(0, weight=1, pad=7)

        self.label_weather.grid(row=0, column=0, sticky='w')
        ttk.Label(self, text='Day').grid(row=0, column=1, sticky='e')
        self.spinbox_day.grid(row=0, column=2)
        self.table_weather.grid(row=1, column=0, columnspan=3, sticky='nsew')


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
        self.HEADINGS = ['Day', 'Weather', 'Min degree', 'Max degree', 'Precipitation']
        self.table_forecast = Table(master=self, headings=self.HEADINGS)

        self.display()

    def display(self):
        self.columnconfigure(0, weight=1, pad=7)
        self.label_forecast.grid(row=0, column=0, sticky='w')
        ttk.Label(self, text='Search city').grid(row=0, column=1, sticky='e')
        self.combobox_searchbar.grid(row=0, column=2)
        self.table_forecast.grid(row=1, column=0, columnspan=3, sticky='nsew')
        self.table_forecast.auto_resize()


class UserActivities(ttk.Frame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.master = master

        # Title
        self.label_activeusers = ttk.Label(self, text='User Activities')

        # Table
        self.HEADINGS = ['Username', 'Priviledge', 'Activity Type', 'Time']
        self.table = Table(self, self.HEADINGS, height=5)
        self.table.auto_resize()

        self.display()

    def display(self):
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        self.label_activeusers.grid(row=0, column=0, sticky='w')
        self.table.grid(row=1, column=0, sticky='nsew')

class Statistics(ttk.Frame):
    def __init__(self, master, **kwargs):
        super().__init__(master)
        self.master = master

        self.var_totalconnections = tk.IntVar(value=0)
        self.var_activeusers = tk.IntVar(value=0)
        self.var_requestsmade = tk.IntVar(value=0)

        self.label_totalconnections = ttk.Label(self, textvariable=self.var_totalconnections)
        self.label_activeusers = ttk.Label(self, textvariable=self.var_activeusers)
        self.label_requestsmade = ttk.Label(self, textvariable=self.var_requestsmade)

        self.display()

    def inc_totalconnections(self):
        self.var_totalconnections.set(self.var_totalconnections.get() + 1)

    def dec_totalconnections(self):
        self.var_totalconnections.set(self.var_totalconnections.get() - 1)

    def inc_activeusers(self):
        self.var_activeusers.set(self.var_activeusers.get() + 1)

    def dec_activeusers(self):
        self.var_activeusers.set(self.var_activeusers.get() - 1)

    def inc_requestsmade(self):
        self.var_requestsmade.set(self.var_requestsmade.get() + 1)

    def dec_requestsmade(self):
        self.var_requestsmade.set(self.var_requestsmade.get() - 1)

    def display(self):
        ttk.Label(self, text='Total Connections').grid(row=0, column=0, columnspan=2)
        self.label_totalconnections.grid(row=1, column=0, columnspan=2)
        ttk.Label(self, text='Active Users').grid(row=2, column=0)
        self.label_activeusers.grid(row=3, column=0)
        ttk.Label(self, text='Requests Made').grid(row=2, column=1)
        self.label_requestsmade.grid(row=3, column=1)


class ServerInterface(threading.Thread):
    def __init__(self, callback):
        super().__init__()
        self.callback = callback

    def run(self):
        self.root = tk.Tk()
        self.root.protocol('WM_DELETE_WINDOW', self.callback)

        self.root.rowconfigure(0, weight=1)
        self.root.columnconfigure(0, weight=1)
        self.root.columnconfigure(1, weight=1)

        self.frame_useractivities = UserActivities(self.root)
        self.frame_useractivities.grid(row=0, column=0)

        self.frame_stat = Statistics(self.root)
        self.frame_stat.grid(row=0, column=1)
        self.root.mainloop()

if __name__ == '__main__':
    root = tk.Tk()
    root.geometry('200x200')
    r = Statistics(root)
    r.grid(row=0, column=0)
    root.mainloop()
    