import datetime
import sqlite3

def extract(message: bytes) -> tuple:
    m = message.decode('utf-8')
    
    header_line, rest = m.split('\n\n', 1)
    field1, field2 = header_line.split(' ', 1)
    message_size, data = rest.split('\n', 1)
    return field1, field2, int(message_size), data

def package(field1: str, field2: str, data: str) -> bytes:
    header_line = (field1 + ' ' + field2).encode()
    blank_line = '\n\n'.encode()
    data = data.encode()

    s = len(header_line) + len(blank_line) + len(data)
    message_size = s + len(str(s).encode()) + 1

    message = header_line + blank_line + str(message_size).encode() + '\n'.encode() + data
    return message

def print_message(message: bytes):
    print(message.decode('utf-8'))

def validate_iso_date_format(date):
    """Validate if a given string is in YYYY-MM-DD format

    Parameters
    ----------
    date : str

    Returns
    -------
    bool
        True if successful, False otherwise
    """

    try:
        datetime.date.fromisoformat(date)
        return True
    except Exception:
        return False
    
def check_username(username: str) -> bool:
    """Check if a given username is valid

    Parameters
    ----------
    username : str
    
    Returns
    -------
    bool
        True if valid, False otherwise
    """

    if len(username) == 0:
        return False
    if username.isnumeric():
        return True
    if username[0].isdecimal():
        return False
    
    for c in username:
        if not (c.isalnum() or c == '_'):
            return False
    return True

def check_name(name: str) -> bool:
    if len(name) == 0:
        return False
    for c in name:
        if not (c.isalnum() or c.isspace()):
            return False
    return True

if __name__ == '__main__':
    n = 'e120'
    print(check_username(n))