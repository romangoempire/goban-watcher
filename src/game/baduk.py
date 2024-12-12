import pygame

from src.utils.game import Game
from src.utils.colors import Color
from src.utils.visualize import add_grid, add_stones
from src import CELL_SIZE,START,SCREEN_SIZE

# CONSTANTS

# colors


# METHODS


def xy() -> list:
    x, y = mouse.get_pos()
    return [x // CELL_SIZE, y // CELL_SIZE]


def coordinates() -> list:
    pos = xy()
    if not pos:
        return []
    x, y = pos
    return [START + x * CELL_SIZE, START + y * CELL_SIZE]


# MAIN

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
    screen = add_grid(screen, game)
    screen = add_stones(screen)

    if mouse.get_pressed()[0]:
        x, y = xy()
        if game.is_empty((x, y)):
            game.add_move(x, y)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
