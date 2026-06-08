import smtplib
from email.message import EmailMessage


class UserEmailSender:

    def __init__(self):
        self.sender_email = "harshavardhanthota143@gmail.com"
        self.app_password = "yahq zpog sjfn obrz"

    def send_user_credentials(self, receiver_email, username, password):
        msg = EmailMessage()

        msg["Subject"] = "CamShield Account Credentials"
        msg["From"] = self.sender_email
        msg["To"] = receiver_email

        msg.set_content(
            f"""
Your CamShield account has been created.

Username: {username}
Password: {password}

Please change your password after first login.
"""
        )

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(self.sender_email, self.app_password)
            smtp.send_message(msg)

        print("[EMAIL SENT]")