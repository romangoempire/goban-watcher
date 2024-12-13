from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent
IMG_PATH = ROOT_DIR.joinpath("img")
SGF_PATH = ROOT_DIR.joinpath("sgf")
KATAGO_PATH = ROOT_DIR.joinpath("katago")

SCREEN_SIZE = 800
GRID_SIZE = 19
CELL_SIZE = SCREEN_SIZE // GRID_SIZE
START = CELL_SIZE // 2
END = SCREEN_SIZE - START

HOSHIS = [3, 9, 15]
