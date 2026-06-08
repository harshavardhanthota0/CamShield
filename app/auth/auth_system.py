import json
import os


class AuthSystem:

    def __init__(self):

        self.db_file = "database/users.json"

    # =========================================
    # LOAD USERS
    # =========================================

    def load_users(self):

        if not os.path.exists(self.db_file):

            return {}

        with open(self.db_file, "r") as f:

            return json.load(f)

    # =========================================
    # LOGIN
    # =========================================

    def login(self, username, password):

        users = self.load_users()

        # USER EXISTS?
        if username not in users:

            return None

        # PASSWORD CHECK
        if users[username]["password"] != password:

            return None

        # SUCCESS
        return users[username]["role"]

    # =========================================
    # CREATE USER
    # =========================================

    def create_user(
        self,
        username,
        password,
        role="user"
    ):

        users = self.load_users()

        if username in users:

            print("[ERROR] User already exists")

            return False

        users[username] = {
            "password": password,
            "role": role
        }

        with open(self.db_file, "w") as f:

            json.dump(
                users,
                f,
                indent=4
            )

        print("[SUCCESS] User created")

        return True