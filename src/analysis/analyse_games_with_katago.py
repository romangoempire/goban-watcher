import random
import json
import subprocess
import sys
from pathlib import Path

from tqdm import tqdm
from sgfmill import sgf

sys.path.append(str(Path(__file__).parent.parent.parent))

from src import KATAGO_PATH, SGF_PATH
from src.utils.sgf_helper import convert_move_to_coordinate


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


def analyse_position(process, data: dict) -> None:
    data_string = json.dumps(data).replace("\n", "") + "\n"
    process.stdin.write(data_string)
    process.stdin.flush()


def get_start_and_amount(max_n: int) -> tuple[int, int]:
    missing = random.randint(MIN_MISSING, MAX_MISSING)
    start = random.randint(0, max_n - missing)
    return start, missing


def main():
    model_path = str(KATAGO_PATH.joinpath("models", "b28c512nbt.bin.gz"))
    config_path = str(KATAGO_PATH.joinpath("configs", "analysis_example.cfg"))

    process = subprocess.Popen(
        ["katago", "analysis", "-config", config_path, "-model", model_path],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1,
    )

    dir_path = SGF_PATH.joinpath("selected_sgf")
    paths = [dir_path.joinpath(f"{i}.sgf") for i in range(1, 21)]

    total_moves = 0
    results = {}

    for path in paths:
        moves = get_moves(path)

        data = {
            "id": path.name,
            "initialStones": [],
            "moves": moves,
            "rules": "tromp-taylor",
            "komi": 6.5,
            "boardXSize": 19,
            "boardYSize": 19,
            "analyzeTurns": [i for i in range(len(moves))],
        }
        analyse_position(process, data)
        results[path.name] = []
        total_moves += len(moves)

    for i in tqdm(range(total_moves)):
        while True:
            new_data = process.stdout.readline().strip()
            if new_data:
                result = json.loads(new_data)
                results[result["id"]].append(result)
                break

    with open("src/analysis/analysis_of_selected_games.json", "w") as f:
        json.dump(results, f, indent=4)

    process.terminate()


if __name__ == "__main__":
    main()
