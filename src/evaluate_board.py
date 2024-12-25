import time
from copy import deepcopy

import cv2
import numpy as np
import pygame
import torch
import torchvision.transforms as transforms

from src import CELL_SIZE, GRID_SIZE, START, END, SCREEN_SIZE, HOSHIS
from stone_classification import StoneClassifactionModel

PATH = "weights/stone_classification_weights.pth"
CORNERS_INDEXES = [0, 1, 2, 3]

TRANSFORM = transforms.Compose(
    [
        transforms.ToPILImage(),  # Convert NumPy array to PIL Image
        transforms.Resize((CELL_SIZE, CELL_SIZE)),  # Resize to 105x105
        transforms.ToTensor(),  # Convert to tensor
        transforms.Normalize(mean=[0.5, 0.5, 0.5], std=[0.5, 0.5, 0.5]),  # Normalize
    ]
)

# colors
GREEN = [0, 255, 0]
BLACK = [0, 0, 0]
WHITE = [255, 255, 255]
BROWN = [245, 143, 41]


def default_mouse_callback(event, x, y, flags, param):
    if event == cv2.EVENT_MOUSEMOVE:
        global default_mouse
        default_mouse = [x, y]


def transform_frame(frame):
    global corners
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


def add_grid(frame):
    for i in range(GRID_SIZE):
        cv2.line(
            frame,
            (0, i * SCREEN_SIZE),
            (CELL_SIZE, i * CELL_SIZE),
            GREEN,
        )
        cv2.line(
            frame,
            (i * CELL_SIZE, 0),
            (i * CELL_SIZE, SCREEN_SIZE),
            GREEN,
        )
    return frame


def extract_cells(frame):
    transformed_cell_size = SCREEN_SIZE // GRID_SIZE
    half_cell_size = transformed_cell_size // 2

    return [
        frame[
        max(0, y * transformed_cell_size - half_cell_size): min(
            frame.shape[0],
            (y + 1) * transformed_cell_size + half_cell_size,
        ),
        max(0, x * transformed_cell_size - half_cell_size): min(
            frame.shape[1],
            (x + 1) * transformed_cell_size + half_cell_size,
        ),
        ]
        for y in range(GRID_SIZE)
        for x in range(GRID_SIZE)
    ]


def evaluate_board(frame) -> list[int]:
    cells = extract_cells(frame)
    tensor_images = torch.from_numpy(np.array([TRANSFORM(image) for image in cells]))
    outputs = net(tensor_images)
    _, predictions = torch.max(outputs, 1)
    return predictions.tolist()


def setup():
    global corners
    selected_corner = None

    while True:
        key = cv2.waitKey(1) & 0xFF
        if key == ord("q"):
            break

        ret, frame = cap.read()
        display_img = deepcopy(frame)

        # This can happen when connecting to and Iphone.
        # Usually it connects after few seconds
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
            cv2.line(display_img, corner, corners[index - 1], GREEN)

        transformed_frame = transform_frame(frame)
        display_transform_frame = deepcopy(transformed_frame)
        display_transform_frame = add_grid(display_transform_frame)

        cv2.imshow("Default", display_img)
        cv2.imshow("Transformed", display_transform_frame)

    cv2.destroyAllWindows()
    return corners


def display_results():
    global corners

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
        transformed_frame = transform_frame(frame)
        transformed_frame = add_grid(transformed_frame)
        cv2.imshow("Transformed", transformed_frame)
        results = evaluate_board(transformed_frame)
        screen.fill(BROWN)
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
        pygame.draw.line(screen, BLACK, [START, increment], [END, increment], width)
        pygame.draw.line(screen, BLACK, [increment, START], [increment, END], width)

    # Hoshi
    for x in HOSHIS:
        for y in HOSHIS:
            pygame.draw.circle(
                screen,
                BLACK,
                [
                    CELL_SIZE // 2 + x * CELL_SIZE + 1,
                    CELL_SIZE // 2 + y * CELL_SIZE + 1,
                ],
                5,
            )
    return screen


def add_stones(screen, results) -> pygame.Surface:
    for i, cell in enumerate(results):
        if cell == 0:
            continue

        color = BLACK if cell == 1 else WHITE

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


net = StoneClassifactionModel()
net.load_state_dict(torch.load(PATH, weights_only=True))

cap = cv2.VideoCapture(3)

if not cap.isOpened():
    exit()

cv2.namedWindow("Default")
cv2.setMouseCallback("Default", default_mouse_callback)
cv2.namedWindow("Transformed")

default_mouse = [0, 0]

x, y = (1920, 1080)
left = x // 4
right = x - x // 4
top = y // 4
bottom = y - y // 4
corners = [[left, top], [right, top], [right, bottom], [left, bottom]]

setup()
display_results()

cap.release()
