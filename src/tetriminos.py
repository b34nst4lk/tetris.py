from copy import deepcopy
import random
from itertools import cycle
from typing import List, Optional, Dict, Tuple
from dataclasses import dataclass
from abc import abstractmethod, ABC
import logging
from enum import Enum

import pygame
from pygame.rect import Rect
from pygame.surface import Surface

from src.settings import (
    SIZE,
    COLUMNS,
    ROWS,
    TILE_HEIGHT,
    TILE_SIZE,
    TILE_WIDTH,
)

from src.utils import asset_resource_path

from src.bitboard import (
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
background_path = asset_resource_path("Board.png")
background = pygame.image.load(background_path)
background = pygame.transform.scale(background, SIZE)

COLORS = ["Blue", "Green", "LightBlue", "Orange", "Purple", "Red", "Yellow"]

_tiles = []
for color in COLORS:
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


tetriminos_widths: Dict[Shapes, int] = {}
for key, arrangement in tetriminos.items():
    tetriminos_widths[key] = len(arrangement[0])

def render(screen: pygame.display, bits_and_tiles: Dict[int, Surface], offset, rows: int = ROWS, columns: int = COLUMNS):
    for bit, tile in bits_and_tiles.items():
        rect = tile.get_rect()

        x, y = bitboard_to_coords(bit, rows, columns)
        offset_x, offset_y = offset
        x += offset_x
        y += offset_y

        rect.update((x, y), TILE_SIZE)

        screen.blit(tile, rect) 

@dataclass
class Tile:
    bitboard: int
    rect: Rect
    tile: Surface
    screen: pygame.display
    offset: Tuple[int, int]
    rows: int = ROWS
    columns: int = COLUMNS

    def render(self, bitboard: Optional[int] = None):
        if not bitboard:
            bitboard = self.bitboard

        x, y = bitboard_to_coords(bitboard, self.rows, self.columns)
        offset_x, offset_y = self.offset
        self.rect.update((x + offset_x, y + offset_y), TILE_SIZE)
        self.screen.blit(self.tile, self.rect)
        self.bitboard = bitboard


@dataclass
class Tetrimino:
    shape: Shapes
    tile: pygame.Surface
    screen: pygame.display
    offset: Tuple[int, int]
    bitboard: int = 0
    rotation: int = 0
    columns: int = COLUMNS
    rows: int = ROWS
    locked: bool = False

    def __post_init__(self):
        arrangement = tetriminos[self.shape]
        bitboard = arrangement_to_bit(arrangement, self.columns)
        self.bitboard = bitboard << (
            self.columns * (self.rows - 1) - self.columns // 2 - 2
        )

        self.tiles: Dict[int, Surface] = {}
        for bit in decompose_bits(self.bitboard):
            self.tiles[bit] =(self.tile.copy())

    def render(self):
        render(self.screen, self.tiles, self.offset, self.rows, self.columns)

    def update_tiles(self):
        tiles: Dict[int, Surface] = {}
        bits = decompose_bits(self.bitboard)
        for bit, tile in zip(bits, self.tiles.values()):
            tiles[bit] = tile
        self.tiles = tiles             

    def move_down(self):
        self.bitboard >>= self.columns
        self.update_tiles()

    def move_left(self):
        self.bitboard <<= 1
        self.update_tiles()

    def move_right(self):
        self.bitboard >>= 1
        self.update_tiles()

    def test_rotate(self):
        # Prepare tetrimino for comparison
        current_rotation = self.rotation
        arrangement = tetriminos[self.shape]
        tetrimino_width = tetriminos_widths[self.shape]
        small_bitboard = arrangement_to_bit(arrangement, tetrimino_width)
        for _ in range(current_rotation):
            small_bitboard = rotate_bitboard(small_bitboard, tetrimino_width)

        compare_bitboard = widen_bitboard_width(
            small_bitboard, tetrimino_width, self.columns
        )

        # Trim current bitboard to identify shift
        bitboard = self.bitboard

        shift = 0
        while bitboard & bottom_border == 0:
            bitboard >>= self.columns
            shift += self.columns

        while bitboard != compare_bitboard:
            if bitboard > compare_bitboard:
                bitboard >>= 1
                shift += 1
            else:
                bitboard <<= 1
                shift -= 1

        small_bitboard = rotate_bitboard(small_bitboard, tetrimino_width)
        rotated_bitboard = widen_bitboard_width(
            small_bitboard, tetrimino_width, self.columns
        )
        rotated_bitboard <<= shift
        return rotated_bitboard

    def set_rotate(self, bitboard: int):
        self.bitboard = bitboard
        self.rotation += 1
        if self.rotation > 3:
            self.rotation = 0
        self.update_tiles()

def shape_generator():
    bag = []
    while True:
        if not bag:
            bag = list(Shapes)
            random.shuffle(bag)
        yield bag.pop(0)


class TetriminoQueue:
    def __init__(self):
        self.shape_generator = shape_generator()
        self.queue = [next(self.shape_generator) for _ in range(7)]
        self.tile = next(tiles)

    def __iter__(self):
        return self

    def __next__(self) -> Tuple[Shapes, Surface]:
        self.queue.append(next(self.shape_generator))
        tile = self.tile
        self.tile = next(tiles)
        return self.queue.pop(0), tile

    def peek(self) -> Tuple[Shapes, Surface]:
        return self.queue[0], self.tile


@dataclass
class Widget(ABC):
    screen: pygame.display
    offset: Tuple[int, int]

    @abstractmethod
    def render(self):
        pass


@dataclass
class NextTetrimino(Widget):
    def __post_init__(self):
        self.columns = 8
        self.rows = 6

        widget_bottom_border = 0
        for i in range(self.columns):
            widget_bottom_border |= 1 << i
        widget_top_border = widget_bottom_border << (self.columns * (self.rows - 1))
        widget_left_border = 0
        for i in range(self.rows):
            widget_left_border |= 1 << (self.columns * i)

        widget_right_border = widget_left_border << (self.columns - 1)
        borders = (
            widget_bottom_border
            | widget_top_border
            | widget_left_border
            | widget_right_border
        )

        tile = next(tiles)
        self.tiles = {}
        for bit in decompose_bits(borders):
            self.tiles[bit] = tile.copy()

        self.tetrimino = None

    def set_tetrimino(self, shape: Shapes, tile: Surface):
        if self.tetrimino and self.tetrimino.tile == tile and self.tetrimino.shape == shape:
            return

        self.tetrimino = Tetrimino(shape, tile, self.screen, self.offset, columns=self.columns, rows=self.rows)
        self.tetrimino.move_down()
        self.tetrimino.move_down()
        self.tetrimino.move_down()

    def render(self):
        # render(self.screen, self.tiles, self.offset, self.rows, self.columns)
        render(self.screen, self.tetrimino.tiles, self.offset, self.rows, self.columns)

@dataclass
class Game(Widget):
    shape_generator: TetriminoQueue

    def __post_init__(self):
        self.tiles: Dict[int, Surface] = {}
        self.tetrimino: Optional[Tetrimino] = None

    def get_tetrimino(self):
        if not self.tetrimino or self.tetrimino.locked:
            shape, tile = next(self.shape_generator)
            self.tetrimino = Tetrimino(shape, tile, self.screen, self.offset)

        return self.tetrimino

    def get_full_board(self, include_borders=False):
        full_board = (right_border | left_border) if include_borders else 0
        for tile in self.tiles:
            full_board |= tile
        return full_board

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

    def clear_lines(self):

        line_filter = bottom_border << COLUMNS
        while line_filter < top_border:
            all_tiles = self.tiles
            full_board = self.get_full_board(include_borders=True)

            if (line_filter & full_board) != line_filter:
                line_filter <<= COLUMNS
                continue

            for bit in decompose_bits(line_filter):
                if bit in all_tiles:
                    del all_tiles[bit]

            shift_tiles = {
                bit: tile for bit, tile in all_tiles.items() if bit > line_filter
            }

            shifted_tiles: Dict[int, Surface] = {}
            for bit, tile  in shift_tiles.items():
                bit >>= COLUMNS
                shifted_tiles[bit] = tile

            static_tiles = {
                bit: tile for bit, tile in all_tiles.items() if bit < line_filter
            }
            self.tiles = shifted_tiles | static_tiles

    def _move_down(self, tetrimino: Tetrimino) -> Tetrimino:
        if self.collide_bottom(tetrimino, bottom_border):
            self.tiles |= tetrimino.tiles
            tetrimino.locked = True
            return tetrimino

        for bit in self.tiles:
            if self.collide_bottom(tetrimino, bit) and not tetrimino.locked:
                tetrimino.locked = True
                break

        if tetrimino.locked:
            self.tiles |= tetrimino.tiles
            tetrimino.locked = True
            return tetrimino

        tetrimino.move_down()
        return tetrimino

    def move_down(self):
        active_tetrimino = self.get_tetrimino()
        self._move_down(active_tetrimino)

    def move_left(self):
        active_tetrimino = self.get_tetrimino()
        if self.collide_left(active_tetrimino, left_border):
            return

        for bit in self.tiles:
            if self.collide_left(active_tetrimino, bit):
                return

        self.get_tetrimino().move_left()

    def move_right(self):
        active_tetrimino = self.get_tetrimino()
        if self.collide_right(active_tetrimino, right_border):
            return

        for bit in self.tiles:
            if self.collide_right(active_tetrimino, bit):
                return

        self.get_tetrimino().move_right()

    def move_down_and_lock(self):
        active_tetrimino = self.get_tetrimino()
        while not active_tetrimino.locked:
            self._move_down(active_tetrimino)
            active_tetrimino.render()

    def rotate(self):
        active_tetrimino = self.get_tetrimino()
        test_bitboard = active_tetrimino.test_rotate()

        full_board = self.get_full_board(include_borders=True)

        if self.collide(full_board, test_bitboard):
            if not self.collide(test_bitboard >> 1, full_board):
                test_bitboard >>= 1
            elif not self.collide(test_bitboard << 1, full_board):
                test_bitboard <<= 1
            else:
                return

        active_tetrimino.set_rotate(test_bitboard)

    def render(self):
        self.screen.blit(background, self.offset)
        self.get_tetrimino().render()
        render(self.screen, self.tiles, self.offset)

    def is_game_over(self):
        for bit in self.tiles:
            if bit & top_border > 0:
                return True


def game_over():
    logging.warning("game over")
