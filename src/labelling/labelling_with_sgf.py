import json
from copy import deepcopy
from pathlib import Path

import cv2
import numpy as np
from tqdm import tqdm

from src import IMG_PATH, GRID_SIZE, CELL_SIZE, SCREEN_SIZE
from src.utils.colors import Color

MAX_EDGE_LENGTH = 2000
CORNER_INDEXES = [0, 1, 2, 3]


# METHODS

def adjust_image_size(img):
    while any([value > MAX_EDGE_LENGTH for value in img.shape]):
        img = cv2.resize(img, None, fx=0.5, fy=0.5)
    return img


def default_corners(shape: tuple[int, int, int]) -> list[list[int]]:
    """Corners should be a square in the middle of the image."""
    assert len(shape) == 3, "Invalid shape"
    y, x, _ = shape

    left = x // 4
    right = x - x // 4
    top = y // 4
    bottom = y - y // 4
    return [
        [left, top],
        [right, top],
        [right, bottom],
        [left, bottom],
    ]


def transform_image(img: np.ndarray, corners: list[list[int]]) -> np.ndarray:
    matrix = cv2.getPerspectiveTransform(
        np.float32([[c[0], c[1]] for c in corners]),
        np.float32(
            [
                [0, 0],
                [SCREEN_SIZE, 0],
                [SCREEN_SIZE, SCREEN_SIZE],
                [0, SCREEN_SIZE],
            ]
        ),
    )
    return cv2.warpPerspective(img, matrix, (SCREEN_SIZE, SCREEN_SIZE))


def draw_grid(img: np.ndarray) -> np.ndarray:
    for i in range(GRID_SIZE):
        cv2.line(
            img,
            (0, i * CELL_SIZE),
            (SCREEN_SIZE, i * CELL_SIZE),
            Color.GREEN.value,
        )
        cv2.line(
            img,
            (i * CELL_SIZE, 0),
            (i * CELL_SIZE, SCREEN_SIZE),
            Color.GREEN.value,
        )
    return img


def mouse_callback(event, x, y, flags, param):
    if event == cv2.EVENT_MOUSEMOVE:
        global mouse
        mouse = [x, y]


# MAIN

img_dir = IMG_PATH.joinpath("selected_sgf")
board_dir = IMG_PATH.joinpath("boards")
data_filename = Path(__file__).parent.joinpath("corners.json")

if data_filename.exists():
    with open(data_filename, "r") as f:
        data = json.load(f)
else:
    data = {}

image_paths = {
    str(i): [
        file for file in img_dir.joinpath(str(i)).iterdir()
        if file.is_file() and not file.name.startswith(".")
    ]
    for i in range(1, 21)
}

sgf_window_name = "sgf_image"
image_window_name = "image"
cv2.namedWindow(sgf_window_name)
cv2.namedWindow(image_window_name)
cv2.setMouseCallback(image_window_name, mouse_callback)

mouse = [0, 0]

for sgf_number, paths in tqdm(image_paths.items()):

    sgf_img = cv2.imread(str(board_dir.joinpath(f"game_{sgf_number}.png")))
    sgf_img = cv2.resize(sgf_img, (SCREEN_SIZE, SCREEN_SIZE))
    for image_path in tqdm(paths):
        if str(sgf_number) not in data.keys():
            data[sgf_number] = {}
        if data[sgf_number].get(image_path.name, None) is not None:
            continue

        board_img = cv2.imread(str(image_path))
        board_img = adjust_image_size(board_img)

        corners = default_corners(board_img.shape)

        selected_corner = None
        while True:
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                exit(0)
            elif key == ord('r'):
                board_img = cv2.rotate(board_img, cv2.ROTATE_90_CLOCKWISE)
                cv2.imwrite(image_path, board_img)
            elif key == ord('s'):
                percentage_corners = [
                    [corner[0] / board_img.shape[1], corner[1] / board_img.shape[0]]
                    for corner in corners
                ]
                data[sgf_number][image_path.name] = percentage_corners

                with open(data_filename, "w") as f:
                    json.dump(data, f, indent=4)
                break

            # change selected_corner if 1-4 is pressed
            for index in CORNER_INDEXES:
                if key == ord(str(index + 1)):
                    selected_corner = index if selected_corner != index else None

            # update corner position based on mouse position
            if selected_corner is not None:
                corners[selected_corner] = mouse

            # add rect using corners
            display_board_image = deepcopy(board_img)

            for index, corner in enumerate(corners):
                cv2.line(display_board_image, corner, corners[index - 1], Color.GREEN.value)

            transformed_img = transform_image(board_img, corners)
            transform_img = draw_grid(transformed_img)

            cv2.imshow(sgf_window_name, cv2.hconcat([sgf_img, transformed_img]))
            cv2.imshow(image_window_name, display_board_image)

cv2.destroyAllWindows()
