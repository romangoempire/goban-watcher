import json
import os

import cv2
from tqdm import tqdm

from src import IMG_PATH
from src.utils.cv2_helper import blur_and_sharpen
from src.utils.pixel_changes import percentage_pixel_changed

run = "20250115"  # Todo change to your run
game_path = IMG_PATH.joinpath(run)
file_names = [f for f in os.listdir(game_path) if f != ".DS_Store"]
file_names.sort(key=lambda f: int(f.rstrip(".jpg")))

changes = []
last_img = None
for filename in tqdm(file_names):
    img = cv2.imread(f"{game_path}/{filename}")
    img = blur_and_sharpen(img)

    if last_img is None:
        last_img = img
        continue

    changes.append(percentage_pixel_changed(last_img, img))
    last_img = img


with open(f"data/games/{run}.json", "w") as f:
    json.dump(changes, f)
