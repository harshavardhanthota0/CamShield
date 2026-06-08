import sys

from PyQt6.QtWidgets import QApplication

from app.auth.auth_system import AuthSystem
from app.ui.login_window import LoginWindow, SetupWindow


dashboard_window = None
login_window = None
setup_window = None


def launch_dashboard(role):

    global dashboard_window

    try:
        from app.ui.dashboard import CamShield

        dashboard_window = CamShield(role)
        dashboard_window.show()

        return True

    except Exception as e:
        import traceback
        from PyQt6.QtWidgets import QMessageBox

        traceback.print_exc()

        QMessageBox.critical(
            None,
            "Dashboard Error",
            str(e)
        )

        return False


def open_login():
    global login_window

    login_window = LoginWindow(launch_dashboard)
    login_window.show()


def main():
    global setup_window

    app = QApplication(sys.argv)

    auth = AuthSystem()
    users = auth.load_users()

    if len(users) == 0:
        setup_window = SetupWindow(open_login)
        setup_window.show()
    else:
        open_login()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()