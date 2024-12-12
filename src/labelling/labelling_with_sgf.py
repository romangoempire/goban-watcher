from copy import deepcopy
from sgfmill import sgf
from game import Game, Cell
from icecream import ic
import pygame

game = Game()

with open("sgf_20/7.sgf", "rb") as f:
    sgf_game = sgf.Sgf_game.from_bytes(f.read())

for node in sgf_game.get_main_sequence():
    player, move = node.get_move()

    if move:
        game.add_move(*move)


# CONSTANTS

SCREEN_SIZE = 800
GRID_SIZE = 19
CELL_SIZE = SCREEN_SIZE // GRID_SIZE
START = CELL_SIZE // 2
END = SCREEN_SIZE - START

HOSHIS = [3, 9, 15]

# colors
BLACK = [0, 0, 0, 0.5]
WHITE = [255, 255, 255]
BROWN = [245, 143, 41]

# METHODS


def display_stones() -> None:
    board = list(zip(*game.board))[::-1]

    for y in range(GRID_SIZE):
        for x in range(GRID_SIZE):
            if game.is_empty((x, y), board):
                continue

            color = BLACK if board[y][x] == Cell.BLACK else WHITE

            pygame.draw.circle(
                screen,
                color,
                [START + x * CELL_SIZE, START + y * CELL_SIZE],
                CELL_SIZE // 2 - 1,
            )


def display_grid() -> None:
    # Lines
    for x in range(GRID_SIZE):
        increment = START + x * CELL_SIZE
        width = 1
        pygame.draw.line(screen, BLACK, [START, increment], [END, increment], width)
        pygame.draw.line(screen, BLACK, [increment, START], [increment, END], width)

    # Hoshi
    for x in HOSHIS:
        for y in HOSHIS:
            pygame.draw.circle(
                screen,
                BLACK,
                [
                    CELL_SIZE // 2 + x * CELL_SIZE + 1,
                    CELL_SIZE // 2 + y * CELL_SIZE + 1,
                ],
                5,
            )


# MAIN

pygame.init()
screen = pygame.display.set_mode((SCREEN_SIZE, SCREEN_SIZE))
clock = pygame.time.Clock()

mouse = pygame.mouse
running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
            game.reset()

    screen.fill(BROWN)
    display_grid()
    display_stones()

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
