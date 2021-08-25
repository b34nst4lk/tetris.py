import os
import random
from itertools import cycle
from typing import List, Optional, Tuple, Dict
from dataclasses import dataclass
import logging
from enum import Enum

import pygame
from pygame.rect import Rect
from pygame.surface import Surface

from src.settings import (
    base_path,
    size,
    tile_width,
    tile_height,
    tile_size,
    columns,
    rows,
)

from utils import asset_resource_path

from src.bitboard import (
    print_board,
    arrangement_to_bit,
    decompose_bits,
    bottom_border,
    top_border,
    left_border,
    right_border,
)

colors = ["Blue", "Green", "LightBlue", "Orange", "Purple", "Red", "Yellow"]

_tiles = []
for color in colors:
    tile_path = asset_resource_path(f"{color}.png")
    logging.warning(tile_path)
    tile = pygame.image.load(tile_path)
    tile = pygame.transform.scale(tile, (tile_width, tile_height))
    _tiles.append(tile)

tiles = cycle(_tiles)


class Shapes(Enum):
    i = "i"
    j = "j"
    l = "l"
    o = "o"
    s = "s"
    t = "t"
    z = "z"


tetriminos: Dict[Shapes, List[List[int]]] = {
    Shapes.i: [
        [0, 0, 0, 0],
        [1, 1, 1, 1],
        [0, 0, 0, 0],
        [0, 0, 0, 0],
    ],
    Shapes.j: [
        [0, 0, 1],
        [1, 1, 1],
    ],
    Shapes.l: [
        [1, 0, 0],
        [1, 1, 1],
    ],
    Shapes.o: [
        [1, 1],
        [1, 1],
    ],
    Shapes.s: [
        [0, 1, 1],
        [1, 1, 0],
    ],
    Shapes.t: [
        [0, 1, 0],
        [1, 1, 1],
    ],
    Shapes.z: [
        [1, 1, 0],
        [0, 1, 1],
    ],
}

bits: Dict[Shapes, int] = {}
for key, arrangement in tetriminos.items():
    bits[key] = arrangement_to_bit(arrangement)

def bitboard_to_row(bitboard: int):
    row = 1
    while bitboard & bottom_border == 0:
        bitboard >>= columns
        row += 1
    return row


def bitboard_to_column(bitboard: int):
    column = 1
    while bitboard & right_border == 0:
        bitboard >>= 1
        column += 1

    return column

def bitboard_to_coords(bitboard: int) -> Tuple[int, int]:
    global columns, rows, tile_width, tile_height
    only_one_bit = len(decompose_bits(bitboard)) == 1

    if not only_one_bit:
        raise ValueError("bitboard contains more than one bit")

    row = bitboard_to_row(bitboard)
    row = rows - row

    column = bitboard_to_column(bitboard)
    column = columns - column

    coords = (column * tile_width, row * tile_height)
    return coords

# def get_bitboard_top_left_position(bitboard: int) -> Tuple[int, int]:
#     bitboard_copy = bitboard
#     while bitboard_copy  bottom_row > 0
#     pass        

@dataclass
class Tile:
    bitboard: int
    rect: Rect
    tile: Surface
    screen: pygame.display

    def render(self, bitboard: Optional[int] = None):
        if not bitboard:
            bitboard = self.bitboard

        coords = bitboard_to_coords(bitboard)
        self.rect.update(coords, tile_size)
        self.screen.blit(self.tile, self.rect)
        self.bitboard = bitboard


@dataclass
class Tetrimino:
    shape: Shapes
    tile: pygame.Surface
    screen: pygame.display
    bitboard: int = 0
    rotation: int = 0
    locked: bool = False

    def __post_init__(self):
        self.bitboard = bits[self.shape] << (columns * (rows - 1) - columns // 2 - 2)

        self.tiles: List[Tile] = []
        for bit in decompose_bits(self.bitboard):
            tile = Tile(bit, self.tile.get_rect(), self.tile, self.screen)
            self.tiles.append(tile)

        self.render()

    def render(self):
        if not self.tiles:
            raise ValueError("self.tiles required")

        bits = decompose_bits(self.bitboard)
        for bit, tile in zip(bits, self.tiles):
            tile.render(bit)

    def move_down(self):
        self.bitboard >>= columns

    def move_left(self):
        self.bitboard <<= 1

    def move_right(self):
        self.bitboard >>= 1

    def rotate(self):
        bitboard = self.bitboard
        top_left_coords = self.get_top_left_coords(bitboard)
@dataclass
class Tetriminos:
    screen: pygame.display
    tetrimino: Optional[Tetrimino] = None

    def __post_init__(self):
        self.tiles: List[Tile] = []

    def get_tetrimino(self):
        if not self.tetrimino or self.tetrimino.locked:
            tile = next(tiles)
            shape = random.choice(list(Shapes))
            self.tetrimino = Tetrimino(shape, tile, self.screen)

        return self.tetrimino

    @staticmethod
    def collide_left(tetrimino: Tetrimino, obj: int):
        bitboard = tetrimino.bitboard
        collision_zone = bitboard << 1
        return collision_zone & obj > 0

    @staticmethod
    def collide_right(tetrimino: Tetrimino, obj: int):
        bitboard = tetrimino.bitboard
        collision_zone = bitboard >> 1
        return collision_zone & obj > 0

    @staticmethod
    def collide_bottom(tetrimino: Tetrimino, obj: int):
        bitboard = tetrimino.bitboard
        collision_zone = bitboard >> columns
        return collision_zone & obj > 0

    def move_down(self):
        active_tetrimino = self.get_tetrimino()
        if self.collide_bottom(active_tetrimino, bottom_border):
            self.tiles.extend(active_tetrimino.tiles)
            active_tetrimino.locked = True
            return

        for tile in self.tiles:
            if self.collide_bottom(active_tetrimino, tile.bitboard):
                self.tiles.extend(active_tetrimino.tiles)
                active_tetrimino.locked = True
                return

        active_tetrimino.move_down()

    def move_left(self):
        active_tetrimino = self.get_tetrimino()
        if self.collide_left(active_tetrimino, left_border):
            return

        for tile in self.tiles:
            if self.collide_left(active_tetrimino, tile.bitboard):
                return

        self.get_tetrimino().move_left()

    def move_right(self):
        active_tetrimino = self.get_tetrimino()
        if self.collide_right(active_tetrimino, right_border):
            return

        for tile in self.tiles:
            if self.collide_right(active_tetrimino, tile.bitboard):
                return

        self.get_tetrimino().move_right()

    def move_down_and_lock(self):
        active_tetrimino = self.get_tetrimino()
        while not active_tetrimino.locked:
            if self.collide_bottom(active_tetrimino, bottom_border):
                self.tiles.extend(active_tetrimino.tiles)
                active_tetrimino.locked = True
                return

            for tile in self.tiles:
                if self.collide_bottom(active_tetrimino, tile.bitboard):
                    self.tiles.extend(active_tetrimino.tiles)
                    active_tetrimino.locked = True
                    return
            active_tetrimino.move_down()
            active_tetrimino.render()

    def render(self):
        self.get_tetrimino().render()
        for tile in self.tiles:
            tile.render()

    def is_game_over(self):
        for tile in self.tiles:
            if tile.bitboard & top_border > 0:
                return True


def game_over():
    logging.warning("game over")


if __name__ == "__main__":
    # from bitboard import print_board

    # print_board("t", arrangement_to_bit(tetriminos[Shapes.t]))

    # for i in decompose_bits(arrangement_to_bit(tetriminos[Shapes.t])):
    #     print_board(i, i)

    # Tetrimino(Shapes.l, next(tiles), None)

    bitboard = 1 << (rows * columns - 2)
    print_board("top_left_corner", bitboard)
    print(bitboard_to_row(bitboard))
    print(bitboard_to_column(bitboard))
    print(bitboard_to_coords(bitboard))
