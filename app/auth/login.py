import bcrypt
from app.database.db import Database


class LoginSystem:

    def __init__(self):

        self.db = Database()

    def create_admin(self):

        username = "admin"
        password = "admin123"

        hashed = bcrypt.hashpw(
            password.encode(),
            bcrypt.gensalt()
        )

        try:

            self.db.add_user(
                username,
                hashed.decode(),
                "Admin"
            )

            print("Admin Created")

        except:

            print("Admin Already Exists")

    def login(self, username, password):

        user = self.db.get_user(username)

        if user:

            stored_password = user[2].encode()

            if bcrypt.checkpw(
                password.encode(),
                stored_password
            ):

                return True

        return False