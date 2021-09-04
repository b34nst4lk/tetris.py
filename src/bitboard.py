import textwrap
from typing import List, Tuple

from src.settings import (
    columns,
    rows,
    tile_width,
    tile_height,
)

bottom_border: int = 0
for i in range(columns):
    bottom_border |= 1 << i

right_border: int = 0
for i in range(rows):
    right_border |= 1 << (i * 12)

left_border: int = right_border << (columns - 1)
top_border: int = bottom_border << ((columns) * (rows - 1))

all_borders: int = left_border | right_border | top_border | bottom_border


def print_board(name, board, height=rows, width=columns):
    print("\n")
    print(name)
    string_board = str(bin(board))[2:]
    string_board = string_board.zfill(height * width)
    for row in textwrap.wrap(string_board, width):
        print(row)


def arrangement_to_bit(arrangement: List[List[int]], width=columns) -> int:
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

def get_row_filter(width: int):
    row_filter = 0
    for i in range(width):
        row_filter |= 1 << i
    return row_filter

def rotate_bitboard(bitboard: int, width: int) -> int:
    """
    This function rotates a bitboard that is breath * breath in size clockwise
    """
    rotated = 0
    i = 0
    row_filter = get_row_filter(width)

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