import os
import sys

from cryptography.fernet import Fernet


class EncryptionManager:

    def __init__(self):

        if getattr(sys, "frozen", False):

            base_path = sys._MEIPASS

        else:

            base_path = os.path.abspath(
                os.path.join(
                    os.path.dirname(__file__),
                    "../../"
                )
            )

        self.key_path = os.path.join(
            base_path,
            "secret.key"
        )

        with open(self.key_path, "rb") as key_file:

            self.key = key_file.read()

        self.cipher = Fernet(self.key)

    def encrypt_file(self, path):

        with open(path, "rb") as file:
            data = file.read()

        encrypted = self.cipher.encrypt(data)

        with open(path, "wb") as file:
            file.write(encrypted)

    def decrypt_file(self, path):

        with open(path, "rb") as file:
            encrypted = file.read()

        return self.cipher.decrypt(encrypted)