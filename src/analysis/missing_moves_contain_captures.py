import sys
from pathlib import Path

from icecream import ic
from sgfmill import sgf

sys.path.append(str(Path(__file__).parent.parent.parent))
from src import SGF_PATH
from src.utils.game import Game


filename = SGF_PATH.joinpath("selected_sgf", "1.sgf")
game = Game()

with open(filename, "rb") as f:
    main_sequence = sgf.Sgf_game.from_bytes(f.read()).get_main_sequence()

last_captures = 0

for index, node in enumerate(main_sequence):
    _, move = node.get_move()
    if move:
        game.add_move(*move)
        new_amount_captures = game.captured_black + game.captured_white
        if new_amount_captures != last_captures:
            last_captures = new_amount_captures
            ic(index, game.captured_black, game.captured_white)
