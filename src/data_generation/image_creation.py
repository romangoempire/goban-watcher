import os
import json
import time

import cv2
from icecream import ic

IMAGE_RAW_PATH = "../../images/raw"
DATA_PATH = "../../images/data.json"

with open(DATA_PATH, "r") as f:
    data = json.load(f)

os.makedirs(IMAGE_RAW_PATH, exist_ok=True)

cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("No camera found")
    exit()

while True:
    key = cv2.waitKey(1) & 0xFF

    if key == ord("q"):
        with open(DATA_PATH, "w") as f:
            json.dump(data, f, indent=4)
        exit()

    ret, frame = cap.read()

    if not ret:
        time.sleep(1)
        continue

    cv2.imshow("Image", frame)

    if key == ord("s"):
        cv2.imwrite(f"{IMAGE_RAW_PATH}/{data["next_image_number"]}.png", frame)
        data["next_image_number"] += 1
        with open(DATA_PATH, "w") as f:
            json.dump(data, f, indent=4)
cv2.destroyAllWindows()
cap.release()
