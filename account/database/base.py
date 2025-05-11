import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'movan.db')

CREATE_USER_TABLE = '''
CREATE TABLE IF NOT EXISTS user (
    id TEXT PRIMARY KEY,
    password TEXT,
    name TEXT
)
'''

CREATE_ROLE_TABLE = '''
CREATE TABLE IF NOT EXISTS role (
    id TEXT PRIMARY KEY,
    uid TEXT,
    FOREIGN KEY(uid) REFERENCES user(id)
)
'''

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute('PRAGMA foreign_keys = ON')
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(CREATE_USER_TABLE)
    cursor.execute(CREATE_ROLE_TABLE)
    conn.commit()
    conn.close()

init_db()