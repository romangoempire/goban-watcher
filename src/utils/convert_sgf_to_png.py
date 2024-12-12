import os

from sgfmill import sgf
from src.utils.game import Game
from src.utils.visualize import save_png

SGF_DIR = "../../sgf/20"


for i in range(1,20):
    with open(os.path.join(SGF_DIR,f"{i}.sgf"),"rb") as f:
        sgf_game = sgf.Sgf_game.from_bytes(f.read())

    game = Game()
    for node in sgf_game.get_main_sequence():
        _,move = node.get_move()
        if move:
            game.add_move(*move)

    save_png(game,f"../../images/boardss/game_{i}")
