import sqlite3
import os


class Database:

    def __init__(self):

        self.db_path = "camshield.db"
        self.init_db()

    def init_db(self):

        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()

        cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password BLOB NOT NULL,
            role TEXT NOT NULL
        )
        """)

        conn.commit()
        conn.close()