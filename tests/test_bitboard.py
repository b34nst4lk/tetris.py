from src.bitboard import bitboard_to_coords

import pytest

samples = [
    # bit, (columns, rows), (result_x, result_y)
    (0b1, (1, 1), (0, 0)),
    (0b10, (1, 1), (0, -40)),
    (0b1, (2, 2), (40, 40)),
    (0b10, (2, 2), (0, 40)),
    (0b100, (2, 2), (40, 0)),
]


@pytest.mark.parametrize("bit,size,result", samples)
def test_bitboard_to_coords(bit, size, result):
    columns, rows = size
    assert bitboard_to_coords(bit, rows, columns) == result
