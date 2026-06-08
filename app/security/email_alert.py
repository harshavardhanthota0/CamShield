import os
import smtplib
from datetime import datetime
from email.message import EmailMessage

from app.auth.auth_system import AuthSystem
from app.security.encryption import EncryptionManager


class EmailAlert:

    def __init__(self):

        # YOUR Gmail is only the SENDER
        self.sender_email = "harshavardhanthota143@gmail.com"
        self.app_password = "yahq zpog sjfn obrz"

        self.auth = AuthSystem()
        self.encryptor = EncryptionManager()

    def get_receiver_email(self):

        # Gets user/admin email from database/users.json
        return self.auth.get_admin_email()

    def send_intruder_alert(self, image_path):

        receiver_email = self.get_receiver_email()

        if not receiver_email:
            print("[EMAIL ERROR] Receiver email not found")
            return

        try:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            msg = EmailMessage()

            msg["Subject"] = "🚨 CamShield Intruder Alert"
            msg["From"] = self.sender_email
            msg["To"] = receiver_email

            msg.set_content(
                f"""
CamShield Security Alert

Unknown intruder detected.

Time: {timestamp}
Image File: {image_path}

This email was automatically sent by CamShield.
"""
            )

            if os.path.exists(image_path):

                try:
                    image_data = self.encryptor.decrypt_file(image_path)
                except Exception:
                    with open(image_path, "rb") as f:
                        image_data = f.read()

                file_name = os.path.basename(image_path)

                msg.add_attachment(
                    image_data,
                    maintype="image",
                    subtype="jpeg",
                    filename=file_name
                )

            with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
                smtp.login(
                    self.sender_email,
                    self.app_password
                )

                smtp.send_message(msg)

            print("[EMAIL ALERT SENT TO USER]", receiver_email)

        except Exception as e:
            print("[EMAIL ALERT ERROR]", e)