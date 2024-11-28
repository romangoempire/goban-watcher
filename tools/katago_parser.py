from ast import Index
import json
import subprocess

from icecream import ic

MODEL_NAME = "katago/b28c512nbt.bin.gz"
CFG_NAME = "katago/analysis_example.cfg"

process = subprocess.Popen(
    ["katago", "analysis", "-config", f"{CFG_NAME}", "-model", f"{MODEL_NAME}"],
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True,
    bufsize=1,
)

data = {
    "id": "foo",
    "initialStones": [],
    "moves": [],
    "rules": "tromp-taylor",
    "komi": 6.5,
    "boardXSize": 19,
    "boardYSize": 19,
    "analyzeTurns": [0],
}


def format_input(data: dict) -> str:
    return json.dumps(data).replace("\n", "")


input_data = format_input(data)
stdout_output = process.communicate(input=input_data)

with open("output.json", "w") as f:
    json.dump(json.loads(stdout_output[0]), f, indent=4)

process.wait()
