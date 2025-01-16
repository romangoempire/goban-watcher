import sys
import time
from copy import deepcopy
from pathlib import Path
from datetime import datetime
import cv2
from fsspec.config import json
import numpy as np
import torch
import torchvision.transforms as transforms
from cv2.typing import MatLike
from icecream import ic

sys.path.append(str(Path(__file__).parent.parent))

from src import CELL_SIZE, END, GRID_SIZE, HALF_CELL_SIZE, HOSHIS, SCREEN_SIZE, START
from src.utils.colors import Color
from stone_classification import StoneClassifactionModel

PATH = "weights/250107171701-classification_weights.pth"
CORNERS_INDEXES = [0, 1, 2, 3]

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


# def display_results(cap: cv2.VideoCapture, model, corners: list) -> None:
#     pygame.init()
#     width, height = SCREEN_SIZE, SCREEN_SIZE

#     screen = pygame.display.set_mode((width, height))
#     pygame.display.set_caption("Evaluation")
#     clock = pygame.time.Clock()

#     running = True
#     while running:
#         for event in pygame.event.get():
#             if event.type == pygame.QUIT:
#                 running = False

#         _, frame = cap.read()
#         transformed_frame = transform_frame(frame, corners)
#         transformed_frame = add_grid(transformed_frame)
#         cv2.imshow("Transformed", transformed_frame)

#         results = evaluate_board(model, transformed_frame)
#         screen.fill(Color.BROWN.value)
#         screen = display_grid(screen)
#         screen = add_stones(screen, results)

#         pygame.display.flip()
#         clock.tick(2)

#     pygame.quit()


# def display_grid(screen) -> pygame.Surface:
#     # Lines
#     for x in range(GRID_SIZE):
#         increment = START + x * CELL_SIZE
#         width = 1
#         pygame.draw.line(
#             screen, Color.BLACK.value, [START, increment], [END, increment], width
#         )
#         pygame.draw.line(
#             screen, Color.BLACK.value, [increment, START], [increment, END], width
#         )

#     # Hoshi
#     for x in HOSHIS:
#         for y in HOSHIS:
#             pygame.draw.circle(
#                 screen,
#                 Color.BLACK.value,
#                 [
#                     CELL_SIZE // 2 + x * CELL_SIZE + 1,
#                     CELL_SIZE // 2 + y * CELL_SIZE + 1,
#                 ],
#                 5,
#             )
#     return screen


# def add_stones(screen: pygame.Surface, results: list) -> pygame.Surface:
#     for i, cell in enumerate(results):
#         if cell == 0:
#             continue

#         color = Color.BLACK.value if cell == 1 else Color.WHITE.value

#         x = i % 19
#         y = i // 19

#         pygame.draw.circle(
#             screen,
#             color,
#             [
#                 CELL_SIZE // 2 + x * CELL_SIZE + 1,
#                 CELL_SIZE // 2 + y * CELL_SIZE + 1,
#             ],
#             CELL_SIZE // 2,
#         )
#     return screen


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
