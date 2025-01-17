import os
import sys
import time
from copy import deepcopy
from datetime import datetime
from pathlib import Path

import cv2
from cv2.typing import MatLike

sys.path.append(str(Path(__file__).parent.parent.parent))

from src import CELL_SIZE, CORNER_INDEXES, IMG_PATH, SCREEN_SIZE
from src.utils.colors import Color
from src.utils.cv2_helper import add_grid, transform_frame

GAMES_PATH = IMG_PATH.joinpath("games")


def default_mouse_callback(event, x, y, flags, param):
    if event == cv2.EVENT_MOUSEMOVE:
        global default_mouse
        default_mouse = [x, y]


def setup_corners(cap: cv2.VideoCapture) -> list[list[int]]:
    x, y = 1920, 1080
    left = x // 4
    right = x - x // 4
    top = y // 4
    bottom = y - y // 4
    corners = [[left, top], [right, top], [right, bottom], [left, bottom]]

    selected_corner = None

    while True:
        key = cv2.waitKey(1) & 0xFF
        if key == ord("q"):
            break

        ret, frame = cap.read()
        display_img = deepcopy(frame)

        # Handling connecting issues with Iphone
        if not ret:
            time.sleep(2)
            continue

        display_img = cv2.resize(display_img, (x, y))

        for index in CORNER_INDEXES:
            if key == ord(str(index + 1)):
                selected_corner = index if selected_corner != index else None

        if selected_corner is not None:
            corners[selected_corner] = default_mouse

        for index, corner in enumerate(corners):
            cv2.line(display_img, corner, corners[index - 1], Color.GREEN.value)

        transformed_frame = transform_frame(frame, corners)
        display_transformed_frame = add_grid(transformed_frame)

        cv2.imshow("Default", display_img)
        cv2.imshow("Transformed", display_transformed_frame)
    cv2.destroyAllWindows()
    return corners


def main():
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        exit()

    cv2.namedWindow("Default")
    cv2.setMouseCallback("Default", default_mouse_callback)
    cv2.namedWindow("Transformed")

    corners = setup_corners(cap)

    frames = []
    total_count = 0
    count = 0

    run = datetime.now().strftime("%y%m%d%H%M")
    os.makedirs(f"images/{run}")

    while True:
        key = cv2.waitKey(1) & 0xFF
        if key == ord("q"):
            break

        _, frame = cap.read()
        transformed_frame = transform_frame(frame, corners)

        frames.append(transformed_frame)
        if count == 99:
            for i, frame in enumerate(frames):
                cv2.imwrite(f"{GAMES_PATH}/{run}/{total_count + i}.jpg", frame)
            print("Saving images", total_count + count)
            total_count += count
            count = 0
            frames = []
        else:
            count += 1

    cap.release()


if __name__ == "__main__":
    default_mouse = [0, 0]
    main()
