import os
import time
import requests
from icecream import ic

SGF_DIR = "sgf"
SGF_URL = "https://online-go.com/api/v1/games/{}/sgf"
RATE_LIMIT_DURATION = 61


def sgf(id: int) -> str:
    response = requests.get(SGF_URL.format(id))
    if response.status_code == requests.codes.ok:
        return response.content.decode()
    elif response.status_code == requests.codes.too_many_requests:
        time.sleep(RATE_LIMIT_DURATION)
        return sgf(id)
    else:
        return ""


start = 1
end = 69335308

os.makedirs(SGF_DIR, exist_ok=True)
for id in range(start, end):
    sgf_string = sgf(id)
    if sgf_string:
        with open(f"{SGF_DIR}/{id}.sgf", "w") as f:
            f.write(sgf_string)
