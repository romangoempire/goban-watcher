import subprocess
from datetime import datetime
from pathlib import PosixPath

from tqdm import tqdm

from src import KATAGO_PATH


def send(process, message: str) -> str:
    message += "\n" if not message.endswith("\n") else ""

    process.stdin.write(message)
    process.stdin.flush()

    while True:
        answer: str = process.stdout.readline().strip()
        if answer:
            return answer.strip("= ")


def generate_game(config_path: PosixPath, model_path: PosixPath, sgf_dir: PosixPath) -> None:
    process = subprocess.Popen(
        ["katago", "gtp", "-config", f"{config_path}", "-model", f"{model_path}"],
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

    file_name = sgf_dir.joinpath(f"kata_selfplay_{current_time}.sgf")
    with open(file_name, "w") as f:
        f.write(sgf)

    process.terminate()


def main():
    config_path = KATAGO_PATH.joinpath("configs/default_gtp.cfg")
    model_path = KATAGO_PATH.joinpath("models/b28c512nbt.bin.gz")

    sgf_dir = KATAGO_PATH.joinpath("katago_selfplay")
    sgf_dir.mkdir(parents=True, exist_ok=True)

    for i in tqdm(range(10)):
        generate_game(config_path,model_path,sgf_dir)


if __name__ == "__main__":
    main()
