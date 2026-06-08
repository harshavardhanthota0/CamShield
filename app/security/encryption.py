from cryptography.fernet import Fernet


class EncryptionManager:

    def __init__(self):

        with open("secret.key", "rb") as key_file:

            self.key = key_file.read()

        self.cipher = Fernet(self.key)

    # ENCRYPT FILE
    def encrypt_file(self, path):

        with open(path, "rb") as file:

            data = file.read()

        encrypted = self.cipher.encrypt(data)

        with open(path, "wb") as file:

            file.write(encrypted)

    # DECRYPT FILE
    def decrypt_file(self, path):

        with open(path, "rb") as file:

            encrypted = file.read()

        decrypted = self.cipher.decrypt(encrypted)

        return decrypted