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

from src import CELL_SIZE, GRID_SIZE, HALF_CELL_SIZE, CORNER_INDEXES
from src.utils.colors import Color
from src.stone_classification import StoneClassifactionModel
from src.utils.cv2_helper import transform_frame, default_corners, add_grid

PATH = "weights/250107171701-classification_weights.pth"


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


def evaluate_board(model, frame: MatLike) -> list[int]:
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
    shape = (1920, 1080, 0)
    x, y, _ = shape
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
    model = StoneClassifactionModel()
    model.load_state_dict(torch.load(PATH, weights_only=True))

    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        exit()

    cv2.namedWindow("Default")
    cv2.setMouseCallback("Default", default_mouse_callback)
    cv2.namedWindow("Transformed")

    corners = setup_corners(cap)

    while True:
        key = cv2.waitKey(1) & 0xFF
        if key == ord("q"):
            break

        _, frame = cap.read()
        transformed_frame = transform_frame(frame, corners)

        blurred_image = cv2.GaussianBlur(transformed_frame, (5, 5), 0)
        kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]])
        sharpened_image = cv2.filter2D(blurred_image, -1, kernel)

        # resize image for pixel comparison
        # calculate percentage of pixel change
        # calculate moving average  30 frames

        # evaluate position if ma is smaller threshold

        # results = evaluate_board(model, sharpened_image)

        # if 1-2 stones added add -> add moves to game
        # case multiple stones added -> run simple evaluation
        # case add and remove stone -> run complex evaluation

    cap.release()


if __name__ == "__main__":
    default_mouse = [0, 0]
    main()
