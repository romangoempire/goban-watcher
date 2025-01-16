import os
import cv2
import json
import numpy as np
from tqdm import tqdm

from src import IMG_PATH

run = "20250115"
game_path = IMG_PATH.joinpath(run)
file_names = [f for f in os.listdir(game_path) if f != ".DS_Store"]
file_names.sort(key=lambda f: int(f.rstrip(".jpg")))

results = []
last_img = None
for i, filename in tqdm(enumerate(file_names)):
    if last_img is None:
        img = cv2.imread(f"{game_path}/{filename}")
        blurred_image = cv2.GaussianBlur(img, (5, 5), 0)
        kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]])
        sharpened_image = cv2.filter2D(blurred_image, -1, kernel)
        last_img = sharpened_image
        continue

    img = cv2.imread(f"{game_path}/{filename}")

    blurred_image = cv2.GaussianBlur(img, (5, 5), 0)
    kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]])
    sharpened_image = cv2.filter2D(blurred_image, -1, kernel)

    diff = cv2.absdiff(last_img, sharpened_image)
    diff_magnitude = np.linalg.norm(diff.astype(np.float32), axis=2)

    threshold = 50
    mask_above_threshold = diff_magnitude > threshold
    percentage_above_threshold = round(np.mean(mask_above_threshold) * 100, 4)

    results.append(percentage_above_threshold)
    last_img = sharpened_image


with open(f"data/games/{run}.json", "w") as f:
    json.dump(results, f)
