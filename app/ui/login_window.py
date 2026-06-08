import sys

from PyQt6.QtWidgets import (
    QApplication,
    QWidget,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QMessageBox
)

from PyQt6.QtGui import (
    QFont,
    QPixmap,
    QIcon
)

from PyQt6.QtCore import Qt

from app.auth.auth_system import AuthSystem


class LoginWindow(QWidget):

    def __init__(self, on_success):

        super().__init__()

        self.auth = AuthSystem()

        self.on_success = on_success

        self.setup_ui()

    # =====================================================
    # UI
    # =====================================================

    def setup_ui(self):

        self.setWindowTitle(
            "CamShield - Secure Login"
        )

        self.setWindowIcon(
            QIcon("assets/shield.ico")
        )

        self.setFixedSize(420, 500)

        # =====================================================
        # MAIN LAYOUT
        # =====================================================

        layout = QVBoxLayout()

        layout.setSpacing(20)

        layout.setContentsMargins(
            40,
            40,
            40,
            40
        )

        # =====================================================
        # LOGO
        # =====================================================

        logo = QLabel()

        pixmap = QPixmap(
            "assets/logo.png"
        )

        logo.setPixmap(
            pixmap.scaled(
                100,
                100,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
        )

        logo.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        # =====================================================
        # TITLE
        # =====================================================

        title = QLabel(
            "CamShield"
        )

        title.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        title.setFont(
            QFont(
                "Segoe UI",
                24,
                QFont.Weight.Bold
            )
        )

        title.setStyleSheet("""
        color: #00c8ff;
        """)

       

        # =====================================================
        # USERNAME
        # =====================================================

        self.username_input = QLineEdit()

        self.username_input.setPlaceholderText(
            "Enter Username"
        )

        self.username_input.setFixedHeight(50)

        # =====================================================
        # PASSWORD
        # =====================================================

        self.password_input = QLineEdit()

        self.password_input.setPlaceholderText(
            "Enter Password"
        )

        self.password_input.setEchoMode(
            QLineEdit.EchoMode.Password
        )

        self.password_input.setFixedHeight(50)

        # =====================================================
        # LOGIN BUTTON
        # =====================================================

        login_btn = QPushButton(
            "LOGIN"
        )

        login_btn.setFixedHeight(55)

        login_btn.clicked.connect(
            self.login_user
        )

        # =====================================================
        # STATUS
        # =====================================================

        self.status = QLabel("")

        self.status.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        self.status.setStyleSheet("""
        color: #ff4d4d;
        font-size: 13px;
        """)

        # =====================================================
        # ADD WIDGETS
        # =====================================================

        layout.addStretch()

        layout.addWidget(logo)

        layout.addWidget(title)

        

        layout.addSpacing(20)

        layout.addWidget(
            self.username_input
        )

        layout.addWidget(
            self.password_input
        )

        layout.addWidget(login_btn)

        layout.addWidget(self.status)

        layout.addStretch()

        self.setLayout(layout)

        # =====================================================
        # STYLE
        # =====================================================

        self.setStyleSheet("""

        QWidget {
            background-color: #07111f;
            color: white;
            font-family: Segoe UI;
        }

        QLineEdit {
            background-color: #101827;
            border: 2px solid #1e293b;
            border-radius: 12px;
            padding-left: 15px;
            font-size: 15px;
            color: white;
        }

        QLineEdit:focus {
            border: 2px solid #00c8ff;
        }

        QPushButton {
            background-color: #00c8ff;
            color: black;
            border-radius: 14px;
            font-size: 16px;
            font-weight: bold;
        }

        QPushButton:hover {
            background-color: #00ffff;
        }

        """)

    # =====================================================
    # LOGIN
    # =====================================================

    def login_user(self):

        username = self.username_input.text().strip()

        password = self.password_input.text().strip()

        # EMPTY CHECK
        if username == "" or password == "":

            self.status.setStyleSheet("""
            color: #ff4d4d;
            font-size: 13px;
            """)

            self.status.setText(
                "Enter username and password"
            )

            return

        # LOGIN CHECK
        role = self.auth.login(
            username,
            password
        )

        # SUCCESS
        if role is not None:

            self.status.setStyleSheet("""
            color: #00ff99;
            font-size: 13px;
            """)

            self.status.setText(
                "Login Successful"
            )

            self.close()

            self.on_success(role)

        # FAILED
        else:

            self.status.setStyleSheet("""
            color: #ff4d4d;
            font-size: 13px;
            """)

            self.status.setText(
                "Invalid Username or Password"
            )


# =====================================================
# RUN DIRECTLY
# =====================================================

if __name__ == "__main__":

    app = QApplication(sys.argv)

    window = LoginWindow(
        lambda role: print(role)
    )

    window.show()

    sys.exit(app.exec())