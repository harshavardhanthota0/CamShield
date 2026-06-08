import os
import cv2

from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QMessageBox
)


class RegisterWindow(QWidget):

    def __init__(self):

        super().__init__()

        self.setWindowTitle("Register Face")

        self.setFixedSize(350, 200)

        layout = QVBoxLayout()

        self.label = QLabel("Enter Username")

        self.username = QLineEdit()

        self.username.setPlaceholderText("Username")

        self.capture_btn = QPushButton("Capture Face")

        self.capture_btn.clicked.connect(self.capture_face)

        layout.addWidget(self.label)

        layout.addWidget(self.username)

        layout.addWidget(self.capture_btn)

        self.setLayout(layout)

    def capture_face(self):

        username = self.username.text().strip()

        if username == "":

            QMessageBox.warning(
                self,
                "Error",
                "Enter username"
            )

            return

        os.makedirs("known_faces", exist_ok=True)

        camera = cv2.VideoCapture(0)

        if not camera.isOpened():

            QMessageBox.warning(
                self,
                "Error",
                "Cannot access webcam"
            )

            return

        QMessageBox.information(
            self,
            "Instructions",
            "Press SPACE to capture face\nPress ESC to cancel"
        )

        while True:

            ret, frame = camera.read()

            if not ret:
                break

            cv2.imshow("Register Face", frame)

            key = cv2.waitKey(1)

            # SPACE KEY
            if key == 32:

                path = f"known_faces/{username}.jpg"

                cv2.imwrite(path, frame)

                QMessageBox.information(
                    self,
                    "Success",
                    f"Face saved:\n{path}"
                )

                break

            # ESC KEY
            if key == 27:
                break

        camera.release()

        cv2.destroyAllWindows()

        self.close()