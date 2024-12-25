import json
from pathlib import Path

import cv2

from src import IMG_PATH
from src.utils.colors import Color

filename = "1_jwerth_cyan_2.jpg"
sgf_image_path = IMG_PATH.joinpath("selected_sgf")

img = cv2.imread(str(sgf_image_path.joinpath(f"1/{filename}")))
with open(Path(__file__).parent / "corners.json") as f:
    data = json.load(f)

while True:
    key = cv2.waitKey(1) & 0xFF
    for corner in data["1"][filename]:
        img = cv2.circle(img, (int(corner[0] * img.shape[1]),int(corner[1] * img.shape[0])), 10, [0,0,255], -1)
    cv2.imshow("img", img)
