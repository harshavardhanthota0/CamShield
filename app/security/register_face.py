import cv2
import os


class FaceRegistrar:

    def __init__(self):

        # Create folder if missing
        if not os.path.exists("authorized_faces"):
            os.makedirs("authorized_faces")

    def register_user_face(self, username):

        camera = cv2.VideoCapture(0)

        print("Press SPACE to capture face")
        print("Press ESC to cancel")

        while True:

            ret, frame = camera.read()

            if not ret:
                print("Camera Error")
                break

            cv2.imshow("CamShield Face Registration", frame)

            key = cv2.waitKey(1)

            # SPACE KEY
            if key == 32:

                filename = f"authorized_faces/{username}.jpg"

                cv2.imwrite(filename, frame)

                print(f"Face Registered: {filename}")

                break

            # ESC KEY
            elif key == 27:
                break

        camera.release()

        cv2.destroyAllWindows()