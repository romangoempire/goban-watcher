import sys
from pathlib import Path

import pygame

sys.path.append(str(Path(__file__).parent.parent))

from src import CELL_SIZE, SCREEN_SIZE
from src.utils.colors import Color
from src.utils.game import Game
from src.utils.visualize import add_stones, game_add_grid


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

        screen.fill([245, 143, 41])
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
