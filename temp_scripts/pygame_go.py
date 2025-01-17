import pygame

import sys

from pathlib import Path
from icecream import ic

sys.path.append(str(Path(__file__).parent.parent))

from src.utils.game import Game
from src.utils.colors import Color
from src.utils.visualize import game_add_grid, add_stones
from src import CELL_SIZE, GRID_SIZE, SCREEN_SIZE


def xy(mouse) -> list:
    x, y = mouse.get_pos()
    return [x // CELL_SIZE, y // CELL_SIZE]


def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_SIZE, SCREEN_SIZE))
    clock = pygame.time.Clock()

    mouse = pygame.mouse
    running = True

    game = Game()

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                game.reset()

        screen.fill(Color.BROWN.value)
        screen = game_add_grid(screen)
        screen = add_stones(screen, game)

        if mouse.get_pressed()[0]:
            x, y = xy(mouse)
            if game.is_empty((x, y)):
                game.add_move(x, y)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()


if __name__ == "__main__":
    main()
