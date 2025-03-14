from copy import deepcopy
from enum import IntEnum, auto
from pathlib import Path

from sgfmill import sgf

from src import GRID_SIZE


class Cell(IntEnum):
    EMPTY = 0
    BLACK = auto()
    WHITE = auto()


class Game:
    def __init__(self):
        self.move: int = 0
        self.captured_black: int = 0
        self.captured_white: int = 0
        self.board_history: list = []
        self.board: list[list[Cell]] = self._initialize_board()
        self.neighbors = self.get_neighbors()

    def reset(self) -> None:
        self.move: int = 0
        self.captured_black: int = 0
        self.captured_white: int = 0
        self.board_history: list = []
        self.board = self._initialize_board()

    @staticmethod
    def _initialize_board() -> list[list[Cell]]:
        return [[Cell.EMPTY for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]

    def get_colors_current_and_opponent_player(self) -> tuple[Cell, Cell]:
        """Returns the color of the current player and the opponent based on self.move."""
        current_color, opponent_color = (
            (Cell.BLACK, Cell.WHITE),
            (Cell.WHITE, Cell.BLACK),
        )[self.move & 1]
        return current_color, opponent_color

    def add_move(self, x: int, y: int) -> None:
        """Adds Cell at position x, y for the player whose turn it is."""
        assert self.is_empty((x, y)), "Position occupied"

        current_color, opponent_color = self.get_colors_current_and_opponent_player()

        # create copy since move might be invalid and should not change the current boards
        board_after_capture = deepcopy(self.board)

        # add move
        board_after_capture[y][x] = current_color

        # iterate over each neighbor and check if it has liberties
        neighbors = self.neighbors[y][x]
        captures = 0
        for neighbor_x, neighbor_y in neighbors:
            # only check liberties for opponent
            if board_after_capture[neighbor_y][neighbor_x] != opponent_color:
                continue

            queue = {(neighbor_x, neighbor_y)}
            visited = set()

            while queue:
                cell = queue.pop()

                # Pass the board copy since changes could have happen before
                if self.is_empty(cell, board_after_capture):
                    # stone and all connected stones have liberty => not captured
                    visited = set()
                    break

                if cell in visited:
                    continue

                # stone has no liberty, but might be connected and the connected stone might have liberties
                if self.get_color(cell, board_after_capture) == opponent_color:
                    visited.add(cell)
                    cell_x, cell_y = cell
                    queue.update(self.neighbors[cell_y][cell_x])

            # visited cells have no liberties and are removed
            for cell in visited:
                captures += 1
                cell_x, cell_y = cell
                board_after_capture[cell_y][cell_x] = Cell.EMPTY

        # stone does not capture any stones and has no liberties afterwards
        assert self.get_liberties(x, y, opponent_color, board_after_capture) > 0, (
            "Move would lead to suicide"
        )

        if len(self.board_history) > 2:
            # board position repeats => ko rule
            assert board_after_capture != self.board_history[-2], (
                "Move would lead to invalid repetition (ko)"
            )

        if opponent_color == Cell.WHITE:
            self.captured_white += captures
        elif opponent_color == Cell.BLACK:
            self.captured_black += captures

        self.move += 1
        self.board = board_after_capture
        self.board_history.append(board_after_capture)

    @staticmethod
    def get_neighbors() -> list:
        """Returns lookup table of neighbors for each x, y."""
        lookup = []
        for y in range(GRID_SIZE):
            neighbor_row = []
            for x in range(GRID_SIZE):
                neighbors = []
                # left
                if x > 0:
                    neighbors.append((x - 1, y))
                # right
                if x < GRID_SIZE - 1:
                    neighbors.append((x + 1, y))
                # top
                if y > 0:
                    neighbors.append((x, y - 1))
                # bottom
                if y < GRID_SIZE - 1:
                    neighbors.append((x, y + 1))
                neighbor_row.append(neighbors)
            lookup.append(neighbor_row)
        return lookup

    def get_color(self, coordinates: tuple[int, int], board=None) -> Cell:
        board = self.board if board is None else board
        x, y = coordinates
        return board[y][x]

    def is_empty(self, coordinates: tuple[int, int], board=None) -> bool:
        board = self.board if board is None else board
        x, y = coordinates
        return board[y][x] == Cell.EMPTY.value

    def get_liberties(self, x, y, opponent_color: Cell, board=None) -> int:
        board = self.board if board is None else board
        neighbors = self.neighbors[y][x]
        count = 0
        for neighbor in neighbors:
            if self.get_color(neighbor, board) != opponent_color:
                count += 1
        return count

    def add_sgf(self, filename: Path) -> None:
        """Plays out complete sgf by adding each move."""
        with open(filename, "rb") as f:
            main_sequence = sgf.Sgf_game.from_bytes(f.read()).get_main_sequence()

        for node in main_sequence:
            _, move = node.get_move()
            if move:
                x, y = move
                x, y = y, GRID_SIZE - 1 - x  # change due sgf coordinate order
                self.add_move(x, y)
