import time
from enum import IntEnum, auto

import cv2
import numpy as np
from cv2.typing import MatLike
from icecream import ic
from custom_logger import logger


PERCENTAGE_THRESHOLD = 1.0
GRID_SIZE = 19


class Cell(IntEnum):
    EMPTY = 0
    BLACK = auto()
    WHITE = auto()


class Game:
    def __init__(self):
        self.move: int = 0
        self.is_ko: bool = False
        self.captured_black: int = 0
        self.captured_white: int = 0
        self.board = [[Cell.EMPTY for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]

    def print_board(self) -> None:
        symbols = {
            Cell.EMPTY.value: "-",
            Cell.BLACK.value: "X",
            Cell.WHITE.value: "0",
        }
        for y in range(GRID_SIZE):
            for x in range(GRID_SIZE):
                cell = self.board[y][x].value
                print(symbols[cell], end=" ")
            print()

    def add_move(self, x, y) -> None:
        current_color, opponent_color = (
            (Cell.BLACK, Cell.WHITE) if self.move % 2 == 0 else (Cell.WHITE, Cell.BLACK)
        )

        assert self.board[y][x] == Cell.EMPTY.value, f"x: {x} y: {y} is not empty"
        neighbors = self.get_neighbors(x, y)
        visited = set()

        for neighbor in neighbors:
            x, y = neighbor

            if self.board[y][x] == opponent_color:
                self.remove_stones(x, y)

        assert not self.suicide(x, y), "Suicide"

        self.board[y][x] = current_color
        self.move += 1

    def get_neighbors(self, x, y) -> list:
        return [
            (x - 1, y),
            (x + 1, y),
            (x, y - 1),
            (x, y + 1),
        ]


def changed_percentage(last_frame, frame) -> tuple[float, MatLike]:
    difference = cv2.absdiff(last_frame, frame)
    gray_difference = cv2.cvtColor(difference, cv2.COLOR_BGR2GRAY)
    _, binary_difference = cv2.threshold(gray_difference, 30, 255, cv2.THRESH_BINARY)
    total_pixels = binary_difference.size
    changed_pixels = np.count_nonzero(binary_difference)
    percent_changed = round((changed_pixels / total_pixels) * 100, 1)
    return percent_changed, binary_difference


def main():
    cap = cv2.VideoCapture(1)

    if not cap.isOpened():
        logger.fatal("Could not open camera.")
        exit()

    last_frame = None
    last_percentage = 0

    return
    while True:
        # stop application when "q" is pressed
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

        ret, frame = cap.read()

        # This can happen somethings when connecting to the iphone.
        # Usually it connects after few seconds
        if not ret:
            logger.warning("Could not read frame")
            time.sleep(2)
            continue

        if last_frame is None:
            last_frame = frame

        percent_changed, binary_difference = changed_percentage(last_frame, frame)
        movement_last_frame = last_percentage > PERCENTAGE_THRESHOLD
        movement_this_frame = percent_changed > PERCENTAGE_THRESHOLD
        last_percentage = last_percentage

        if movement_last_frame and not movement_this_frame:
            pass
            # save image to recording
            # transform image to top down with 4 points
            # split into each intersection
            # predict each intersection

            # get difference between board and predicted board
            # validate that position is possible
            # if new position is valid
            #   if black_turn -> one new black stones (and potential white stones disappear)
            #   else -> one new white stone (and  potential white stones disappear)
            # elif: check if the position is valid if you ignore the last position (a move was wrong before)
            #   get the move that changed, remove it and add the new move instead
            #   check if th new move is possible with the rest of the moves
            #

        ic(percent_changed)
        cv2.imshow("Original Frame", frame)
        cv2.imshow("Change", binary_difference)

        last_frame = frame

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    game = Game()
    game.print_board()
    game.add_move(3, 3)
    print()
    game.print_board()
    game.add_move(2, 2)
    print()
    game.print_board()
