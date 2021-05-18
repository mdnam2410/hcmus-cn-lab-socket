"""Define neccessary classes for displaying layout in the log in and sign up windows
"""

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
