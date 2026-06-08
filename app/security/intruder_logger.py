import json
import os
from datetime import datetime


class IntruderLogger:

    def __init__(self):

        self.file = "database/intruders.json"

        os.makedirs("database", exist_ok=True)

        if not os.path.exists(self.file):

            with open(self.file, "w") as f:
                json.dump([], f)

    def log_intruder(self, image_path):

        with open(self.file, "r") as f:
            data = json.load(f)

        data.append({
            "image": image_path,
            "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })

        with open(self.file, "w") as f:
            json.dump(data, f, indent=4)

        print("Intruder Logged Successfully")