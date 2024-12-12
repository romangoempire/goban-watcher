import os
import subprocess
from datetime import datetime

from icecream import ic
from tqdm import tqdm

# CONSTANTS
CONFIG_PATH = "../../katago/configs/default_gtp.cfg"
MODEL_PATH = "../../katago/models/b28c512nbt.bin.gz"

SGF_PATH = "../../sgf/katago_selfplay"

# METHODS


def send(process, message: str) -> str:
    message += "\n" if not message.endswith("\n") else ""

    process.stdin.write(message)
    process.stdin.flush()

    while True:
        answer: str = process.stdout.readline().strip()
        if answer:
            return answer.strip("= ")


def generate_game():
    process = subprocess.Popen(
        ["katago", "gtp", "-config", f"{CONFIG_PATH}", "-model", f"{MODEL_PATH}"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1,
    )

    send(process, "komi 6.5")

    color = "b"

    while True:
        move = send(process, f"genmove {color}")
        color = "b" if color == "w" else "w"
        if move in ["pass", "resign"]:
            break

    sgf = send(process, "printsgf")
    current_time = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")

    new_sgf_path = os.path.join(SGF_PATH, f"kata_selfplay_{current_time}.sgf")
    with open(new_sgf_path, "w") as f:
        f.write(sgf)

    process.terminate()


def main():
    os.makedirs(SGF_PATH, exist_ok=True)
    for i in tqdm(range(10)):
        generate_game()


if __name__ == "__main__":
    main()
