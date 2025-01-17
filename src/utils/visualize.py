from pathlib import Path

import pygame
from pygame import SurfaceType

from src import CELL_SIZE, END, GRID_SIZE, HOSHIS, START
from src.utils.colors import Color
from src.utils.game import Cell, Game


def add_stones(screen: SurfaceType, game: Game) -> SurfaceType:
    for y in range(GRID_SIZE):
        for x in range(GRID_SIZE):
            if game.is_empty((x, y)):
                continue

            color = (
                Color.BLACK.value
                if game.board[y][x] == Cell.BLACK
                else Color.WHITE.value
            )
            pygame.draw.circle(
                screen,
                color,
                [START + x * CELL_SIZE, START + y * CELL_SIZE],
                CELL_SIZE // 2,
            )
    return screen


def game_add_grid(screen: SurfaceType) -> SurfaceType:
    # Lines
    for x in range(GRID_SIZE):
        increment = START + x * CELL_SIZE
        width = 1
        pygame.draw.line(
            screen, Color.BLACK.value, [START, increment], [END, increment], width
        )
        pygame.draw.line(
            screen, Color.BLACK.value, [increment, START], [increment, END], width
        )

    # Hoshi
    for x in HOSHIS:
        for y in HOSHIS:
            pygame.draw.circle(
                screen,
                Color.BLACK.value,
                [
                    CELL_SIZE // 2 + x * CELL_SIZE + 1,
                    CELL_SIZE // 2 + y * CELL_SIZE + 1,
                ],
                5,
            )
    return screen


def save_png(game, filename: Path) -> None:
    assert filename.suffix == ".png", "filename must end with .png"
    surface = pygame.Surface((800, 800))

    surface.fill(Color.BROWN.value)
    surface = game_add_grid(surface)
    surface = add_stones(surface, game)

    pygame.image.save(surface, filename)
