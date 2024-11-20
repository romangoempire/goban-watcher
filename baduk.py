import pygame
from icecream import ic

from game import Cell, Game

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


def xy() -> list:
    x, y = mouse.get_pos()
    return [x // CELL_SIZE, y // CELL_SIZE]


def coordinates() -> list:
    pos = xy()
    if not pos:
        return []
    x, y = pos
    return [START + x * CELL_SIZE, START + y * CELL_SIZE]


def display_board() -> None:
    for y in range(GRID_SIZE):
        for x in range(GRID_SIZE):
            if game.is_empty((x, y)):
                continue

            color = BLACK if game.board[y][x] == Cell.BLACK else WHITE
            pygame.draw.circle(
                screen,
                color,
                [START + x * CELL_SIZE, START + y * CELL_SIZE],
                CELL_SIZE // 2,
            )


def display_grid() -> None:
    # Lines
    for x in range(GRID_SIZE):
        increment = START + x * CELL_SIZE
        width = 2
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

game = Game()

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
            game.reset()

    screen.fill(BROWN)
    display_grid()
    display_board()

    if mouse.get_pressed()[0]:
        x, y = xy()
        if game.is_empty((x, y)):
            game.add_move(x, y)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
