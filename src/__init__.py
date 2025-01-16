from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent
IMG_PATH = ROOT_DIR.joinpath("images")
DATA_PATH = ROOT_DIR.joinpath("data")
SGF_PATH = ROOT_DIR.joinpath("sgf")
KATAGO_PATH = ROOT_DIR.joinpath("katago")

GRID_SIZE = 19
CELL_SIZE = 64
HALF_CELL_SIZE = CELL_SIZE // 2
SCREEN_SIZE = CELL_SIZE * GRID_SIZE

START = CELL_SIZE // 2
END = SCREEN_SIZE - START

HOSHIS = [3, 9, 15]
