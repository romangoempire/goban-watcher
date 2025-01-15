import json
import os
from pathlib import Path
import sys
import time
from copy import deepcopy
from datetime import datetime

import cv2
import numpy as np
from cv2.typing import MatLike

sys.path.append(str(Path(__file__).parent.parent.parent))

from src import CELL_SIZE, SCREEN_SIZE
from src.utils.colors import Color

CORNERS_INDEXES = [0, 1, 2, 3]


def default_mouse_callback(event, x, y, flags, param):
    if event == cv2.EVENT_MOUSEMOVE:
        global default_mouse
        default_mouse = [x, y]


def add_grid(frame: MatLike) -> MatLike:
    for i in range(0, SCREEN_SIZE, CELL_SIZE):
        cv2.line(frame, (i, 0), (i, SCREEN_SIZE), Color.GREEN.value)
        cv2.line(frame, (0, i), (SCREEN_SIZE, i), Color.GREEN.value)
    return frame


def transform_frame(frame: MatLike, corners: list) -> MatLike:
    matrix = cv2.getPerspectiveTransform(
        np.float32([[corner[0], corner[1]] for corner in corners]),
        np.float32(
            [[0, 0], [SCREEN_SIZE, 0], [SCREEN_SIZE, SCREEN_SIZE], [0, SCREEN_SIZE]]
        ),
    )
    return cv2.warpPerspective(frame, matrix, (SCREEN_SIZE, SCREEN_SIZE))


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

        for index in CORNERS_INDEXES:
            if key == ord(str(index + 1)):
                selected_corner = index if selected_corner != index else None

        if selected_corner is not None:
            corners[selected_corner] = default_mouse

        for index, corner in enumerate(corners):
            cv2.line(display_img, corner, corners[index - 1], Color.GREEN.value)

        transformed_frame = transform_frame(frame, corners)
        display_transformed_frame = deepcopy(transformed_frame)
        display_transformed_frame = add_grid(display_transformed_frame)

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

    diffs = []
    frames = []
    last_frame = None
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

        blurred_image = cv2.GaussianBlur(transformed_frame, (5, 5), 0)
        kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]])
        sharpened_image = cv2.filter2D(blurred_image, -1, kernel)

        if last_frame is not None:
            diff = cv2.absdiff(last_frame, sharpened_image)
            diff_magnitude = np.linalg.norm(diff.astype(np.float32), axis=2)
            threshold = 50
            mask_above_threshold = diff_magnitude > threshold
            percentage_above_threshold = round(np.mean(mask_above_threshold) * 100, 4)

            show_diff = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
            cv2.imshow("Diff", show_diff)
            diffs.append(percentage_above_threshold)

        last_frame = sharpened_image
        frames.append(last_frame)
        if count > 100:
            for i, frame in enumerate(frames):
                cv2.imwrite(f"images/{run}/{total_count + i}.jpg", frame)
            print("Saving images", total_count + count)
            total_count += count
            count = 0
            frames = []
        count += 1
        # results = evaluate_board(model, transformed_frame)

    with open(f"data/{run}.json", "w") as f:
        json.dump(diffs, f, indent=4)
    cap.release()


if __name__ == "__main__":
    default_mouse = [0, 0]
    main()
