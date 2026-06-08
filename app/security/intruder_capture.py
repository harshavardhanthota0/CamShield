import cv2
import os
from datetime import datetime
from app.security.encryption import EncryptionManager


class IntruderCapture:

    def __init__(self):
        self.folder = "intruders"
        os.makedirs(self.folder, exist_ok=True)
        self.encryptor = EncryptionManager()

    def save_snapshot(self, frame):

        filename = f"{self.folder}/intruder_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
        cv2.imwrite(filename, frame)
        self.encryptor.encrypt_file(filename)

        return filename