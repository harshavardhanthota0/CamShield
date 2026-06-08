import cv2

from app.security.intruder_capture import IntruderCapture
from app.security.encrypted_logger import EncryptedLogger


class WebcamMonitor:

    def __init__(self):

        self.camera = None

        # INTRUDER IMAGE SAVER
        self.capture = IntruderCapture()

        # LOGGER
        self.logger = EncryptedLogger()  

    # ==========================================
    # START CAMERA
    # ==========================================

    def start_camera(self):

        if self.camera is not None:
            self.camera.release()
            self.camera = None

        self.camera = cv2.VideoCapture(0, cv2.CAP_DSHOW)

        if not self.camera.isOpened():
            print("Failed To Access Webcam")
            return False

        print("Webcam Started")
        return True

    # ==========================================
    # STOP CAMERA
    # ==========================================

    def stop_camera(self):

        if self.camera is not None:

            self.camera.release()

            self.camera = None

            cv2.destroyAllWindows()

            print("Webcam Stopped")