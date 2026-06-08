import json
import os
import sys
import bcrypt


if getattr(sys, "frozen", False):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            "../../"
        )
    )


# =====================================================
# AUTH SYSTEM
# =====================================================

class AuthSystem:

    def __init__(self):

        # DATABASE FILE
        self.db_file = os.path.join(
            BASE_DIR,
            "database",
            "users.json"
        )

        # CREATE DATABASE FOLDER
        os.makedirs(
            os.path.dirname(self.db_file),
            exist_ok=True
        )

        # CREATE EMPTY USERS FILE
        if not os.path.exists(self.db_file):

            with open(self.db_file, "w") as f:

                json.dump({}, f, indent=4)

    # =====================================================
    # LOAD USERS
    # =====================================================

    def load_users(self):

        try:

            with open(self.db_file, "r") as f:

                return json.load(f)

        except json.JSONDecodeError:

            return {}

    # =====================================================
    # SAVE USERS
    # =====================================================

    def save_users(self, users):

        with open(self.db_file, "w") as f:

            json.dump(
                users,
                f,
                indent=4
            )

    # =====================================================
    # CREATE USER
    # =====================================================

    def create_user(
        self,
        username,
        password,
        email,
        role="user"
    ):

        users = self.load_users()

        # USER EXISTS
        if username in users:

            return False

        # HASH PASSWORD
        hashed_password = bcrypt.hashpw(
            password.encode(),
            bcrypt.gensalt()
        ).decode()

        # STORE USER
        users[username] = {

            "email": email,

            "password": hashed_password,

            "role": role
        }

        self.save_users(users)

        print("[USER CREATED]")

        return True

    # =====================================================
    # LOGIN
    # =====================================================

    def login(self, username, password):

        users = self.load_users()
        print("DB FILE:", self.db_file)
        print("USERS:", users)

        # USER EXISTS?
        if username not in users:

            return None

        stored_hash = users[username]["password"]

        try:

            # PASSWORD CHECK
            if bcrypt.checkpw(
                password.encode(),
                stored_hash.encode()
            ):

                return users[username]["role"]

        except ValueError:

            return None

        return None

    # =====================================================
    # GET USER EMAIL
    # =====================================================

    def get_user_email(self, username):

        users = self.load_users()
        print("USERS:", users)

        if username in users:

            return users[username].get(
                "email"
            )

        return None

    # =====================================================
    # GET ADMIN EMAIL
    # =====================================================

    def get_admin_email(self):

        users = self.load_users()

        for user in users.values():

            if user.get("role") == "admin":

                return user.get("email")

        return None

    # =====================================================
    # UPDATE USERNAME
    # =====================================================

    def update_username(
        self,
        old_username,
        new_username
    ):

        users = self.load_users()

        # OLD USER EXISTS?
        if old_username not in users:

            return False

        # NEW USER EXISTS?
        if new_username in users:

            return False

        # UPDATE
        users[new_username] = users.pop(
            old_username
        )

        self.save_users(users)

        return True

    # =====================================================
    # UPDATE PASSWORD
    # =====================================================

    def update_password(
        self,
        username,
        new_password
    ):

        users = self.load_users()

        if username not in users:

            return False

        # HASH NEW PASSWORD
        hashed_password = bcrypt.hashpw(
            new_password.encode(),
            bcrypt.gensalt()
        ).decode()

        users[username]["password"] = (
            hashed_password
        )

        self.save_users(users)

        return True