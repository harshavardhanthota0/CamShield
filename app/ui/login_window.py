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

from PyQt6.QtCore import Qt

from PyQt6.QtGui import (
    QPixmap,
    QIcon
)

from app.auth.auth_system import AuthSystem
from app.security.password_generator import generate_password
from app.security.user_email import UserEmailSender


class SetupWindow(QWidget):

    def __init__(self, on_complete):

        super().__init__()

        self.on_complete = on_complete
        self.auth = AuthSystem()

        self.setWindowTitle("CamShield - First Time Setup")
        self.setFixedSize(500, 520)

        self.setWindowIcon(
            QIcon("assets/shield.ico")
        )

        self.setup_ui()

    def setup_ui(self):

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(20)

        logo = QLabel("🛡")
        logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo.setStyleSheet("font-size: 90px; color: #00c8ff;")

        title = QLabel("CamShield Setup")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("""
        font-size: 34px;
        font-weight: bold;
        color: #00c8ff;
        """)

        subtitle = QLabel("Create your first admin account")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setStyleSheet("font-size: 16px; color: #9ca3af;")

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Enter Admin Username")
        self.username_input.setFixedHeight(55)

        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Enter Admin Email")
        self.email_input.setFixedHeight(55)

        setup_btn = QPushButton("Create Admin Account")
        setup_btn.setFixedHeight(55)
        setup_btn.clicked.connect(self.create_admin)

        self.status_label = QLabel("")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet("font-size: 14px; color: red;")

        layout.addStretch()
        layout.addWidget(logo)
        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addSpacing(30)
        layout.addWidget(self.username_input)
        layout.addWidget(self.email_input)
        layout.addSpacing(10)
        layout.addWidget(setup_btn)
        layout.addWidget(self.status_label)
        layout.addStretch()

        self.setLayout(layout)
        self.apply_style()

    def create_admin(self):

        username = self.username_input.text().strip()
        email = self.email_input.text().strip()

        if username == "" or email == "":
            self.status_label.setText("Enter username and email")
            return

        password = generate_password()

        created = self.auth.create_user(
            username,
            password,
            email,
            "admin"
        )

        if not created:
            self.status_label.setText("Admin already exists")
            return

        try:
            sender = UserEmailSender()

            sender.send_user_credentials(
                email,
                username,
                password
            )

            QMessageBox.information(
                self,
                "Success",
                "Admin account created.\nPassword sent to email."
            )

        except Exception as e:
            QMessageBox.warning(
                self,
                "Email Failed",
                f"Admin created, but email failed.\n\nPassword: {password}\n\nError: {e}"
            )

        self.close()
        self.on_complete()

    def apply_style(self):

        self.setStyleSheet("""
        QWidget {
            background-color: #081120;
            color: white;
            font-family: Segoe UI;
        }

        QLineEdit {
            background-color: #101827;
            border: 2px solid #1f2937;
            border-radius: 12px;
            padding-left: 15px;
            color: white;
            font-size: 16px;
        }

        QLineEdit:focus {
            border: 2px solid #00c8ff;
        }

        QPushButton {
            background-color: #00c8ff;
            color: black;
            border-radius: 12px;
            font-size: 18px;
            font-weight: bold;
        }

        QPushButton:hover {
            background-color: #00ffff;
        }
        """)


class LoginWindow(QWidget):

    def __init__(self, on_success):

        super().__init__()
        
        self.setWindowIcon(
            QIcon("assets/shield.ico")
        )

        self.on_success = on_success
        self.auth = AuthSystem()


        self.setWindowTitle("CamShield - Secure Login")
        self.setFixedSize(500, 600)

        self.setup_ui()

    def setup_ui(self):

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(20)

        logo = QLabel("🛡")
        logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo.setStyleSheet("font-size: 90px; color: #00c8ff;")

        title = QLabel("CamShield")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("""
        font-size: 36px;
        font-weight: bold;
        color: #00c8ff;
        """)

       

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Enter Username")
        self.username_input.setFixedHeight(55)

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Enter Password")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setFixedHeight(55)

        login_btn = QPushButton("Login")
        login_btn.setFixedHeight(55)
        login_btn.clicked.connect(self.login_user)

        self.status_label = QLabel("")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet("font-size: 14px; color: red;")

        layout.addStretch()
        layout.addWidget(logo)
        layout.addWidget(title)
       
        layout.addSpacing(30)
        layout.addWidget(self.username_input)
        layout.addWidget(self.password_input)
        layout.addSpacing(10)
        layout.addWidget(login_btn)
        layout.addWidget(self.status_label)
        layout.addStretch()

        self.setLayout(layout)
        self.apply_style()

    def login_user(self):

        username = self.username_input.text().strip()
        password = self.password_input.text().strip()

        if username == "" or password == "":
            self.status_label.setText("Enter username and password")
            return

        role = self.auth.login(username, password)

        if role is None:
            self.status_label.setText("Wrong username or password")
            return

        self.status_label.setText("")

        opened = self.on_success(role)

        if opened:
            self.hide()
        else:
            self.status_label.setText("Dashboard failed to open")

    def apply_style(self):

        self.setStyleSheet("""
        QWidget {
            background-color: #081120;
            color: white;
            font-family: Segoe UI;
        }

        QLineEdit {
            background-color: #101827;
            border: 2px solid #1f2937;
            border-radius: 12px;
            padding-left: 15px;
            color: white;
            font-size: 16px;
        }

        QLineEdit:focus {
            border: 2px solid #00c8ff;
        }

        QPushButton {
            background-color: #00c8ff;
            color: black;
            border-radius: 12px;
            font-size: 18px;
            font-weight: bold;
        }

        QPushButton:hover {
            background-color: #00ffff;
        }
        """)


if __name__ == "__main__":

    app = QApplication(sys.argv)

    window = LoginWindow(
        lambda role: print("Logged in as:", role)
    )

    window.show()

    sys.exit(app.exec())