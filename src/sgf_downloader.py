from custom_logger import logger
import os
import random
import time

import requests


URL = "https://online-go.com/api/v1/games/{game_id}/{mode}"
PATH_PNG = "./data/png/{game_id}.png"
PATH_SGF = "./data/sgf/{game_id}.sgf"


def create_folders() -> None:
    os.makedirs("./data", exist_ok=True)
    os.makedirs("./data/png", exist_ok=True)
    os.makedirs("./data/sgf", exist_ok=True)


def save_png(png: bytes, game_id: int) -> None:
    path = PATH_PNG.format(game_id=game_id)
    with open(path, "wb") as f:
        f.write(png)


def save_sgf(sgf: bytes, game_id: int) -> None:
    path = PATH_SGF.format(game_id=game_id)
    with open(path, "wb") as f:
        f.write(sgf)


def get_png(
    game_id: int,
) -> None:
    if os.path.exists(PATH_PNG.format(game_id=game_id)):
        logger.info(f"PNG for game {game_id} already exists")
        return

    path = URL.format(game_id=game_id, mode="png")

    response = requests.get(path)

    if response.status_code == requests.codes.ok:
        logger.info(f"Got PNG for game {game_id}")
        save_png(response.content, game_id)
    elif response.status_code == requests.codes.too_many_requests:
        logger.info("Rate limited")
        time.sleep(61)
        get_png(game_id)  # ! try again after waiting
    elif response.status_code == requests.codes.not_found:
        logger.info(f"Game {game_id} not found")
    else:
        logger.info(f"Error getting PNG for game {game_id}")
        logger.error(response.status_code)
        logger.error(response.text)


def get_sgf(game_id: int) -> None:
    if os.path.exists(PATH_SGF.format(game_id=game_id)):
        logger.info(f"SGF for game {game_id} already exists")
        return
    path = URL.format(game_id=game_id, mode="/sgf")
    response = requests.get(path)

    if response.status_code == requests.codes.ok:
        logger.info(f"Got SGF for game {game_id}")
        save_sgf(response.content, game_id)
    elif response.status_code == requests.codes.too_many_requests:
        logger.info("Rate limited")
        time.sleep(61)  # ! Limit are 10 requests per minute
        get_sgf(game_id)  # ! try again after waiting
    elif response.status_code == requests.codes.not_found:
        logger.info(f"Game {game_id} not found")
    else:
        logger.info(f"Error getting SGF for game {game_id}")
        logger.error(response.status_code)
        logger.error(response.text)


if __name__ == "__main__":
    create_folders()
    i = 0
    while i < 100:
        game_id = random.randint(1, 67_621_523)
        get_sgf(game_id)
        get_png(game_id)
        i += 1
