import sqlite3

def get_db():
    conn = sqlite3.connect('app.sqlite')
    return conn


def initialize_db():
    conn = get_db()
    with open('schema.sql', "r") as file:
        conn.executescript(file.read())


def cleanup_db(conn):
    if conn is not None:
        conn.close()
