import json
import os
from enum import Enum, StrEnum

import cv2
import numpy as np
from icecream import ic

from custom_logger import logger

IMAGE_DIR = "images/raw"
DATA_PATH = "images/images.json"

GRID_SIZE = 19
TRANSFORMED_SCREEN_SIZE = 2000
CELL_SIZE = TRANSFORMED_SCREEN_SIZE // GRID_SIZE
CORNERS_INDEXES = [0, 1, 2, 3]


class Color(Enum):
    RED = (0, 0, 255)
    GREEN = (0, 255, 0)
    BLUE = (255, 0, 0)
    MAGENTA = (255, 0, 255)
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)


class Cell(StrEnum):
    BLACK = "b"
    WHITE = "w"
    EMPTY = " "
    OCCLUSION = "o"


def save_data():
    with open(DATA_PATH, "w") as f:
        json.dump(data, f, indent=4)


image_names = [
    f
    for f in os.listdir(IMAGE_DIR)
    if os.path.isfile(os.path.join(IMAGE_DIR, f)) and not f.startswith(".")
]

data: dict

if not os.path.exists(DATA_PATH):
    with open(DATA_PATH, "w") as f:
        f.write("{}")

os.makedirs("images/black", exist_ok=True)
os.makedirs("images/white", exist_ok=True)
os.makedirs("images/empty", exist_ok=True)
os.makedirs("images/occlusion", exist_ok=True)


with open(DATA_PATH) as f:
    data = json.load(f)


# Add new images to data
for image_name in image_names:
    if data.get(image_name):
        continue

    data[image_name] = {"corners": [], "board": []}
    logger.info(f"Adding {image_name} to json")


save_data()

missing_labelling_file_names = [
    path for path, information in data.items() if not information["corners"]
]

default_mouse = [0, 0]
transformed_cell = [0, 0]
board = [[Cell.EMPTY for _ in range(CELL_SIZE)] for _ in range(CELL_SIZE)]
selected_color = Cell.EMPTY


def default_mouse_callback(event, x, y, flags, param):
    if event == cv2.EVENT_MOUSEMOVE:
        global default_mouse
        default_mouse = [x, y]


def transformed_mouse_callback(event, x, y, flags, param):
    if event == cv2.EVENT_MOUSEMOVE:
        global transformed_cell
        transformed_cell = [x // CELL_SIZE, y // CELL_SIZE]
    if event == cv2.EVENT_LBUTTONUP:
        global board

        board[transformed_cell[1]][transformed_cell[0]] = (
            selected_color
            if board[transformed_cell[1]][transformed_cell[0]] != selected_color
            else Cell.EMPTY
        )


cv2.namedWindow("Default")
cv2.namedWindow("Transformed")

cv2.setMouseCallback("Default", default_mouse_callback)
cv2.setMouseCallback("Transformed", transformed_mouse_callback)

ic(len(missing_labelling_file_names))
for image_name in missing_labelling_file_names:
    board = [[Cell.EMPTY for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
    selected_color = Cell.EMPTY
    selected_corner = None

    img = cv2.imread(f"{IMAGE_DIR}/{image_name}")

    down_scale_factor = 4
    x, y = (
        int(img.shape[1] // down_scale_factor),
        int(img.shape[0] // down_scale_factor),
    )

    left = x // 4
    right = x - x // 4
    top = y // 4
    bottom = y - y // 4
    corners = [
        [left, top],
        [right, top],
        [right, bottom],
        [left, bottom],
    ]

    # lags for original size
    resized_img = cv2.resize(img, (x, y))

    while True:
        display_img = resized_img.copy()
        key = cv2.waitKey(1) & 0xFF
        if key == ord("q"):
            data[image_name]["corners"] = [
                [corner[0] / display_img.shape[1], corner[1] / display_img.shape[0]]
                for corner in corners
            ]
            data[image_name]["board"] = board
            save_data()

            transformed_cell_size = 2000 // 19
            half_transformed_cell_size = transformed_cell_size // 8
            for y in range(GRID_SIZE):
                for x in range(GRID_SIZE):
                    cell = board[y][x]

                    if cell == Cell.BLACK.value:
                        folder = "black"
                    elif cell == Cell.WHITE.value:
                        folder = "white"
                    elif cell == Cell.OCCLUSION.value:
                        folder = "occlusion"
                    else:
                        folder = "empty"

                    cv2.imwrite(
                        f"images/{folder}/{image_name}_{x}_{y}.png",
                        transformed_img[
                            y * transformed_cell_size : (y + 1) * transformed_cell_size,
                            x * transformed_cell_size : (x + 1) * transformed_cell_size,
                        ],
                    )

            break

        color_mapping = {
            ord("b"): Cell.BLACK,
            ord("w"): Cell.WHITE,
            ord("o"): Cell.OCCLUSION,
        }

        if key in color_mapping:
            selected_color = (
                color_mapping[key].value
                if selected_color != color_mapping[key]
                else Cell.EMPTY.value
            )

        # selected point
        for index in CORNERS_INDEXES:
            if key == ord(str(index + 1)):
                selected_corner = index if selected_corner != index else None

        if selected_corner is not None:
            corners[selected_corner] = default_mouse

        # draw four points
        for index, corner in enumerate(corners):
            cv2.line(display_img, corner, corners[index - 1], Color.GREEN.value)

        # transform image
        matrix = cv2.getPerspectiveTransform(
            np.float32(
                [
                    [corner[0] * down_scale_factor, corner[1] * down_scale_factor]
                    for corner in corners
                ]
            ),
            np.float32(
                [
                    [0, 0],
                    [TRANSFORMED_SCREEN_SIZE, 0],
                    [TRANSFORMED_SCREEN_SIZE, TRANSFORMED_SCREEN_SIZE],
                    [0, TRANSFORMED_SCREEN_SIZE],
                ]
            ),
        )
        transformed_img = cv2.warpPerspective(
            img,
            matrix,
            (
                TRANSFORMED_SCREEN_SIZE,
                TRANSFORMED_SCREEN_SIZE,
            ),
        )
        display_transformed_img = transformed_img.copy()

        for i in range(GRID_SIZE):
            cv2.line(
                display_transformed_img,
                (0, i * CELL_SIZE),
                (TRANSFORMED_SCREEN_SIZE, i * CELL_SIZE),
                Color.GREEN.value,
            )
            cv2.line(
                display_transformed_img,
                (i * CELL_SIZE, 0),
                (i * CELL_SIZE, TRANSFORMED_SCREEN_SIZE),
                Color.GREEN.value,
            )
        x, y = 0, 0
        color = Color.BLACK.value

        for y in range(GRID_SIZE):
            for x in range(GRID_SIZE):
                cell = board[y][x]

                if cell == Cell.BLACK:
                    color = Color.BLACK.value
                elif cell == Cell.WHITE:
                    color = Color.WHITE.value
                elif cell == Cell.OCCLUSION:
                    color = Color.RED.value
                else:
                    color = None

                if color:
                    cv2.circle(
                        display_transformed_img,
                        (
                            x * CELL_SIZE + CELL_SIZE // 2,
                            y * CELL_SIZE + CELL_SIZE // 2,
                        ),
                        CELL_SIZE // 2,
                        color,
                        -1,
                    )
                    cv2.circle(
                        display_transformed_img,
                        (
                            x * CELL_SIZE + CELL_SIZE // 2,
                            y * CELL_SIZE + CELL_SIZE // 2,
                        ),
                        CELL_SIZE // 2,
                        Color.RED.value,
                        2,
                    )
        cv2.imshow("Default", display_img)

        cv2.imshow("Transformed", display_transformed_img)

cv2.destroyAllWindows()
