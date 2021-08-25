import textwrap
from typing import List

from src.settings import columns, rows

bottom_border: int = 0
for i in range(columns):
    bottom_border |= 1 << i

right_border: int = 0
for i in range(rows):
    right_border |= 1 << (i * 12)

left_border: int = right_border << (columns - 1)
top_border: int = bottom_border << ((columns) * (rows - 1))

all_borders: int = left_border | right_border | top_border | bottom_border

def print_board(name, board):
    print("\n")
    print(name)
    string_board = str(bin(board))[2:]
    string_board = string_board.zfill(22*12)
    for row in textwrap.wrap(string_board, 12):
        print(row)

def arrangement_to_bit(arrangement: List[List[int]]) -> int:
    bit = 0
    for row in arrangement:
        bit <<= 12
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
        if (bit:= i & x):
            bits.append(bit)
        i <<= 1
    return bits

if __name__ == "__main__":
    print_board("left_border", left_border)
    print_board("right_border", right_border)
    print_board("bottom_border", bottom_border)
    print_board("top_border", top_border)
    print_board("all", all_borders)

    i_tetri_start = 0b1111 << (18 * 12 - 11)
    print_board("tetri_start", i_tetri_start)

    i_tetri_collision = (i_tetri_start << 1) | (i_tetri_start >> 1) | (i_tetri_start >> 12)
    print_board("tetri_collision", i_tetri_collision)

    tetri_collision = i_tetri_collision & right_border
    print_board("tetri_collided", tetri_collision)
