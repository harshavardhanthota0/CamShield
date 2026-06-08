import sys
import os
import time
import cv2
import json
import bcrypt
import threading
import subprocess

import numpy as np
import face_recognition

from playsound import playsound

from PyQt6.QtCore import (
    Qt,
    QSize,
    QTimer,
    QTime
)

from PyQt6.QtGui import (
    QPixmap,
    QIcon,
    QImage
)

from PyQt6.QtWidgets import (
    QApplication,
    QWidget,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QListWidget,
    QListWidgetItem,
    QTextEdit,
    QDialog,
    QStackedWidget,
    QGridLayout,
    QInputDialog,
    QMessageBox,
    QTimeEdit
)

from app.security.email_alert import EmailAlert
from app.security.encrypted_logger import EncryptedLogger
from app.webcam.webcam_monitor import WebcamMonitor
from app.auth.register import RegisterWindow


class CamShield(QWidget):

    def __init__(self, role):

        super().__init__()

        self.role = role

        # WINDOW
        self.setWindowTitle("CamShield - Secure Dashboard")
        self.setGeometry(100, 50, 1500, 900)
        self.setWindowIcon(
            QIcon("assets/shield.ico")
        )

        # CORE SERVICES
        self.webcam = WebcamMonitor()
        self.logger = EncryptedLogger()
        self.email_alert = EmailAlert()
        self.register_window = RegisterWindow()

        # FACE DATA
        self.known_face_encodings = []
        self.known_face_names = []
        self.last_detected_name = ""

        # INTRUDER COOLDOWN
        self.last_intruder_time = 0
        self.cooldown = 60 * 5  # 5 minutes

        # SAFE CAMERA LOCK
        self.camera_lock = None

        # SCHEDULER
        self.schedule_enabled = False

        # UI
        self.setup_ui()

        # CAMERA TIMER
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)

        # SCHEDULER TIMER
        self.scheduler_timer = QTimer()
        self.scheduler_timer.timeout.connect(
            self.check_schedule
        )
        self.scheduler_timer.start(1000)

        # LOAD FACES
        self.load_known_faces()

    # =====================================================
    # UI
    # =====================================================

    def setup_ui(self):
        print("UI LOADING...")

        main_layout = QHBoxLayout()

        # =====================================================
        # SIDEBAR
        # =====================================================

        self.sidebar = QListWidget()

        self.sidebar.setFixedWidth(280)

        sidebar_items = [
            ("assets/shield.png", "Security Overview"),
            ("assets/webcam.png", "Webcam Protection"),
            ("assets/intruder.png", "Intruder Detection"),
            ("assets/face.png", "Face Recognition"),
            ("assets/logs.png", "Logs & Monitoring"),
            ("assets/settings.png", "Settings")
        ]

        for icon_path, text in sidebar_items:

            item = QListWidgetItem(
                QIcon(icon_path),
                text
            )

            self.sidebar.addItem(item)

        self.sidebar.currentRowChanged.connect(
            self.change_page
        )

        # =====================================================
        # RIGHT SIDE
        # =====================================================

        right_layout = QVBoxLayout()

        # =====================================================
        # TOP BAR
        # =====================================================

        top_bar = QHBoxLayout()

        # LOGO
        logo = QLabel()

        logo_pixmap = QPixmap(
            "assets/logo.png"
        )

        logo.setPixmap(
            logo_pixmap.scaled(
                70,
                70,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
        )

        # TITLE
        title = QLabel(
            "CamShield  Security Dashboard"
        )

        title.setStyleSheet("""
        font-size: 30px;
        font-weight: bold;
        color: #00c8ff;
        padding-left: 10px;
        """)

        # TITLE LAYOUT
        title_layout = QHBoxLayout()

        title_layout.addWidget(logo)

        title_layout.addWidget(title)

        title_widget = QWidget()

        title_widget.setLayout(title_layout)

        # STATUS
        self.status = QLabel(
            f"🟢 Logged in as: {self.role}"
        )

        self.status.setStyleSheet("""
        font-size: 16px;
        color: #00ff99;
        padding-right: 20px;
        """)

        # REGISTER BUTTON
        register_btn = QPushButton(
            "Register Face"
        )

        register_btn.setFixedSize(190, 50)

        register_btn.clicked.connect(
            self.open_register_window
        )

        top_bar.addWidget(title_widget)

        top_bar.addStretch()

        top_bar.addWidget(self.status)

        top_bar.addSpacing(20)

        top_bar.addWidget(register_btn)

        # =====================================================
        # CAMERA BUTTONS
        # =====================================================

        self.enable_btn = QPushButton("Enable Camera")

        self.disable_btn = QPushButton("Disable Camera")

        self.enable_btn.setFixedHeight(55)

        self.disable_btn.setFixedHeight(55)

        self.enable_btn.clicked.connect(
            self.enable_webcam
        )

        self.disable_btn.clicked.connect(
            self.disable_webcam
        )

        # =====================================================
        # LIVE CAMERA
        # =====================================================

        self.camera_label = QLabel()

        self.camera_label.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        self.camera_label.setMinimumHeight(500)

        self.camera_label.setText(
            "Live Camera Feed"
        )

        self.camera_label.setStyleSheet("""
        background-color: black;
        border: 3px solid #00c8ff;
        border-radius: 15px;
        """)

        # =====================================================
        # LOGS
        # =====================================================

        self.logs_box = QTextEdit()

        self.logs_box.setReadOnly(True)

        # =====================================================
        # GALLERY
        # =====================================================

        self.gallery = QListWidget()

        self.gallery.setViewMode(
            QListWidget.ViewMode.IconMode
        )

        self.gallery.setResizeMode(
            QListWidget.ResizeMode.Adjust
        )

        self.gallery.setIconSize(
            QSize(150, 150)
        )

        self.gallery.setSpacing(15)

        self.gallery.itemClicked.connect(
            self.open_image_preview
        )

        # =====================================================
        # STACKED PAGES
        # =====================================================

        self.pages = QStackedWidget()

        # =====================================================
        # OVERVIEW PAGE
        # =====================================================

        overview_page = QWidget()

        overview_layout = QVBoxLayout()

        overview_title = QLabel(
            "System Overview"
        )

        overview_title.setStyleSheet("""
        font-size: 24px;
        color: #00c8ff;
        """)

        overview_layout.addWidget(
            overview_title
        )

        # STATUS CARDS
        cards_layout = QGridLayout()

        card1 = QLabel(
            "📷 Camera Protection\nACTIVE"
        )

        card2 = QLabel(
            "🙂 Face Recognition\nRUNNING"
        )

        card3 = QLabel(
            "🚨 Intruder Detection\nMONITORING"
        )

        card4 = QLabel(
            "🛡 System Status\nSECURE"
        )

        cards = [card1, card2, card3, card4]

        for card in cards:

            card.setAlignment(
                Qt.AlignmentFlag.AlignCenter
            )

            card.setMinimumHeight(120)

            card.setStyleSheet("""
            background-color: #101827;
            border-radius: 15px;
            font-size: 20px;
            padding: 20px;
            border: 2px solid #00c8ff;
            """)

        cards_layout.addWidget(card1, 0, 0)
        cards_layout.addWidget(card2, 0, 1)
        cards_layout.addWidget(card3, 1, 0)
        cards_layout.addWidget(card4, 1, 1)

        overview_layout.addLayout(cards_layout)

        overview_layout.addSpacing(20)

        # BUTTONS IN CENTER
        button_layout = QHBoxLayout()

        button_layout.addStretch()

        button_layout.addWidget(
            self.enable_btn
        )

        button_layout.addWidget(
            self.disable_btn
        )

        button_layout.addStretch()

        overview_layout.addLayout(
            button_layout
        )

        overview_layout.addSpacing(25)

        overview_layout.addWidget(
            self.camera_label
        )

        overview_page.setLayout(
            overview_layout
        )

        # =====================================================
        # WEBCAM PAGE
        # =====================================================

        webcam_page = QWidget()

        webcam_layout = QVBoxLayout()

        webcam_title = QLabel(
            "Webcam Protection"
        )

        webcam_title.setStyleSheet("""
        font-size: 24px;
        color: #00c8ff;
        """)

        webcam_layout.addWidget(
            webcam_title
        )

        webcam_layout.addSpacing(20)

        webcam_buttons = QHBoxLayout()

        webcam_buttons.addStretch()

        webcam_buttons.addWidget(
            self.enable_btn
        )

        webcam_buttons.addWidget(
            self.disable_btn
        )

        webcam_buttons.addStretch()

        webcam_layout.addLayout(
            webcam_buttons
        )

        webcam_layout.addSpacing(20)

        webcam_layout.addWidget(
            self.camera_label
        )

        webcam_page.setLayout(
            webcam_layout
        )

        # =====================================================
        # INTRUDER PAGE
        # =====================================================

        intruder_page = QWidget()

        intruder_layout = QVBoxLayout()

        intruder_title = QLabel(
            "Intruder Detection Gallery"
        )

        intruder_title.setStyleSheet("""
        font-size: 24px;
        color: #00c8ff;
        """)

        intruder_layout.addWidget(
            intruder_title
        )

        intruder_layout.addWidget(
            self.gallery
        )

        intruder_page.setLayout(
            intruder_layout
        )

        # =====================================================
        # FACE PAGE
        # =====================================================

        face_page = QWidget()

        face_layout = QVBoxLayout()

        face_title = QLabel(
            "Face Recognition System"
        )

        face_title.setStyleSheet("""
        font-size: 24px;
        color: #00c8ff;
        """)

        face_layout.addWidget(
            face_title
        )

        info = QLabel("""
Green Box  = Authorized User
Red Box    = Unknown Intruder
        """)

        info.setStyleSheet("""
        background-color: #101827;
        padding: 20px;
        border-radius: 10px;
        font-size: 18px;
        """)

        face_layout.addWidget(info)

        face_layout.addWidget(
            self.camera_label
        )

        face_page.setLayout(
            face_layout
        )

        # =====================================================
        # LOGS PAGE
        # =====================================================

        logs_page = QWidget()

        logs_layout = QVBoxLayout()

        logs_title = QLabel(
            "Logs & Monitoring"
        )

        logs_title.setStyleSheet("""
        font-size: 24px;
        color: #00c8ff;
        """)

        logs_layout.addWidget(
            logs_title
        )

        logs_layout.addWidget(
            self.logs_box
        )

        logs_page.setLayout(
            logs_layout
        )

        # =====================================================
        # SETTINGS PAGE
        # =====================================================
        # =====================================================
        # SETTINGS PAGE
        # =====================================================

        settings_page = QWidget()

        settings_layout = QVBoxLayout()

        settings_title = QLabel("Settings")

        settings_title.setStyleSheet("""
        font-size: 24px;
        color: #00c8ff;
        font-weight: bold;
        """)

        settings_layout.addWidget(settings_title)

        settings_layout.addSpacing(25)

        # =====================================================
        # CHANGE USERNAME BUTTON
        # =====================================================

        change_username_btn = QPushButton(
            "Change Username"
        )

        change_username_btn.setFixedHeight(60)

        change_username_btn.clicked.connect(
            self.change_username
        )

        # =====================================================
        # CHANGE PASSWORD BUTTON
        # =====================================================

        change_password_btn = QPushButton(
            "Change Password"
        )

        change_password_btn.setFixedHeight(60)

        change_password_btn.clicked.connect(
            self.change_password
        )

        # =====================================================
        # CREATE NEW USER BUTTON
        # =====================================================

        create_user_btn = QPushButton(
            "Create New User"
        )

        create_user_btn.setFixedHeight(60)

        create_user_btn.clicked.connect(
            self.create_new_user
        )

        # =====================================================
        # BUTTON STYLE
        # =====================================================

        buttons = [
            change_username_btn,
            change_password_btn,
            create_user_btn
        ]

        for btn in buttons:

            btn.setStyleSheet("""
            QPushButton {
                background-color: #00c8ff;
                color: black;
                border-radius: 12px;
                font-size: 16px;
                font-weight: bold;
                padding: 15px;
            }

            QPushButton:hover {
                background-color: #00ffff;
            }
            """)

        # =====================================================
        # ADD BUTTONS
        # =====================================================

        settings_layout.addWidget(
            change_username_btn
        )

        settings_layout.addSpacing(15)

        settings_layout.addWidget(
            change_password_btn
        )

        settings_layout.addSpacing(15)

        settings_layout.addWidget(
            create_user_btn
        )

        settings_layout.addStretch()

        settings_page.setLayout(
            settings_layout
        )

        # =====================================================
# WEBCAM SCHEDULER
# =====================================================

        settings_layout.addSpacing(30)

        schedule_title = QLabel(
            "Webcam Scheduler"
        )

        schedule_title.setStyleSheet("""
        font-size: 22px;
        color: #00c8ff;
        font-weight: bold;
        """)

        settings_layout.addWidget(
            schedule_title
        )

        # =====================================================
        # START TIME
        # =====================================================

        start_label = QLabel(
            "Start Time"
        )

        self.start_time = QTimeEdit()

        self.start_time.setDisplayFormat(
            "hh:mm AP"
        )

        self.start_time.setTime(
            QTime(9, 0)
        )

        self.start_time.setFixedHeight(50)

        settings_layout.addWidget(
            start_label
        )

        settings_layout.addWidget(
            self.start_time
        )

        # =====================================================
        # END TIME
        # =====================================================

        end_label = QLabel(
            "End Time"
        )

        self.end_time = QTimeEdit()

        self.end_time.setDisplayFormat(
            "hh:mm AP"
        )

        self.end_time.setTime(
            QTime(18, 0)
        )

        self.end_time.setFixedHeight(50)

        settings_layout.addWidget(
            end_label
        )

        settings_layout.addWidget(
            self.end_time
        )

        # =====================================================
        # ENABLE SCHEDULER BUTTON
        # =====================================================

        schedule_btn = QPushButton(
            "Enable Webcam Schedule"
        )

        schedule_btn.setFixedHeight(55)

        schedule_btn.clicked.connect(
            self.enable_schedule
        )

        settings_layout.addSpacing(15)

        settings_layout.addWidget(
            schedule_btn
        )   

       
        


        # =====================================================
        # ADD PAGES
        # =====================================================

        self.pages.addWidget(
            overview_page
        )

        self.pages.addWidget(
            webcam_page
        )

        self.pages.addWidget(
            intruder_page
        )

        self.pages.addWidget(
            face_page
        )

        self.pages.addWidget(
            logs_page
        )

        self.pages.addWidget(
            settings_page
        )

        # =====================================================
        # ADD TO RIGHT
        # =====================================================

        right_layout.addLayout(top_bar)

        right_layout.addSpacing(20)

        right_layout.addWidget(
            self.pages
        )

        # =====================================================
        # MAIN LAYOUT
        # =====================================================

        main_layout.addWidget(
            self.sidebar
        )

        main_layout.addLayout(
            right_layout
        )

        self.setLayout(main_layout)

        # =====================================================
        # LOAD DATA
        # =====================================================

        self.load_logs()

        self.load_intruder_gallery()

        # =====================================================
        # STYLES
        # =====================================================

        self.setStyleSheet("""

        QWidget {
            background-color: #07111f;
            color: white;
            font-family: Segoe UI;
            font-size: 15px;
        }

        QListWidget {
            background-color: #0d1b2a;
            border-radius: 15px;
            padding: 12px;
            border: 1px solid #00c8ff;
        }

        QListWidget::item {
            padding: 18px;
            margin: 8px;
            border-radius: 12px;
        }

        QListWidget::item:selected {
            background-color: #00c8ff;
            color: black;
            font-weight: bold;
        }

        QPushButton {
            background-color: #00c8ff;
            color: black;
            border-radius: 14px;
            font-size: 16px;
            font-weight: bold;
            padding: 14px;
        }

        QPushButton:hover {
            background-color: #00ffff;
        }

        QTextEdit {
            background-color: #101827;
            border-radius: 14px;
            padding: 15px;
            color: #00ff99;
            border: 1px solid #00c8ff;
            font-size: 15px;
        }

        QLabel {
            font-size: 18px;
            font-weight: bold;
        }

        QStackedWidget {
            background-color: #081120;
            border-radius: 15px;
        }

        """)

    # =====================================================
    # CHANGE PAGE
    # =====================================================

    def change_page(self, index):

        self.pages.setCurrentIndex(index)

    # =====================================================
    # ENABLE CAMERA
    # =====================================================

    def enable_webcam(self):

        if self.role != "admin":
            print("[ACCESS DENIED]")
            return

        # release lock if active
        if hasattr(self, "camera_lock") and self.camera_lock is not None:
            self.camera_lock.release()
            self.camera_lock = None

        if self.webcam.start_camera():
            self.timer.start(30)
            self.camera_label.setText("")
            self.status.setText("🟢 Camera Active")
            print("Webcam Started")


    def disable_webcam(self):

        # stop CamShield preview
        self.timer.stop()
        self.webcam.stop_camera()

        # lock camera safely by occupying it
        import cv2

        self.camera_lock = cv2.VideoCapture(
            0,
            cv2.CAP_DSHOW
        )

        self.camera_label.clear()
        self.camera_label.setText("Camera Locked & Protected")
        self.status.setText("🔴 Camera Locked")

        print("Camera locked safely")

    
        
    def disable_system_camera(self):

        import subprocess

        device_id = r"USB\VID_0C45&PID_6730&MI_00\6&30134149&0&0000"

        command = f'powershell -Command "Disable-PnpDevice -InstanceId \'{device_id}\' -Confirm:$false"'

        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True
        )

        print(result.stdout)
        print(result.stderr)


    def enable_system_camera(self):

        import subprocess

        device_id = r"USB\VID_0C45&PID_6730&MI_00\6&30134149&0&0000"

        command = f'powershell -Command "Enable-PnpDevice -InstanceId \'{device_id}\' -Confirm:$false"'

        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True
        )

        print(result.stdout)
        print(result.stderr)

    # =====================================================
    # REGISTER WINDOW
    # =====================================================

    def open_register_window(self):

        self.register_window.show()

        self.register_window.destroyed.connect(
            self.reload_faces
        )

    # =====================================================
    # LOAD FACES
    # =====================================================

    def load_known_faces(self):

        self.known_face_encodings.clear()

        self.known_face_names.clear()

        folder = "known_faces"

        if not os.path.exists(folder):

            os.makedirs(folder)

            return

        files = os.listdir(folder)

        print("[INFO] Loading Known Faces...")

        for file in files:

            path = os.path.join(folder, file)

            try:

                image = face_recognition.load_image_file(path)

                encodings = face_recognition.face_encodings(image)

                # CHECK FACE EXISTS
                if len(encodings) == 0:

                    print(f"[WARNING] No face found in {file}")

                    continue

                encoding = encodings[0]

                name = os.path.splitext(file)[0]

                self.known_face_encodings.append(
                    encoding
                )

                self.known_face_names.append(
                    name
                )

                print(f"[LOADED] {name}")

            except Exception as e:

                print(f"[ERROR] {file} -> {e}")

        print("[INFO] Faces Loaded Successfully")
        print(self.known_face_names)


    # =====================================================
    # RELOAD FACES
    # =====================================================

    def reload_faces(self):

        self.known_face_encodings.clear()

        self.known_face_names.clear()

        self.load_known_faces()

    # =====================================================
    # UPDATE FRAME
    # =====================================================

    def update_frame(self):

        if not self.webcam.camera:
            return

        ret, frame = self.webcam.camera.read()

        if not ret:
            return

        # ==========================================
        # RGB CONVERSION
        # ==========================================

        rgb_frame = cv2.cvtColor(
            frame,
            cv2.COLOR_BGR2RGB
        )

        # ==========================================
        # FACE DETECTION
        # ==========================================

        face_locations = face_recognition.face_locations(
            rgb_frame
        )

        face_encodings = face_recognition.face_encodings(
            rgb_frame,
            face_locations
        )

        face_names = []

        # ==========================================
        # LOOP THROUGH FACES
        # ==========================================

        for (
            (top, right, bottom, left),
            face_encoding
        ) in zip(face_locations, face_encodings):

            name = "Unknown"

            color = (0, 0, 255)

            # ==========================================
            # FACE MATCHING
            # ==========================================

            if len(self.known_face_encodings) > 0:

                matches = face_recognition.compare_faces(
                    self.known_face_encodings,
                    face_encoding,
                    tolerance=0.65
                )

                face_distances = face_recognition.face_distance(
                    self.known_face_encodings,
                    face_encoding
                )

                best_match_index = np.argmin(
                    face_distances
                )

                if matches[best_match_index]:

                    name = self.known_face_names[
                        best_match_index
                    ]

                    color = (0, 255, 0)

            # STORE DETECTED NAME
            face_names.append(name)

            # ==========================================
            # FACE BOX
            # ==========================================

            cv2.rectangle(
                frame,
                (left, top),
                (right, bottom),
                color,
                2
            )

            # ==========================================
            # LABEL BACKGROUND
            # ==========================================

            cv2.rectangle(
                frame,
                (left, bottom - 35),
                (right, bottom),
                color,
                cv2.FILLED
            )

            # ==========================================
            # NAME TEXT
            # ==========================================

            cv2.putText(
                frame,
                name,
                (left + 6, bottom - 6),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (255, 255, 255),
                2
            )

            # ==========================================
            # SAVE UNKNOWN ONLY ONCE
            # ==========================================

            if name == "Unknown":

                current_time = time.time()

                if (
                    current_time -
                    self.last_intruder_time
                ) > self.cooldown:

                    self.trigger_alert()

                    print("[INTRUDER DETECTED]")

                    # SAVE IMAGE
                    path = self.webcam.capture.save_snapshot(
                        frame
                    )

                    # SEND EMAIL
                    self.email_alert.send_intruder_alert(
                        path
                    )

                    # SAVE LOG
                    self.logger.log_intruder(path)

                    # REFRESH UI
                    self.load_logs()

                    self.load_intruder_gallery()

                    # UPDATE TIMER
                    self.last_intruder_time = current_time

        # ==========================================
        # DISPLAY FRAME
        # ==========================================

        rgb = cv2.cvtColor(
            frame,
            cv2.COLOR_BGR2RGB
        )

        h, w, ch = rgb.shape

        bytes_per_line = ch * w

        image = QImage(
            rgb.data,
            w,
            h,
            bytes_per_line,
            QImage.Format.Format_RGB888
        )

        pixmap = QPixmap.fromImage(image)

        self.camera_label.setPixmap(
            pixmap.scaled(
                self.camera_label.width(),
                self.camera_label.height(),
                Qt.AspectRatioMode.KeepAspectRatio
            )
        )

        # ==========================================
        # DEBUG
        # ==========================================

        if face_names:

            current_name = face_names[0]

            if current_name != self.last_detected_name:

                print("Detected:", current_name)

                self.last_detected_name = current_name

    # =====================================================
    # LOAD LOGS
    # =====================================================

    def load_logs(self):

        try:

            logs = self.logger.read_logs()

            self.logs_box.setPlainText(logs)

        except Exception as e:

            self.logs_box.setPlainText(
                f"Error loading logs:\n{e}"
            )

    # =====================================================
    # LOAD GALLERY
    # =====================================================

    def load_intruder_gallery(self):

        from app.security.encryption import EncryptionManager

        encryptor = EncryptionManager()

        folder = "intruders"

        if not os.path.exists(folder):
            return

        self.gallery.clear()

        files = sorted(
            os.listdir(folder),
            reverse=True
        )

        for file in files:

            path = os.path.join(folder, file)

            try:

                # DECRYPT IMAGE
                image_data = encryptor.decrypt_file(
                    path
                )

                pixmap = QPixmap()

                pixmap.loadFromData(image_data)

                if pixmap.isNull():
                    continue

                item = QListWidgetItem()

                icon = QIcon(
                    pixmap.scaled(
                        120,
                        120,
                        Qt.AspectRatioMode.KeepAspectRatio,
                        Qt.TransformationMode.SmoothTransformation
                    )
                )

                item.setIcon(icon)

                item.setText(file)

                self.gallery.addItem(item)

            except Exception as e:

                print(
                    f"[GALLERY ERROR] {file}: {e}"
                )

    # =====================================================
    # IMAGE PREVIEW
    # =====================================================

    def open_image_preview(self, item):

        from app.security.encryption import EncryptionManager

        encryptor = EncryptionManager()

        file_name = item.text()

        path = os.path.join(
            "intruders",
            file_name
        )

        try:

            # DECRYPT IMAGE
            image_data = encryptor.decrypt_file(
                path
            )

            pixmap = QPixmap()

            pixmap.loadFromData(image_data)

            dialog = QDialog(self)

            dialog.setWindowTitle(file_name)

            dialog.setFixedSize(900, 700)

            layout = QVBoxLayout()

            image_label = QLabel()

            image_label.setPixmap(
                pixmap.scaled(
                    850,
                    650,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                )
            )

            image_label.setAlignment(
                Qt.AlignmentFlag.AlignCenter
            )

            layout.addWidget(image_label)

            dialog.setLayout(layout)

            dialog.exec()

        except Exception as e:

            print(f"[PREVIEW ERROR] {e}")
    def open_register_window(self):
        self.register_window.show()

        self.register_window.destroyed.connect(
            self.reload_faces
        )


    def change_username(self):

        db_file = "database/users.json"

        # CURRENT USERNAME
        current_username, ok1 = QInputDialog.getText(
            self,
            "Current Username",
            "Enter current username:"
        )

        if not ok1 or not current_username:
            return

        # CURRENT PASSWORD
        current_password, ok2 = QInputDialog.getText(
            self,
            "Current Password",
            "Enter current password:"
        )

        if not ok2 or not current_password:
            return

        with open(db_file, "r") as file:

            users = json.load(file)

        # CHECK USER EXISTS
        if current_username not in users:

            QMessageBox.warning(
                self,
                "Error",
                "Username not found"
            )

            return

        stored_hash = users[current_username]["password"]

        import bcrypt

        # VERIFY PASSWORD
        if not bcrypt.checkpw(
            current_password.encode(),
            stored_hash.encode()
        ):

            QMessageBox.warning(
                self,
                "Error",
                "Incorrect password"
            )

            return

        # NEW USERNAME
        new_username, ok3 = QInputDialog.getText(
            self,
            "New Username",
            "Enter new username:"
        )

        if not ok3 or not new_username:
            return

        # UPDATE USERNAME
        users[new_username] = users.pop(current_username)

        with open(db_file, "w") as file:

            json.dump(users, file, indent=4)

        QMessageBox.information(
            self,
            "Success",
            "Username updated successfully"
        )
    def change_password(self):

        db_file = "database/users.json"

        # USERNAME
        username, ok1 = QInputDialog.getText(
            self,
            "Username",
            "Enter username:"
        )

        if not ok1 or not username:
            return

        # CURRENT PASSWORD
        current_password, ok2 = QInputDialog.getText(
            self,
            "Current Password",
            "Enter current password:"
        )

        if not ok2 or not current_password:
            return

        with open(db_file, "r") as file:

            users = json.load(file)

        # CHECK USER
        if username not in users:

            QMessageBox.warning(
                self,
                "Error",
                "User not found"
            )

            return

        stored_hash = users[username]["password"]

        import bcrypt

        # VERIFY OLD PASSWORD
        if not bcrypt.checkpw(
            current_password.encode(),
            stored_hash.encode()
        ):

            QMessageBox.warning(
                self,
                "Error",
                "Incorrect password"
            )

            return

        # NEW PASSWORD
        new_password, ok3 = QInputDialog.getText(
            self,
            "New Password",
            "Enter new password:"
        )

        if not ok3 or not new_password:
            return

        # HASH NEW PASSWORD
        hashed = bcrypt.hashpw(
            new_password.encode(),
            bcrypt.gensalt()
        ).decode()

        users[username]["password"] = hashed

        with open(db_file, "w") as file:

            json.dump(users, file, indent=4)

        QMessageBox.information(
            self,
            "Success",
            "Password updated successfully"
        )
    def create_new_user(self):

        from PyQt6.QtWidgets import QInputDialog, QMessageBox
        from app.auth.auth_system import AuthSystem
        from app.security.password_generator import generate_password
        from app.security.user_email import UserEmailSender

        username, ok1 = QInputDialog.getText(
            self,
            "Create New User",
            "Enter username:"
        )

        if not ok1 or not username:
            return

        email, ok2 = QInputDialog.getText(
            self,
            "User Email",
            "Enter user email:"
        )

        if not ok2 or not email:
            return

        password = generate_password()

        auth = AuthSystem()

        created = auth.create_user(
            username,
            password,
            email,
            "user"
        )

        if not created:
            QMessageBox.warning(
                self,
                "Error",
                "User already exists"
            )
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
                "User created and password sent to email"
            )

        except Exception as e:
            QMessageBox.warning(
                self,
                "Email Failed",
                f"User created, but email failed.\n\nPassword: {password}\n\nError: {e}"
            )
    def trigger_alert(self):

    # PLAY SOUND IN THREAD
        threading.Thread(
            target=playsound,
            args=("assets/sounds/alarm.wav",),
            daemon=True
        ).start()

        # POPUP ALERT
        QMessageBox.warning(
            self,
            "SECURITY ALERT",
            "Unknown Intruder Detected!"
        )
    # =====================================================
# ENABLE WEBCAM SCHEDULE
# =====================================================

    def enable_schedule(self):

        self.schedule_enabled = True

        QMessageBox.information(
            self,
            "Scheduler",
            "Webcam Schedule Enabled"
        )

        print("Webcam Scheduler Enabled")
    # =====================================================
# CHECK SCHEDULE
# =====================================================

    def check_schedule(self):

        if not self.schedule_enabled:
            return

        current_time = QTime.currentTime()

        start = self.start_time.time()

        end = self.end_time.time()

        # INSIDE TIME RANGE
        if start <= current_time <= end:

            if not self.webcam.camera:

                print("Schedule -> Camera ON")

                self.enable_webcam()

        # OUTSIDE TIME RANGE
        else:

            if self.webcam.camera:

                print("Schedule -> Camera OFF")

                self.disable_webcam()
        
   
    # =====================================================
# RUN APP
# =====================================================

if __name__ == "__main__":

    app = QApplication(sys.argv)

    window = CamShield("admin")

    window.show()

    sys.exit(app.exec())