from sgfmill import sgf

from src import ROOT_DIR, SGF_PATH
from src.utils.game import Game
from src.utils.visualize import save_png

sgf_dir = SGF_PATH.joinpath("selected_sgf")

for i in range(1, 21):
    with open(sgf_dir.joinpath(f"{i}.sgf"), "rb") as f:
        sgf_game = sgf.Sgf_game.from_bytes(f.read())

    game = Game()
    for node in sgf_game.get_main_sequence():
        _, move = node.get_move()
        if move:
            game.add_move(*move)

    save_png(game, ROOT_DIR.joinpath(f"images/boards/game_{i}.png"))
