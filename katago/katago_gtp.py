import time
import json
import subprocess

from .utils import format_raw_string


class KataGo:

    def __init__(self):

        self._katago = subprocess.Popen(
            ["katago", "gtp"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        print("Katago started")

    def send(self, text: str) -> None:
        self._katago.stdin.write((text + "\n").encode())
        self._katago.stdin.flush()

    def read(self) -> str:
        while True:
            if self._katago.poll():
                time.sleep(1)
                raise Exception("Unexpected katago exit")
            line = self._katago.stdout.readline().decode().strip()
            if line:
                return line[2:]

    def read_move(self) -> list[dict]:
        while True:
            if self._katago.poll():
                time.sleep(1)
                raise Exception("Unexpected katago exit")
            line = self._katago.stdout.readline().decode().strip()
            if line and "=" not in line:
                return format_raw_string(line)

    def __del__(self):
        self._katago.stdin.close()
        print("Katago Closed")


if __name__ == "__main__":
    from icecream import ic

    katago = KataGo()

    katago.send("kata-analyze B 100")
    with open("katago/testfiles/output_gtp.json", "w") as f:
        json.dump(katago.read_move(), f, indent=4)
