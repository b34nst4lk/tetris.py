import random
from itertools import cycle
from typing import List, Optional, Dict, Tuple, Callable
from dataclasses import dataclass
from abc import abstractmethod, ABC
import logging
from enum import Enum

import pygame
from pygame.surface import Surface

from src.settings import (
    SIZE,
    COLUMNS,
    ROWS,
    TILE_SIZE,
    SMALL_TILE_SIZE,
)

from utils.io import (
    asset_resource_path,
)

from utils.draw import (
    draw_scaffold,
)

from src.bitboard import (
    arrangement_to_bit,
    bitboard_height,
    bitboard_to_coords,
    bottom_border,
    decompose_bits,
    left_border,
    right_border,
    rotate_bitboard,
    top_border,
    widen_bitboard_width,
)

from utils.interpolation import (
    clamp,
    incomplete_perimeter_points,
)

from utils.easing import ease_in_sine

# Load assets
background_path = asset_resource_path("Board.png")
background = pygame.image.load(background_path)
background = pygame.transform.scale(background, SIZE)

COLORS = ["Blue", "Green", "LightBlue", "Orange", "Purple", "Red", "Yellow"]
tiles = {}
ghost_tiles = {}
small_tiles = {}
for color in COLORS:
    tile_path = asset_resource_path(f"{color}.png")
    tile = pygame.image.load(tile_path)
    tile = pygame.transform.scale(tile, TILE_SIZE)
    tiles[color] = tile

    ghost_tiles[color] = tile.copy()
    ghost_tiles[color].set_alpha(128)

    small_tile = tile.copy()
    small_tile = pygame.transform.scale(small_tile, SMALL_TILE_SIZE)
    small_tiles[color] = small_tile

colors = cycle(COLORS)

black_tile_path = asset_resource_path("Black.png")
black_tile = pygame.image.load(black_tile_path)
black_tile = pygame.transform.scale(black_tile, SMALL_TILE_SIZE)


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

trimmed_tetriminos: Dict[Shapes, List[List[int]]] = {}
for key, arrangement in tetriminos.items():
    trimmed_tetriminos[key] = [row for row in arrangement if sum(row) > 0]

tetriminos_widths: Dict[Shapes, int] = {}
for key, arrangement in tetriminos.items():
    tetriminos_widths[key] = len(arrangement[0])

tetriminos_height: Dict[Shapes, int] = {}
for key, arrangement in trimmed_tetriminos.items():
    tetriminos_height[key] = len(arrangement)


def render(
    screen: pygame.display,
    bits_and_tiles: Dict[int, Surface],
    offset,
    rows: int = ROWS,
    columns: int = COLUMNS,
    tile_size: Tuple[int, int] = TILE_SIZE,
):
    for bit, tile in bits_and_tiles.items():
        rect = tile.get_rect()

        tile_width, tile_height = tile_size
        x, y = bitboard_to_coords(bit, rows, columns, tile_width, tile_height)
        if x < 0 or y < 0:
            continue
        offset_x, offset_y = offset
        x += offset_x
        y += offset_y

        rect.update((x, y), tile_size)
        screen.blit(tile, rect)


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
        self.color = next(colors)

    def __iter__(self):
        return self

    def __next__(self) -> Tuple[Shapes, str]:
        self.queue.append(next(self.shape_generator))
        color = self.color
        self.color = next(colors)

        self.current = self.queue.pop(0), color
        return self.current

    def peek(self) -> Tuple[Shapes, str]:
        return self.queue[0], self.color


class TetriminoStash:
    def __init__(self):
        self.stashed: Optional[Tuple[Shapes, str]] = None

    def stash(self, to_stash) -> Optional[Tuple[Shapes, str]]:
        stashed, self.stashed = self.stashed, to_stash
        return stashed


@dataclass
class Widget(ABC):
    screen: pygame.display
    offset: Tuple[int, int]

    @abstractmethod
    def render(self):
        pass


@dataclass
class Text(Widget):
    size: Tuple[int, int]
    font: pygame.font.Font
    text: str = ""
    centered: bool = True

    def __post_init__(self):
        self.rect = pygame.rect.Rect(self.offset, self.size)

    def set_text(self, text):
        self.text = str(text)

    def render(self):
        text = self.font.render(self.text, 1, (255, 255, 255))
        x, y = self.offset
        if self.centered:
            x += self.rect.width / 2
            y += self.rect.height / 2
        draw_scaffold(self.screen, self.rect)
        self.screen.blit(text, text.get_rect(center=(x, y)))


class MouseInteraction(ABC):
    def push(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.on_move(event)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            self.on_click(event)
        elif event.type == pygame.MOUSEBUTTONUP:
            self.on_release(event)

    @abstractmethod
    def on_move(self, event):
        pass

    @abstractmethod
    def on_click(self, event):
        pass

    @abstractmethod
    def on_release(self, event):
        pass


@dataclass
class ReactiveText(Text, MouseInteraction):
    active_function: Callable = lambda weight: clamp(ease_in_sine(weight), 0, 1)
    inactive_function: Callable = lambda weight: 1 - clamp(ease_in_sine(weight), 0, 1)

    def __post_init__(self):
        super().__post_init__()
        self.start = self.end = None
        self.duration = 200
        self.active = False

    def on_click(self, event):
        print("down")

    def on_release(self, event):
        print("up")

    def on_move(self, event):
        collide = self.rect.collidepoint(event.pos) == 1
        if collide:
            if self.start:
                return
            self.start = pygame.time.get_ticks()
            self.end = None
            self.active = True
            return
        else:
            if self.start:
                self.start = None
                self.end = pygame.time.get_ticks()

            if self.end and pygame.time.get_ticks() - self.end >= self.duration:
                self.active = False

    def render(self):
        super().render()
        if not self.active:
            return

        now = pygame.time.get_ticks()
        weight = 0
        if self.start:
            time_passed = clamp((now - self.start) / self.duration, 0, 1)
            weight = self.active_function(time_passed)
        elif self.end:
            time_passed = clamp((now - self.end) / self.duration, 0, 1)
            weight = self.inactive_function(time_passed)

        if not weight:
            return

        points = [
            self.rect.topleft,
            self.rect.topright,
            self.rect.bottomright,
            self.rect.bottomleft,
        ]

        draw_points = incomplete_perimeter_points(points, weight)

        for p1, p2 in zip(draw_points, draw_points[1:]):
            pygame.draw.line(self.screen, (255, 255, 255), p1, p2)


@dataclass
class Tetrimino(Widget):
    shape: Shapes
    color: str
    arrangement: List[List[int]]
    columns: int = COLUMNS
    rows: int = ROWS
    size: str = "normal"
    placed: bool = False

    def __post_init__(self):
        if self.size == "normal":
            self.tile = tiles[self.color]
            self.tile_size = TILE_SIZE
        else:
            self.tile = small_tiles[self.color]
            self.tile_size = SMALL_TILE_SIZE
        self.setup()

    def setup(self):
        self.bitboard = arrangement_to_bit(self.arrangement, self.columns)
        self.tiles: Dict[int, Surface] = {}
        self.rotation: int = 0
        for bit in decompose_bits(self.bitboard):
            self.tiles[bit] = self.tile

    def move_to_start(self):
        self.bitboard = self.bitboard << (
            self.columns * (self.rows - 1) - self.columns // 2 - 2
        )

        self.update_tiles()

    def render(self):
        render(
            self.screen,
            self.tiles,
            self.offset,
            self.rows,
            self.columns,
            tile_size=self.tile_size,
        )

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

    def test_rotate(self, direction=1):
        # Prepare tetrimino for comparison
        current_rotation = self.rotation
        arrangement = tetriminos[self.shape]
        tetrimino_width = tetriminos_widths[self.shape]
        small_bitboard = arrangement_to_bit(arrangement, tetrimino_width)
        for _ in range(current_rotation):
            small_bitboard = rotate_bitboard(small_bitboard, tetrimino_width, direction)

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


@dataclass
class Ghost(Tetrimino):
    parent: Optional[Tetrimino] = None

    def __post_init__(self):
        self.tile = ghost_tiles[self.color]
        self.setup()

    def reset(self):
        self.bitboard = self.parent.bitboard
        self.update_tiles()

    def update(self, full_board: int):
        self.reset()
        while (self.bitboard >> self.columns) & (full_board | bottom_border) == 0:
            self.move_down()

    def render(self):
        render(self.screen, self.tiles, self.offset, self.rows, self.columns)


@dataclass
class TetriminoDisplay(Widget):
    tile_size: Tuple[int, int] = SMALL_TILE_SIZE

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

        self.tiles = {}
        for bit in decompose_bits(borders):
            self.tiles[bit] = black_tile

        self.tetrimino = None

    def set_tetrimino(self, shape: Shapes, color: str):
        if (
            self.tetrimino
            and self.tetrimino.color == color
            and self.tetrimino.shape == shape
        ):
            return

        tetrimno_column = tetriminos_widths[shape]
        tetrimno_row = tetriminos_height[shape]
        tile_width, tile_height = self.tile_size
        offset_x = int(
            (self.columns - tetrimno_column) / 2 * tile_width + self.offset[0]
        )
        offset_y = int((self.rows - tetrimno_row) / 2 * tile_height + self.offset[1])
        arrangement = trimmed_tetriminos[shape]

        self.tetrimino = Tetrimino(
            self.screen,
            (offset_x, offset_y),
            shape,
            color,
            arrangement,
            columns=tetriminos_widths[shape],
            rows=tetriminos_height[shape],
            size="small",
        )

    def render(self):
        render(
            self.screen,
            self.tiles,
            self.offset,
            self.rows,
            self.columns,
            tile_size=self.tile_size,
        )
        if self.tetrimino:
            self.tetrimino.render()


@dataclass
class Matrix(Widget):
    shape_generator: TetriminoQueue

    def __post_init__(self):
        self.tiles: Dict[int, Surface] = {}
        self.tetrimino: Optional[Tetrimino] = None
        self.stashed: Optional[Tuple[Shapes, str]] = None

    def get_tetrimino(self):
        if not self.tetrimino or self.tetrimino.placed:
            shape, color = next(self.shape_generator)
            arrangement = tetriminos[shape]
            self.tetrimino = Tetrimino(
                self.screen, self.offset, shape, color, arrangement
            )
            self.ghost = Ghost(
                self.screen,
                self.offset,
                shape,
                color,
                arrangement,
                parent=self.tetrimino,
            )
            self.tetrimino.move_to_start()
            self.ghost.update(self.get_full_board())

        return self.tetrimino

    def stash(self) -> Tuple[Shapes, str]:
        stashed, self.stashed = self.stashed, (
            self.tetrimino.shape,
            self.tetrimino.color,
        )
        if stashed:
            shape, color = stashed
            arrangement = tetriminos[shape]
            self.tetrimino = Tetrimino(
                self.screen, self.offset, shape, color, arrangement
            )
            self.ghost = Ghost(
                self.screen,
                self.offset,
                shape,
                color,
                arrangement,
                parent=self.tetrimino,
            )
            self.tetrimino.move_to_start()
            self.ghost.update(self.get_full_board())
        else:
            self.tetrimino = None
        return self.stashed

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
        line_filters = []
        for i in range(1, 5):
            line_filter = 0
            for j in range(i):
                line_filter |= bottom_border << COLUMNS * j

            line_filters.append(line_filter)
        line_filters = reversed(line_filters)
        lines_cleared = []

        for line_filter in line_filters:
            height = bitboard_height(line_filter)
            while line_filter < top_border:
                all_tiles = self.tiles
                full_board = self.get_full_board(include_borders=True)

                if (line_filter & full_board) != line_filter:
                    line_filter <<= COLUMNS
                    continue
                lines_cleared.append(height)

                for bit in decompose_bits(line_filter):
                    if bit in all_tiles:
                        del all_tiles[bit]

                shift_tiles = {
                    bit: tile for bit, tile in all_tiles.items() if bit > line_filter
                }

                shifted_tiles: Dict[int, Surface] = {}
                for bit, tile in shift_tiles.items():
                    bit >>= height * COLUMNS
                    shifted_tiles[bit] = tile

                static_tiles = {
                    bit: tile for bit, tile in all_tiles.items() if bit < line_filter
                }
                self.tiles = shifted_tiles | static_tiles

        return lines_cleared

    def move_down(self):
        tetrimino = self.get_tetrimino()
        if self.collide_bottom(tetrimino, bottom_border):
            self.tiles |= tetrimino.tiles
            tetrimino.placed = True
            return

        for bit in self.tiles:
            if self.collide_bottom(tetrimino, bit) and not tetrimino.placed:
                tetrimino.placed = True
                break

        if tetrimino.placed:
            self.tiles |= tetrimino.tiles
            tetrimino.placed = True
            return tetrimino

        tetrimino.move_down()
        self.ghost.update(self.get_full_board())

    def move_left(self):
        active_tetrimino = self.get_tetrimino()
        if self.collide_left(active_tetrimino, left_border):
            return

        for bit in self.tiles:
            if self.collide_left(active_tetrimino, bit):
                return

        self.get_tetrimino().move_left()
        self.ghost.update(self.get_full_board())

    def move_right(self):
        active_tetrimino = self.get_tetrimino()
        if self.collide_right(active_tetrimino, right_border):
            return

        for bit in self.tiles:
            if self.collide_right(active_tetrimino, bit):
                return

        self.get_tetrimino().move_right()
        self.ghost.update(self.get_full_board())

    def rotate(self, direction: int = 1):
        active_tetrimino = self.get_tetrimino()
        test_bitboard = active_tetrimino.test_rotate(direction)

        full_board = self.get_full_board(include_borders=True)

        if self.collide(full_board, test_bitboard):
            if not self.collide(test_bitboard >> 1, full_board):
                test_bitboard >>= 1
            elif not self.collide(test_bitboard << 1, full_board):
                test_bitboard <<= 1
            else:
                return

        active_tetrimino.set_rotate(test_bitboard)
        self.ghost.update(self.get_full_board())

    def render(self):
        self.screen.blit(background, self.offset)
        self.get_tetrimino().render()
        self.ghost.render()
        render(self.screen, self.tiles, self.offset)

    def is_game_over(self):
        for bit in self.tiles:
            if bit & top_border > 0:
                return True


def game_over():
    logging.warning("game over")
