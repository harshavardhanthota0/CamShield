import os
import sys
from datetime import datetime

from cryptography.fernet import Fernet


class EncryptedLogger:

    def __init__(self):

        os.makedirs("logs", exist_ok=True)

        self.log_file = "logs/intruder_logs.txt"

        # EXE MODE
        if getattr(sys, "frozen", False):
            key_path = os.path.join(
                sys._MEIPASS,
                "secret.key"
            )

        # NORMAL PYTHON MODE
        else:
            key_path = os.path.abspath(
                "secret.key"
            )

        with open(key_path, "rb") as key_file:
            self.key = key_file.read()

        self.cipher = Fernet(self.key)

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

            except Exception:
                continue

        if len(logs) == 0:
            return "No logs found"

        return "\n".join(logs)