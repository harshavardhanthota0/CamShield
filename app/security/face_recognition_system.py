import face_recognition
import cv2


class FaceRecognitionSystem:

    def __init__(self):
        self.known_encodings = []
        self.known_names = []

    def load_face(self, image_path, name):

        image = face_recognition.load_image_file(image_path)
        encoding = face_recognition.face_encodings(image)[0]

        self.known_encodings.append(encoding)
        self.known_names.append(name)

    def detect_face(self, frame):

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        locations = face_recognition.face_locations(rgb)
        encodings = face_recognition.face_encodings(rgb, locations)

        names = []

        for encoding in encodings:

            matches = face_recognition.compare_faces(self.known_encodings, encoding)

            name = "Unknown"

            if True in matches:
                match_index = matches.index(True)
                name = self.known_names[match_index]

            names.append(name)

        return locations, names