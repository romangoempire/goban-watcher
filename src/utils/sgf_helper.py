def convert_move_to_coordinate(x: int, y: int) -> str:
    x_axis = "ABCDEFGHJKLMNOPQRST"
    return f"{x_axis[y]}{x + 1}"


def opponent(current: str) -> str:
    return "B" if current == "W" else "W"


def moves_of_player(moves: list[tuple[str, str]], color: str) -> list[tuple[str, str]]:
    return [move for move in moves if move[0] == color]
