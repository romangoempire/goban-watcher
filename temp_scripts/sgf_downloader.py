import time

import requests
from icecream import ic

from src import ROOT_DIR

SGF_URL = "https://online-go.com/api/v1/games/{}/sgf"
RATE_LIMIT_DURATION = 61

sgf_dir = ROOT_DIR.joinpath("sgf/ogs")


def fetch_sgf(game_id: int) -> str:
    response = requests.get(SGF_URL.format(game_id))
    ic(response.content)
    if response.status_code == requests.codes.ok:
        return response.content.decode()
    elif response.status_code == requests.codes.too_many_requests:
        time.sleep(RATE_LIMIT_DURATION)
        return fetch_sgf(game_id)
    else:
        return ""


start = 16
end = 69335308

sgf_dir.mkdir(parents=True, exist_ok=True)

for i in range(start, end):
    sgf_string = fetch_sgf(i)
    if sgf_string:
        print(f"saving game {i}")
        with open(sgf_dir.joinpath(f"{i}.sgf"), "w") as f:
            f.write(sgf_string)
