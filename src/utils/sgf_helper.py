from pathlib import Path
from sgfmill import sgf
from src.utils.game import Cell

X_AXIS = "ABCDEFGHJKLMNOPQRST"


def convert_move_to_coordinate(x: int, y: int) -> str:
    return f"{X_AXIS[y]}{x + 1}"


def convert_coordinate_to_move(coordinate: str) -> tuple[int, int]:
    return X_AXIS.index(coordinate[0]), int(coordinate[1:]) - 1


def convert_cell_to_player_color(cell: Cell) -> str:
    return "B" if cell == Cell.BLACK else "W"


def opponent(current: str) -> str:
    return "B" if current == "W" else "W"


def moves_of_player(moves: list[tuple[str, str]], color: str) -> list[tuple[str, str]]:
    return [move for move in moves if move[0] == color]


def get_moves(path: Path) -> list[tuple[str, str]]:
    with open(str(path), "rb") as f:
        game = sgf.Sgf_game.from_bytes(f.read())

    moves = []
    for node in game.get_main_sequence():
        player, move = node.get_move()
        if not move:
            continue

        assert player, "No Player"

        move_data = (player.upper(), convert_move_to_coordinate(*move))
        moves.append(move_data)
    return moves
