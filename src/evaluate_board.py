import time
from copy import deepcopy

import cv2
from cv2.typing import MatLike
import numpy as np
import pygame
import torch
import torchvision.transforms as transforms

from src import CELL_SIZE, GRID_SIZE, START, END, SCREEN_SIZE, HOSHIS
from src.utils.colors import Color
from stone_classification import StoneClassifactionModel

PATH = "weights/stone_classification_weights.pth"
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


def transform_frame(frame: MatLike, corners: list) -> MatLike:
    matrix = cv2.getPerspectiveTransform(
        np.float32([[corner[0], corner[1]] for corner in corners]),
        np.float32(
            [
                [0, 0],
                [SCREEN_SIZE, 0],
                [SCREEN_SIZE, SCREEN_SIZE],
                [0, SCREEN_SIZE],
            ]
        ),
    )
    return cv2.warpPerspective(
        frame,
        matrix,
        (
            SCREEN_SIZE,
            SCREEN_SIZE,
        ),
    )


def add_grid(frame: MatLike) -> MatLike:
    for i in range(GRID_SIZE):
        cv2.line(
            frame,
            (0, i * SCREEN_SIZE),
            (CELL_SIZE, i * CELL_SIZE),
            Color.GREEN.value,
        )
        cv2.line(
            frame,
            (i * CELL_SIZE, 0),
            (i * CELL_SIZE, SCREEN_SIZE),
            Color.GREEN.value,
        )
    return frame


def extract_cells(frame: MatLike) -> list:
    transformed_cell_size = SCREEN_SIZE // GRID_SIZE
    half_cell_size = transformed_cell_size // 2

    low = transformed_cell_size - half_cell_size
    high = transformed_cell_size + half_cell_size
    return [
        frame[
            max(0, y * low) : min(frame.shape[0], (y + 1) * high),
            max(0, x * low) : min(frame.shape[1], (x + 1) * high),
        ]
        for y in range(GRID_SIZE)
        for x in range(GRID_SIZE)
    ]


def evaluate_board(model, frame: MatLike) -> list[int]:
    cells = extract_cells(frame)
    tensor_images = torch.from_numpy(np.array([TRANSFORM(image) for image in cells]))
    outputs = model(tensor_images)
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


def display_results(cap: cv2.VideoCapture, model, corners: list) -> None:
    pygame.init()
    width, height = 800, 800

    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption("Evaluation")
    clock = pygame.time.Clock()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        _, frame = cap.read()
        transformed_frame = transform_frame(frame, corners)
        transformed_frame = add_grid(transformed_frame)
        cv2.imshow("Transformed", transformed_frame)

        results = evaluate_board(model, transformed_frame)
        screen.fill(Color.BROWN.value)
        screen = display_grid(screen)
        screen = add_stones(screen, results)

        pygame.display.flip()
        clock.tick(2)

    pygame.quit()


def display_grid(screen) -> pygame.Surface:
    # Lines
    for x in range(GRID_SIZE):
        increment = START + x * CELL_SIZE
        width = 1
        pygame.draw.line(
            screen, Color.BLACK.value, [START, increment], [END, increment], width
        )
        pygame.draw.line(
            screen, Color.BLACK.value, [increment, START], [increment, END], width
        )

    # Hoshi
    for x in HOSHIS:
        for y in HOSHIS:
            pygame.draw.circle(
                screen,
                Color.BLACK.value,
                [
                    CELL_SIZE // 2 + x * CELL_SIZE + 1,
                    CELL_SIZE // 2 + y * CELL_SIZE + 1,
                ],
                5,
            )
    return screen


def add_stones(screen: pygame.Surface, results: list) -> pygame.Surface:
    for i, cell in enumerate(results):
        if cell == 0:
            continue

        color = Color.BLACK.value if cell == 1 else Color.WHITE.value

        x = i % 19
        y = i // 19

        pygame.draw.circle(
            screen,
            color,
            [
                CELL_SIZE // 2 + x * CELL_SIZE + 1,
                CELL_SIZE // 2 + y * CELL_SIZE + 1,
            ],
            CELL_SIZE // 2,
        )
    return screen


def main():
    model = StoneClassifactionModel()
    model.load_state_dict(torch.load(PATH, weights_only=True))

    cap = cv2.VideoCapture(3)

    if not cap.isOpened():
        exit()

    cv2.namedWindow("Default")
    cv2.setMouseCallback("Default", default_mouse_callback)
    cv2.namedWindow("Transformed")

    corners = setup_corners(cap)
    display_results(cap, model, corners)

    cap.release()


if __name__ == "__main__":
    default_mouse = [0, 0]
    main()
