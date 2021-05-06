import sqlite3

def extract(message: bytes) -> tuple:
    message = message.decode('utf-8')
    header, data = tuple(message.split('\n', 1))
    field1, field2 = tuple(header.split(' ', 1))
    return (field1, field2, data)

def package(field1, field2, data) -> bytes:
    message = str(field1) + ' ' + str(field2) + '\n' + str(data)
    return message.encode('utf-8')

def print_message(message: bytes):
    print(message.decode('utf-8'))

