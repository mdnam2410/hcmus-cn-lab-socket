import util

import socket

class ConnectionError(Exception):
    pass

class App:
    """Base class for Client and Server class
    """
    
    def __init__(self):
        # Main socket object
        self.main_socket = None
        self.socket_buffer = 1024

        # Ports
        self.DISCOVERY_PORT = 2410
        self.SERVER_PORT = 2802

    def receive_from(self, s: socket.socket) -> bytes:
        """Receive data from a given socket

        Parameters
        ----------
        s : socket.socket

        Returns
        -------
        bytes
            The full message
        """

        # Receive the first message
        message = s.recv(self.socket_buffer)
        if len(message) == 0:
            raise ConnectionError('Connection closed')

        # Investigate the size
        _, _, size, _ = util.extract(message)

        # The number of remaining parts of the message to receive
        r = size // self.socket_buffer - 1

        # Receive the rest
        while r >= 0:
            message += s.recv(self.socket_buffer)
            r -= 1
        return message

    def send(self, message: bytes):
        """Send message using main_socket

        Parameters
        ----------
        message : bytes

        """
        self.main_socket.send(message)

    def receive(self) -> bytes:
        """Receive from the main_socket

        Returns
        -------
        bytes
            The full message
        """
        return self.receive_from(self.main_socket)
