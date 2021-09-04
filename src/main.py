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
    COLUMNS,
    ROWS,
    TILE_HEIGHT,
    TILE_SIZE,
    TILE_WIDTH,
)

from src.utils import asset_resource_path

from src.bitboard import (
    all_borders,
    arrangement_to_bit,
    bitboard_to_coords,
    bottom_border,
    decompose_bits,
    left_border,
    right_border,
    rotate_bitboard,
    top_border,
    widen_bitboard_width,
)

# Load assets
colors = ["Blue", "Green", "LightBlue", "Orange", "Purple", "Red", "Yellow"]

_tiles = []
for color in colors:
    tile_path = asset_resource_path(f"{color}.png")
    tile = pygame.image.load(tile_path)
    tile = pygame.transform.scale(tile, (TILE_WIDTH, TILE_HEIGHT))
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
        [0, 0, 0],
    ],
    Shapes.l: [
        [1, 0, 0],
        [1, 1, 1],
        [0, 0, 0],
    ],
    Shapes.o: [
        [1, 1],
        [1, 1],
    ],
    Shapes.s: [
        [0, 1, 1],
        [1, 1, 0],
        [0, 0, 0],
    ],
    Shapes.t: [
        [0, 1, 0],
        [1, 1, 1],
        [0, 0, 0],
    ],
    Shapes.z: [
        [1, 1, 0],
        [0, 1, 1],
        [0, 0, 0],
    ],
}

def shape_generator():
    bag = []
    while True:
        if not bag:
            bag = list(Shapes)
            random.shuffle(bag)
        yield bag.pop(0)  
        
bits: Dict[Shapes, int] = {}
for key, arrangement in tetriminos.items():
    bits[key] = arrangement_to_bit(arrangement)

tetriminos_widths: Dict[Shapes, int] = {}
for key, arrangement in tetriminos.items():
    tetriminos_widths[key] = len(arrangement[0])

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
        self.rect.update(coords, TILE_SIZE)
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
        self.bitboard = bits[self.shape] << (COLUMNS * (ROWS - 1) - COLUMNS // 2 - 2)

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
        self.bitboard >>= COLUMNS

    def move_left(self):
        self.bitboard <<= 1

    def move_right(self):
        self.bitboard >>= 1

    def test_rotate(self):
        # Prepare tetrimino for comparison
        current_rotation = self.rotation
        arrangement = tetriminos[self.shape]
        tetrimino_width = tetriminos_widths[self.shape]
        small_bitboard = arrangement_to_bit(arrangement, tetrimino_width) 
        for _ in range(current_rotation):
            small_bitboard = rotate_bitboard(small_bitboard, tetrimino_width)

        compare_bitboard = widen_bitboard_width(
            small_bitboard, tetrimino_width, COLUMNS
        )

        # Trim current bitboard to identify shift
        bitboard = self.bitboard

        shift = 0
        while bitboard & bottom_border == 0:
            bitboard >>= COLUMNS
            shift += COLUMNS

        while bitboard != compare_bitboard:
            if bitboard > compare_bitboard:
                bitboard >>= 1
                shift += 1
            else:
                bitboard <<= 1
                shift -= 1

        small_bitboard = rotate_bitboard(small_bitboard, tetrimino_width)
        rotated_bitboard = widen_bitboard_width(
            small_bitboard, tetrimino_width, COLUMNS
        )
        rotated_bitboard <<= shift
        return rotated_bitboard

    def set_rotate(self, bitboard: int):
        self.bitboard = bitboard
        self.rotation += 1
        if self.rotation > 3:
            self.rotation = 0
        
@dataclass
class Tetriminos:
    screen: pygame.display
    tetrimino: Optional[Tetrimino] = None

    def __post_init__(self):
        self.tiles: List[Tile] = []
        self.shape_generator = shape_generator()

    def get_tetrimino(self):
        if not self.tetrimino or self.tetrimino.locked:
            tile = next(tiles)
            shape = next(self.shape_generator)
            self.tetrimino = Tetrimino(shape, tile, self.screen)

        return self.tetrimino

    @staticmethod
    def collide(bitboard: int, obj: int):
        return bitboard & obj > 0

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
        collision_zone = bitboard >> COLUMNS
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

    def rotate(self):
        active_tetrimino = self.get_tetrimino()
        test_bitboard = active_tetrimino.test_rotate()

        full_board = all_borders
        for tile in self.tiles:
            full_board |= tile.bitboard

        if self.collide(full_board, test_bitboard):
            if not self.collide(test_bitboard >> 1, all_borders):
                test_bitboard >>= 1
            elif not self.collide(test_bitboard << 1, all_borders):
                test_bitboard <<= 1
            else:
                return

        active_tetrimino.set_rotate(test_bitboard)

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
