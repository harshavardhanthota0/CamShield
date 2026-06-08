import os
from datetime import datetime
from cryptography.fernet import Fernet


class EncryptedLogger:

    def __init__(self):

        os.makedirs("logs", exist_ok=True)

        self.log_file = "logs/intruder_logs.txt"

        # LOAD KEY
        with open("secret.key", "rb") as key_file:

            key = key_file.read()

        self.cipher = Fernet(key)

    # =====================================================
    # WRITE ENCRYPTED LOG
    # =====================================================

    def log_intruder(self, image_path):

        timestamp = datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )

        log_text = (
            f"[{timestamp}] "
            f"INTRUDER DETECTED -> "
            f"{image_path}"
        )

        encrypted = self.cipher.encrypt(
            log_text.encode()
        )

        with open(self.log_file, "ab") as file:

            file.write(encrypted + b"\n")

        print("[ENCRYPTED LOG SAVED]")

    # =====================================================
    # READ DECRYPTED LOGS
    # =====================================================

    def read_logs(self):

        if not os.path.exists(self.log_file):

            return "No logs found"

        logs = []

        with open(self.log_file, "rb") as file:

            lines = file.readlines()

        for line in lines:

            try:

                decrypted = self.cipher.decrypt(
                    line.strip()
                ).decode()

                logs.append(decrypted)

            except:

                continue

        return "\n".join(logs)