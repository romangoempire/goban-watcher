import json
import os
import time
from datetime import datetime

import cv2

from custom_logger import logger

IMAGE_PATH = "images/raw"
IMAGE_INFO_PATH = "images/images.json"

MAX_HEIGHT: int = 4
MAX_POSITION: int = 5


def open_image_info() -> dict:
    os.makedirs(IMAGE_PATH, exist_ok=True)

    if not os.path.exists(IMAGE_INFO_PATH):
        with open(IMAGE_INFO_PATH, "w") as f:
            json.dump({}, f)

    with open(IMAGE_INFO_PATH) as f:
        return json.load(f)


def main() -> None:
    info_dict = open_image_info()
    cap: cv2.VideoCapture = cv2.VideoCapture(3)

    position: int = 0
    height: int = 0
    last_file_name = list(info_dict.keys())[-1]
    current_set: int = info_dict[last_file_name]["set"] + 1 if info_dict.keys() else 0

    if not cap.isOpened():
        logger.fatal("Could not open camera")
        exit()

    while True:
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

        ret, frame = cap.read()

        if not ret:
            logger.warning("Could not read frame")
            time.sleep(2)
            continue

        display_frame = frame.copy()
        cv2.putText(
            display_frame,
            f"S: {current_set}",
            (50, 50),
            cv2.FONT_HERSHEY_DUPLEX,
            1,
            (255, 255, 255),
            2,
        )
        cv2.putText(
            display_frame,
            f"P: {position}",
            (50, 80),
            cv2.FONT_HERSHEY_DUPLEX,
            1,
            (255, 255, 255),
            2,
        )
        cv2.putText(
            display_frame,
            f"H: {height}",
            (50, 110),
            cv2.FONT_HERSHEY_DUPLEX,
            1,
            (255, 255, 255),
            2,
        )
        cv2.imshow("Image", display_frame)

        if cv2.waitKey(1) & 0xFF == ord("s"):
            file_name: str = f"{current_set}_{position}_{height}.png"
            info_dict[file_name] = {
                "set": current_set,
                "position": position,
                "height": height,
                "creation_timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "corners": [],
                "board": [],
            }
            cv2.imwrite(os.path.join(IMAGE_PATH, file_name), frame)

            height += 1
            if height >= MAX_HEIGHT:
                height = 0
                position += 1

            if position >= MAX_POSITION:
                position = 0
                current_set += 1

            with open(IMAGE_INFO_PATH, "w") as f:
                json.dump(info_dict, f, indent=4)

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
