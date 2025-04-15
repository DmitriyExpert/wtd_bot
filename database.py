import sqlite3

def conn_db():
    connection = sqlite3.connect('db.db')
    return connection
