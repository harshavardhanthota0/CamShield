import sqlite3
import os


class Database:

    def __init__(self):

        # Create database folder if missing
        if not os.path.exists("database"):
            os.makedirs("database")

        # Connect database
        self.conn = sqlite3.connect("database/camshield.db")

        # Create cursor
        self.cursor = self.conn.cursor()

        # Create tables
        self.create_tables()

    def create_tables(self):

        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            username TEXT UNIQUE,

            password TEXT,

            role TEXT
        )
        """)

        self.conn.commit()

    def add_user(self, username, password, role):

        self.cursor.execute(
            """
            INSERT INTO users(username, password, role)
            VALUES (?, ?, ?)
            """,
            (username, password, role)
        )

        self.conn.commit()

    def get_user(self, username):

        self.cursor.execute(
            """
            SELECT * FROM users
            WHERE username=?
            """,
            (username,)
        )

        return self.cursor.fetchone()