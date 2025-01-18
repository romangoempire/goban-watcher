import sys
import time
from copy import deepcopy
from pathlib import Path

import cv2
import numpy as np
import torch
import torchvision.transforms as transforms
from cv2.typing import MatLike

sys.path.append(str(Path(__file__).parent.parent))

from src import CELL_SIZE, CORNER_INDEXES, GRID_SIZE, HALF_CELL_SIZE
from src.stone_classification import StoneClassifactionModel
from src.utils.colors import Color
from src.utils.custom_logger import get_color_logger
from src.utils.cv2_helper import (
    add_grid,
    blur_and_sharpen,
    default_corners,
    transform_frame,
)
from src.utils.pixel_changes import percentage_pixel_changed

PATH = "weights/250107171701-classification_weights.pth"
AMOUNT_FRAMES_MOVING_AVERAGE = 30

TRANSFORM = transforms.Compose(
    [
        transforms.ToPILImage(),
        transforms.Resize((CELL_SIZE, CELL_SIZE)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.5, 0.5, 0.5], std=[0.5, 0.5, 0.5]),
    ]
)


def default_mouse_callback(event, x, y, flags, param):
    if event == cv2.EVENT_MOUSEMOVE:
        global default_mouse
        default_mouse = [x, y]


def classify_all_cells(model, frame: MatLike) -> list[int]:
    low_offsets = np.arange(0, GRID_SIZE) * CELL_SIZE - HALF_CELL_SIZE
    high_offsets = np.arange(1, GRID_SIZE + 1) * CELL_SIZE + HALF_CELL_SIZE

    low_offsets = np.clip(low_offsets, 0, frame.shape[0])
    high_offsets = np.clip(high_offsets, 0, frame.shape[1])

    cells = np.array(
        [
            TRANSFORM(
                frame[
                    low_offsets[y] : high_offsets[y], low_offsets[x] : high_offsets[x]
                ]
            )
            for y in range(GRID_SIZE)
            for x in range(GRID_SIZE)
        ]
    )

    outputs = model(torch.from_numpy(cells))
    _, predictions = torch.max(outputs, 1)
    return predictions.tolist()


def setup_corners(cap: cv2.VideoCapture) -> list[list[int]]:
    shape = (1080, 1920, 0)
    y, x, _ = shape
    corners = default_corners(shape)

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
    logger = get_color_logger()
    model = StoneClassifactionModel()
    model.load_state_dict(torch.load(PATH, weights_only=True))

    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        exit()

    cv2.namedWindow("Default")
    cv2.setMouseCallback("Default", default_mouse_callback)
    cv2.namedWindow("Transformed")

    corners = setup_corners(cap)

    threshold = 0.01
    moving_average = None
    last_img = None
    high_movement = False

    percentage_changes = []

    while True:
        key = cv2.waitKey(1) & 0xFF
        if key == ord("q"):
            break

        _, frame = cap.read()
        img = transform_frame(frame, corners)
        img = blur_and_sharpen(img)

        if last_img is None:
            last_img = img
            continue

        percent_changed = percentage_pixel_changed(last_img, img)
        percentage_changes.append(percent_changed)

        if len(percentage_changes) == AMOUNT_FRAMES_MOVING_AVERAGE:
            moving_average = sum(percentage_changes) / AMOUNT_FRAMES_MOVING_AVERAGE
            percentage_changes.pop(0)

        if not moving_average:
            continue

        # High movement
        if percent_changed > threshold and percent_changed > moving_average:
            logger.debug("High Movement")
            high_movement = True

        # After movement
        if percent_changed < threshold and moving_average > threshold and high_movement:
            logger.info("End High Movement")
            high_movement = False
            results = classify_all_cells(model, img)
            for i in range(GRID_SIZE):
                logger.info(results[i * GRID_SIZE : i * GRID_SIZE + GRID_SIZE])

            # if 1-2 stones added add -> add moves to game
            # case multiple stones added -> run simple evaluation
            # case add and remove stone -> run complex evaluation
        last_img = img

    cap.release()


if __name__ == "__main__":
    default_mouse = [0, 0]
    main()
