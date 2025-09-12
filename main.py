import argparse
import json
import os
import time
from copy import deepcopy
from pathlib import Path

import cv2
import numpy as np
from cv2.typing import MatLike

from src import (
    CELL_SIZE,
    CORNER_INDEXES,
    GRID_SIZE,
    HALF_CELL_SIZE,
    HOSHIS,
    SCREEN_SIZE,
)
from src.stone_classification import load_rf
from src.utils.colors import Color
from src.utils.custom_logger import get_color_logger
from src.utils.cv2_helper import (
    add_grid,
    blur_and_sharpen,
    convert_to_top_down,
    default_corners,
)
from src.utils.game import Cell, Game
from src.utils.katago_helper import get_best_variation, start_katago_process

RF_PATH = "weights/random_forest_model.pkl"
BACKUP_PATH_CORNERS = "backup/corners.json"

AMOUNT_IDENTICAL_IMAGES = 15


def default_mouse_callback(event, x, y, flags, param):
    if event == cv2.EVENT_MOUSEMOVE:
        global default_mouse
        default_mouse = [x, y]


def setup_corners(cap: cv2.VideoCapture) -> list[list[int]]:
    shape = (1080, 1920, 0)
    y, x, _ = shape
    corners = default_corners(shape)

    selected_corner = None

    while True:
        key = cv2.waitKey(1) & 0xFF
        if key == ord("q"):
            break
        if key == ord("r"):
            logger.debug("Reset corners")
            corners = default_corners(shape)
            continue
        # TODO(2025-09-12 15:09:30): Maybe add "l" to load corners instead of passing a cli flag?
        if key == ord("s"):
            save_corners_to_file(corners)
            continue

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

        transformed_frame = convert_to_top_down(frame, corners)
        display_transformed_frame = add_grid(transformed_frame)

        cv2.imshow("Default", display_img)
        cv2.imshow("Transformed", display_transformed_frame)
    cv2.destroyAllWindows()
    return corners


def save_corners_to_file(corners: list[list[int]]) -> None:
    os.makedirs("backup", exist_ok=True)
    with open(BACKUP_PATH_CORNERS, "w") as f:
        json.dump(corners, f, indent=4)
    logger.info(f"Saved corners to: {BACKUP_PATH_CORNERS}")


def try_to_load_corners_from_file() -> list[list[int]] | None:
    if not Path.exists(Path(BACKUP_PATH_CORNERS)):
        logger.warning(
            f"No corner backup found in: {BACKUP_PATH_CORNERS}. Manual setup required"
        )
        return None
    with open(BACKUP_PATH_CORNERS) as f:
        return json.load(f)


def classify_all_cells(model, frame: MatLike) -> list[Cell]:
    low_offsets = np.arange(0, GRID_SIZE) * CELL_SIZE - HALF_CELL_SIZE
    high_offsets = np.arange(1, GRID_SIZE + 1) * CELL_SIZE + HALF_CELL_SIZE

    low_offsets = np.clip(low_offsets, 0, frame.shape[0])
    high_offsets = np.clip(high_offsets, 0, frame.shape[1])

    cells = np.array(
        [
            cv2.resize(
                frame[
                    low_offsets[y] : high_offsets[y], low_offsets[x] : high_offsets[x]
                ],
                (CELL_SIZE, CELL_SIZE),
            ).flatten()
            for y in range(GRID_SIZE)
            for x in range(GRID_SIZE)
        ]
    )

    results = model.predict(cells)
    results = [Cell(r) for r in results]

    return results


def base_visual_board() -> MatLike:
    frame = np.full((SCREEN_SIZE, SCREEN_SIZE, 3), Color.BROWN.value, dtype=np.uint8)

    # draw lines
    for i in range(GRID_SIZE):
        start = HALF_CELL_SIZE
        end = SCREEN_SIZE - HALF_CELL_SIZE
        height = i * CELL_SIZE + HALF_CELL_SIZE
        frame = cv2.line(frame, (start, height), (end, height), Color.BLACK.value, 1)
        frame = cv2.line(frame, (height, start), (height, end), Color.BLACK.value, 1)

    # draw hoshis
    for x in HOSHIS:
        for y in HOSHIS:
            frame = cv2.circle(
                frame,
                (HALF_CELL_SIZE + x * CELL_SIZE, HALF_CELL_SIZE + y * CELL_SIZE),
                int(CELL_SIZE * 0.1),
                Color.BLACK.value,
                -1,
            )
    return frame


def add_stones_to_visual(frame, board: list[list[Cell]]) -> None:
    for col in range(GRID_SIZE):
        for row in range(GRID_SIZE):
            cell = board[col][row].value
            if cell == 1:
                color = Color.BLACK.value
            elif cell == 2:
                color = Color.WHITE.value
            else:
                color = None

            if color:
                frame = cv2.circle(
                    frame,
                    (
                        HALF_CELL_SIZE + CELL_SIZE * row,
                        HALF_CELL_SIZE + CELL_SIZE * col,
                    ),
                    HALF_CELL_SIZE,
                    color,
                    -1,
                )
    return frame


def diff_between_boards(current_board: list[list[Cell]], new_board: list[Cell]) -> list:
    diff = []
    for i in range(len(new_board)):
        col = i // GRID_SIZE
        row = i % GRID_SIZE
        current_cell = current_board[col][row]
        new_cell = new_board[i]

        if current_cell != new_cell:
            diff.append(
                {"position": (row, col), "current": current_cell, "new": new_cell}
            )

    return diff


def main() -> None:
    parser = argparse.ArgumentParser(description="Example CLI with argparse")
    parser.add_argument(
        "-c", "--camera", type=int, default=0, help="Camera index. Starts at 0"
    )
    parser.add_argument(
        "--enable-katago",
        action="store_true",
        default=False,
        dest="use_katago",
        help="Activates KataGo for move reconstruction",
    )
    parser.add_argument(
        "--identical-frames",
        type=int,
        default=AMOUNT_IDENTICAL_IMAGES,
        help="Amount of identical frames required to trigger stone evaluation. Default is 15 for 30fps -> 0.5s",
    )
    parser.add_argument(
        "--use-saved-corners",
        action="store_true",
        default=True,
        dest="use_saved_corners",  # optional: name the positive concept
        help='Uses saved corners instead of manual setup. Press "r" after manual setup is done to save corners',
    )
    args = parser.parse_args()

    logger.info(f"Using Camera {args.camera}")
    cap = cv2.VideoCapture(args.camera)
    if not cap.isOpened():
        logger.error("Camera could not be openend")
        exit(1)

    cv2.namedWindow("Default")
    cv2.setMouseCallback("Default", default_mouse_callback)
    cv2.namedWindow("Transformed")

    corners = None
    if args.use_saved_corners:
        corners = try_to_load_corners_from_file()

    if corners:
        logger.info("Corner backup found and loaded")
    else:
        corners = setup_corners(cap)

    model = load_rf(RF_PATH)
    katago_process = None
    if args.use_katago:
        katago_process = start_katago_process()

    visual_board = base_visual_board()

    last_results = []
    changelog = []

    game = Game()

    while True:
        key = cv2.waitKey(1) & 0xFF
        if key == ord("q"):
            break

        _, frame = cap.read()
        img = convert_to_top_down(frame, corners)
        img = blur_and_sharpen(img)
        results = classify_all_cells(model, img)

        last_results.append(results)

        visual = add_stones_to_visual(visual_board.copy(), game.board)
        complete = np.hstack((img, visual))  # type: ignore #
        cv2.imshow("Complete", complete)

        # last_results are empty at the start and have to be filled up at the start
        # this initialisation process is ignored and the recording only starts
        # when enough frames exists to be compared
        if len(last_results) < args.identical_frames:
            continue
        # remove oldest result
        last_results.pop(0)

        current_player, opponent_player = game.current_and_opponent_color()

        # new state is idential to all past states => no movement
        if all(r == results for r in last_results):
            changes = diff_between_boards(game.board, results)

            if not changes:
                continue

            changelog += changes

            # single new move
            if (
                len(changes) == 1
                and changes[0]["current"] == Cell.EMPTY.value
                and changes[0]["new"] == current_player
            ):
                position = changes[0]["position"]
                if game.is_empty(position):
                    logger.info(f"New Move: {changes[0]['new']} - {position}")
                    game.add_move(*position)
                    continue
                else:
                    logger.fatal(f"Illegal Move: {changes[0]['new']} - {position}")

            # two new moves
            if (
                len(changes) == 2
                and all(d["current"] == 0 for d in changes)  # only additions
                # one move of each color
                and set([changes[0]["new"], changes[1]["new"]])
                == set([Cell.BLACK.value, Cell.WHITE.value])
            ):
                logger.info("Two Moves")
                ordered_changes = (
                    changes if changes[0]["new"] == current_player else changes[::-1]
                )
                for c in ordered_changes:
                    logger.info(f"Move: {c['new']} - {c['position']}")
                    game.add_move(*c["position"])
                continue

            # capture happended. One new move of current_player and 1+ removals of opponent
            moves_added = [c for c in changes if c["current"] == 0]
            moves_removed = [c for c in changes if c["new"] == 0]
            removed_colors = set([rm["current"] for rm in moves_removed])
            if (
                len(moves_added) == 1
                and moves_added[0]["new"] == current_player
                and len(removed_colors) == 1
                and moves_removed[0]["current"] == opponent_player
            ):
                new_move = moves_added[0]
                logger.info(
                    f"Move (Capture): {new_move['new']} - {new_move['position']}"
                )
                game.add_move(*new_move["position"])
                continue

            # multiple moves added
            if katago_process:
                valid_addition = all(c["current"] == Cell.EMPTY for c in changes)
                amount_player_stones = len(
                    [c["new"] for c in changes if c["new"] == current_player]
                )
                amount_opponent_stones = len(
                    [c["new"] for c in changes if c["new"] == opponent_player]
                )
                # New moves must be evenly distributed a
                valid_offset = [0, 1]
                valid_amounts = (
                    amount_player_stones - amount_opponent_stones in valid_offset
                )

                if (
                    valid_addition
                    and valid_amounts
                    and 1 < len(moves_added) < 9
                    and len(moves_removed) == 0
                ):
                    logger.info(
                        "Multiple new moves. Using katago to guess the correct sequence"
                    )
                    new_moves = []
                    for new_move in moves_added:
                        new_moves.append((new_move["new"], new_move["position"]))

                    sequence = get_best_variation(
                        katago_process,
                        game.board,
                        new_moves,
                        current_player,
                    )
                    for move in sequence:
                        color, position = move
                        logger.info(f"Move: {color} - {position}")
                        game.add_move(*position)
                    continue

            # Chaos. Possible reasons:
            # A -> capture and moves after
            # B -> capture and stone was moved or wrongly recognized at the start
            # C -> illegal moves
            if len(moves_added) > 0 or len(moves_removed) > 0:
                logger.warning(
                    "Game State changed drastically! Unable to extract sequence and therefore updating the board as whole to the new state"
                )
                game.board = [
                    results[i * GRID_SIZE : i * GRID_SIZE + GRID_SIZE]
                    for i in range(GRID_SIZE)
                ]

    cap.release()

    # TODO(2025-09-12 14:09:28): use sgf instead. Probably you want to save to sgf directly on each change
    logger.info("Changelog:")
    for move in changelog:
        logger.info(move)

    if katago_process:
        katago_process.terminate()


if __name__ == "__main__":
    default_mouse = [0, 0]

    logger = get_color_logger()
    main()
