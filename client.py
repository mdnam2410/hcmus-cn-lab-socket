from datetime import date
import app
import util

import socket
import time


class Client(app.App):
    def __init__(self):
        super().__init__()

        self.main_socket = self.discover_server()
        if self.main_socket is None:
            raise app.ConnectionError('Unable to connect to server')
        
        # Check if the maximum number of clients the server can serve is reached
        status_code, status_message, _, _ = util.extract(self.receive())
        if status_code != '000':
            self.main_socket.close()
            raise app.ConnectionError(status_message)

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

    def login(self):
        self.username = input('Username: ')
        self.password = input('Password: ')
        self.send(util.package('login', '', f'{self.username},{self.password}'))
        status_code, status_message, _, data = util.extract(self.receive())
        if status_code == '000':
            print('Logged in')
            print(data)
        else:
            print('Error:', status_message)

    def signup(self):
        command = 'signup'
        command_type = ''

        self.username = input('Username: ')
        self.password = input('Password: ')
        self.name = input('Name: ')
        retype_password = input('Retype password: ')

        if self.password != retype_password:
            print('Unmatched password')
            return
        else:
            data = self.username + ',' + self.password + ',' + self.name

        self.send(util.package(command, command_type, data))
        status_code, status_message, _, _ = util.extract(self.receive())
        if status_code == '000':
            print('Sign up succeeded.')
        else:
            print(status_message)

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
        
if __name__ == '__main__':
    client = Client()
    client.login()
    client.search()
