import sqlite3

def connect():
    return sqlite3.connect('test.db')

def create_db() :
    connection = connect()
    connection.close()

def create_tables():
    connection = connect()

    cursor = connection.cursor()
    cursor.execute('''
CREATE TABLE IF NOT EXISTS plants (
        id INTEGER PRIMARY KEY,
        name TEXT,
        sc_name TEXT NOT NULL
)
''')

    connection.commit()
    connection.close()

def add_data(name, sc_name):
    connection = connect()

    cursor = connection.cursor()

    cursor.execute('''
INSERT INTO plants (name, sc_name) 
VALUES (?, ?)''', (name, sc_name))

    connection.commit()
    connection.close()


def query():
    connection = connect()
    cursor = connection.cursor()

    cursor.execute('SELECT * FROM plants')

    rows = cursor.fetchall()

    print(rows)
    print()
    for row in rows:
        print(row)

    connection.close()

query()