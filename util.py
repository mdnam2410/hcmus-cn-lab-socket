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
    """Validate if a given string can be used as a username.

    Parameters
    ----------
    username : str

    Returns
    -------
    bool

    A string is validated if:
    - It contains at least one character.
    - Its characters are either alphanumeric or underscores.
    - It does not start with a number.
    - It contains at least one alphanumeric character, i.e. cannot contain all numbers or all underscores.
    """

    if len(username) == 0:
        return False
    if username[0].isdecimal():
        return False
    
    has_alnum = False
    for c in username:
        if not(c.isalnum() or c == '_'):
            return False
        if c.isalnum():
            has_alnum = True
    return True if has_alnum else False

def is_alnum_with_space(name: str) -> bool:
    """Validate if a given string only contains alphanumeric characters or spaces.

    Parameters
    ----------
    string : str

    Returns
    -------
    bool

    A string is validated if:
    - It contains more than one character.
    - Its characters are either alphanumeric or spaces.
    - It contains at least one alphanumeric character, i.e. cannot contain spaces only.
    """

    if len(name) == 0:
        return False
    has_alnum = False
    for c in name:
        if not (c.isalnum() or c.isspace()):
            return False
        if c.isalnum():
            has_alnum = True
    return True if has_alnum else False

def isfloat(string) -> bool:
    try:
        float(string)
        return True
    except Exception:
        return False

if __name__ == '__main__':
    n = 'e120'
    print(check_username(n))