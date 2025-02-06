import json
import subprocess
import sys
from pathlib import Path

from tqdm import tqdm

sys.path.append(str(Path(__file__).parent.parent.parent))

from src import DATA_PATH, KATAGO_PATH, SGF_PATH
from src.utils.sgf_helper import get_moves


def send_position_into_analysis(process, data: dict) -> None:
    # katago analyse requires input as oneline
    data_string = json.dumps(data).replace("\n", "") + "\n"
    process.stdin.write(data_string)
    process.stdin.flush()


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
        send_position_into_analysis(process, data)
        results[path.name] = []
        total_moves += len(moves)

    assert process.stdout, "No Output"

    for i in tqdm(range(total_moves)):
        while True:
            new_data = process.stdout.readline().strip()
            if new_data:
                result = json.loads(new_data)
                results[result["id"]].append(result)
                break

    with open(DATA_PATH.joinpath("analysis_of_selected_games.json"), "w") as f:
        json.dump(results, f, indent=4)

    process.terminate()


if __name__ == "__main__":
    main()
