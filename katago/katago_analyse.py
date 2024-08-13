import time
import json
import subprocess
from threading import Thread

from icecream import ic


class KataGo:

    def __init__(
        self,
        katago_path: str,
        config_path: str,
        model_path: str,
    ):

        katago = subprocess.Popen(
            [
                katago_path,
                "analysis",
                "-config",
                config_path,
                "-model",
                model_path,
            ],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        self._katago = katago
        self.query_counter = 0

        def printforever():
            while katago.poll() is None:
                data = katago.stderr.readline()
                time.sleep(0)
                if data:
                    print("KataGo: ", data.decode(), end="")
            data = katago.stderr.read()
            if data:
                print("KataGo: ", data.decode(), end="")

        self.stderrthread = Thread(target=printforever)
        self.stderrthread.start()

    def __del__(self):
        self._katago.stdin.close()

    def analyse(
        self,
        moves: list,
        initial_board: list = [],
        rules: str = "tromp-taylor",
        komi: float = 6.5,
        max_visits=None,
    ):
        data = {
            "id": str(self.query_counter),
            "moves": moves,
            "initialStones": initial_board,
            "rules": rules,
            "komi": komi,
            "boardXSize": 19,
            "boardYSize": 19,
        }

        if max_visits is not None:
            data["maxVisits"] = max_visits

        self.query_counter += 1

        return self._to_katago(data)

    def _to_katago(self, query: dict):
        self._katago.stdin.write((json.dumps(query) + "\n").encode())
        self._katago.stdin.flush()

        line = ""
        while line == "":
            if self._katago.poll():
                time.sleep(1)
                raise Exception("Unexpected katago exit")
            line = self._katago.stdout.readline()
            line = line.decode().strip()

        response = json.loads(line)
        return response


def coordinate_to_xy(coordinate: str) -> tuple[int, int]:
    return "ABCDEFGHJKLMNOPQRST".index(coordinate[0]), 19 - int(coordinate[1:])


def xy_to_coordinate(x: int, y: int) -> str:
    return f"{"ABCDEFGHJKLMNOPQRST"[x - 1]}{20 - y}"


if __name__ == "__main__":
    katago = KataGo(
        "katago",
        "katago/configs/analysis_example.cfg",
        "katago/models/g170-b30c320x2.bin.gz",
    )

    moves = []
    results = katago.analyse(moves)

    json.dump(results, open("out.json", "w"), indent=4)
