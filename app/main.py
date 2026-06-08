import sys

from PyQt6.QtWidgets import QApplication

from app.ui.login_window import LoginWindow
from app.ui.dashboard import CamShield


def launch_dashboard(role):

    global dashboard_window

    dashboard_window = CamShield(role)

    dashboard_window.show()


app = QApplication(sys.argv)

login_window = LoginWindow(
    launch_dashboard
)

login_window.show()

sys.exit(app.exec())