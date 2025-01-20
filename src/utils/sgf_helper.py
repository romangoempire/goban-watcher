from pathlib import Path
from sgfmill import sgf


def convert_move_to_coordinate(x: int, y: int) -> str:
    x_axis = "ABCDEFGHJKLMNOPQRST"
    return f"{x_axis[y]}{x + 1}"


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
