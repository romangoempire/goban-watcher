from enum import IntEnum, auto

from icecream import ic
from copy import deepcopy

from src import GRID_SIZE


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
        self.board_history: list = []
        self.board = [[Cell.EMPTY for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]

    def reset(self) -> None:
        self.move: int = 0
        self.is_ko: bool = False
        self.captured_black: int = 0
        self.captured_white: int = 0
        self.board_history: list = []
        self.board = [[Cell.EMPTY for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]

    def add_move(self, x, y) -> None:
        if self.move % 2 == 0:
            current_color, opponent_color = (Cell.BLACK, Cell.WHITE)
        else:
            current_color, opponent_color = (Cell.WHITE, Cell.BLACK)

        assert self.is_empty((x, y))

        board_after_capture = deepcopy(self.board)
        board_after_capture[y][x] = current_color

        # iterate over each neighbor and check if it has liberties
        neighbors = self.get_neighbors(x, y)
        for cell_x, cell_y in neighbors:
            if board_after_capture[cell_y][cell_x] != opponent_color:
                continue

            queue = set(self.get_neighbors(cell_x, cell_y))
            visited = set([(cell_x, cell_y)])

            while queue:
                cell = queue.pop()
                if self.is_empty(cell, board_after_capture):
                    visited = set()
                    break

                if cell in visited:
                    continue

                if self.get_color(cell, board_after_capture) == opponent_color:
                    visited.add(cell)
                    for neighbor in self.get_neighbors(*cell):
                        queue.add(neighbor)

            # visited cells have no liberties and are removed
            for cell in visited:
                board_after_capture[cell[1]][cell[0]] = Cell.EMPTY

        assert self.get_liberties(x, y, opponent_color, board_after_capture) > 0

        if (
                len(self.board_history) > 2
                and board_after_capture == self.board_history[-2]
        ):
            return

        self.board = board_after_capture
        self.move += 1
        self.board_history.append(board_after_capture)

    def get_neighbors(self, x, y) -> list:
        neighbors = []

        if x > 0:
            neighbors.append((x - 1, y))
        if x < GRID_SIZE - 1:
            neighbors.append((x + 1, y))
        if y > 0:
            neighbors.append((x, y - 1))
        if y < GRID_SIZE - 1:
            neighbors.append((x, y + 1))
        return neighbors

    def get_color(self, coordinates: tuple[int, int], board=None) -> Cell:
        if not board:
            board = self.board
        x, y = coordinates
        return board[y][x]

    def is_empty(self, coordinates: tuple[int, int], board=None) -> bool:
        if not board:
            board = self.board
        x, y = coordinates
        return board[y][x] == Cell.EMPTY.value

    def get_liberties(self, x, y, opponent_color: Cell, board=None) -> int:
        if not board:
            board = self.board
        neighbors = self.get_neighbors(x, y)
        count = 0
        for neighbor in neighbors:
            if self.get_color(neighbor, board) != opponent_color:
                count += 1
        return count
