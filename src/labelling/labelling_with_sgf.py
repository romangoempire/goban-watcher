from copy import deepcopy

import cv2
from pathlib import Path
from icecream import ic

from src import ROOT_DIR, IMG_PATH

img_dir = IMG_PATH.joinpath("selected_sgf")
board_dir = IMG_PATH.joinpath("boards")

image_paths = {
    str(i): [file for file in img_dir.joinpath(str(i)).iterdir() if file.is_file() and not file.name.startswith(".")]
    for i in range(1, 21)
}

for sgf_number, paths in image_paths.items():
    img = cv2.imread(str(board_dir.joinpath(f"game_{sgf_number}.png")))
    while True:
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            cv2.destroyWindow(sgf_number)
            break
        cv2.imshow(sgf_number, img)

cv2.destroyAllWindows()
