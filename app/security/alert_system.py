from app.ui.alert_screen import AlertScreen


class AlertSystem:

    def __init__(self):
        self.screen = None

    def show_alert(self, message="Intruder Detected!"):

        self.screen = AlertScreen()
        self.screen.show()