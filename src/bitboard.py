import textwrap
from typing import List, Tuple

from src.settings import (
    COLUMNS,
    ROWS,
    TILE_WIDTH,
    TILE_HEIGHT,
)

bottom_border: int = 0
for i in range(COLUMNS):
    bottom_border |= 1 << i

right_border: int = 0
for i in range(ROWS):
    right_border |= 1 << (i * 12)

left_border: int = right_border << (COLUMNS - 1)
top_border: int = bottom_border << ((COLUMNS) * (ROWS - 1))

all_borders: int = left_border | right_border | top_border | bottom_border


def print_board(name, board, height=ROWS, width=COLUMNS):
    print("\n")
    print(name)
    string_board = str(bin(board))[2:]
    string_board = string_board.zfill(height * width)
    for row in textwrap.wrap(string_board, width):
        print(row)


def arrangement_to_bit(arrangement: List[List[int]], width=COLUMNS) -> int:
    bit = 0
    for row in arrangement:
        bit <<= width
        row_bit = 0
        for tile in row:
            row_bit <<= 1
            if tile == 0:
                continue
            row_bit |= 1
        bit |= row_bit

    return bit


def decompose_bits(x: int) -> List[int]:
    bits = []
    i = 1
    while i <= x:
        if bit := i & x:
            bits.append(bit)
        i <<= 1
    return bits


def get_bottom_border(columns: int) -> int:
    border = 0
    for shift in range(columns):
        border |= 1 << shift
    return border


def get_top_border(columns: int, rows: int) -> int:
    border = get_bottom_border(columns)
    border <<= columns * (rows - 1)
    return border


def get_right_border(columns: int, rows: int) -> int:
    border = 0
    for shift in range(rows):
        border |= 1 << (shift * columns)
    return border


def get_left_border(columns: int, rows: int) -> int:
    border = get_right_border(columns, rows)
    border <<= columns - 1
    return border


def bitboard_to_row(bitboard: int, rows: int = ROWS, columns: int = COLUMNS) -> int:
    row = 1
    while bitboard & get_bottom_border(columns) == 0:
        bitboard >>= columns
        row += 1
    return rows - row


def bitboard_to_column(bitboard: int, columns: int = COLUMNS, rows: int = ROWS) -> int:
    column = 1
    while bitboard & get_right_border(columns, rows) == 0:
        bitboard >>= 1
        column += 1

    return columns - column


def bitboard_bottom(bitboard: int, rows: int = ROWS, columns: int = COLUMNS) -> int:
    if bitboard == 0:
        return 0

    for row in range(rows):
        if bitboard & bottom_border > 0:
            return row
        bitboard >>= columns
    return rows


def bitboard_top(bitboard: int, rows: int = ROWS, columns: int = COLUMNS) -> int:
    if bitboard == 0:
        return 0

    for row in range(rows):
        if bitboard >> columns == 0:
            return row
        bitboard >>= columns

    return rows


def bitboard_height(bitboard: int, rows: int = ROWS, columns: int = COLUMNS):
    top = bitboard_top(bitboard, rows, columns)
    bottom = bitboard_bottom(bitboard, rows, columns)
    return top - bottom + 1


def bitboard_line_filters(start, end) -> List[int]:
    if start > end:
        raise ValueError
    line_filter = 0
    for i in range(start, end + 1):
        line_filter |= bottom_border << (i * COLUMNS)

    line_filters = [line_filter]
    for i in range(start, end + 1):
        line_filters.append(bottom_border << (i * COLUMNS))

    return line_filters


def bitboard_to_coords(
    bitboard: int,
    rows: int = ROWS,
    columns: int = COLUMNS,
    tile_width: int = TILE_WIDTH,
    tile_height: int = TILE_HEIGHT,
) -> Tuple[int, int]:
    only_one_bit = len(decompose_bits(bitboard)) == 1
    if not only_one_bit:
        raise ValueError("bitboard contains more than one bit")

    row = bitboard_to_row(bitboard, rows, columns)
    column = bitboard_to_column(bitboard, columns)

    coords = (column * tile_width, row * tile_height)
    return coords


def get_row_filter(width: int):
    row_filter = 0
    for i in range(width):
        row_filter |= 1 << i
    return row_filter


def rotate_bitboard(bitboard: int, width: int, rotations: int = 1) -> int:
    """
    This function rotates a bitboard that is breath * breath in size clockwise
    """
    rotated = 0
    i = 0
    row_filter = get_row_filter(width)

    if rotations < 0:
        rotations = 4 + rotations

    for _ in range(rotations):
        while bitboard > 0:
            row = bitboard & row_filter
            row_values = decompose_bits(row)
            for row_value in row_values:
                bit_length = row_value.bit_length()
                shift = (bit_length - 1) * width + (width - i - 1)
                rotated |= 1 << shift
            bitboard >>= width
            i += 1
    return rotated


def widen_bitboard_width(bitboard: int, width: int, new_width: int) -> int:
    new_bitboard = 0
    row_filter = get_row_filter(width)

    row_num = 0
    while bitboard > 0:
        row = bitboard & row_filter
        new_bitboard |= row << (row_num * new_width)
        bitboard >>= width
        row_num += 1

    return new_bitboard


if __name__ == "__main__":
    print_board("left_border", left_border)
    print_board("right_border", right_border)
    print_board("bottom_border", bottom_border)
    print_board("top_border", top_border)
    print_board("all", all_borders)

    i_tetri_start = 0b1111 << (18 * 12 - 11)
    print_board("tetri_start", i_tetri_start)

    i_tetri_collision = (
        (i_tetri_start << 1) | (i_tetri_start >> 1) | (i_tetri_start >> 12)
    )
    print_board("tetri_collision", i_tetri_collision)

    tetri_collision = i_tetri_collision & right_border
    print_board("tetri_collided", tetri_collision)
