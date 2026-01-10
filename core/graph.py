# core/graph.py
from __future__ import annotations

from typing import Callable, Dict, List, Tuple


__all__ = [
    "MILLS",
    "NEIGHBORS",
    "GRID_7x7",
    "SYMMETRY_MAPS",
]


# 24 positions indexed 0..23
# Grid layout (7x7) for UI placement (None = empty cell)
GRID_7x7 = [
    [0,  None, None, 1,  None, None, 2],
    [None, 3,  None, 4,  None, 5,  None],
    [None, None, 6,  7,  8,  None, None],
    [9,  10,  11, None, 12, 13, 14],
    [None, None, 15, 16, 17, None, None],
    [None, 18, None, 19, None, 20, None],
    [21, None, None, 22, None, None, 23],
]

# Adjacency list for Nine Men's Morris
NEIGHBORS: Dict[int, List[int]] = {
    0:  [1, 9],
    1:  [0, 2, 4],
    2:  [1, 14],
    3:  [4, 10],
    4:  [1, 3, 5, 7],
    5:  [4, 13],
    6:  [7, 11],
    7:  [4, 6, 8],
    8:  [7, 12],
    9:  [0, 10, 21],
    10: [3, 9, 11, 18],
    11: [6, 10, 15],
    12: [8, 13, 17],
    13: [5, 12, 14, 20],
    14: [2, 13, 23],
    15: [11, 16],
    16: [15, 17, 19],
    17: [12, 16],
    18: [10, 19],
    19: [16, 18, 20, 22],
    20: [13, 19],
    21: [9, 22],
    22: [19, 21, 23],
    23: [14, 22],
}

# All possible mills (16 lines of 3)
MILLS: List[Tuple[int, int, int]] = [
    (0, 1, 2),
    (3, 4, 5),
    (6, 7, 8),
    (9, 10, 11),
    (12, 13, 14),
    (15, 16, 17),
    (18, 19, 20),
    (21, 22, 23),

    (0, 9, 21),
    (3, 10, 18),
    (6, 11, 15),
    (1, 4, 7),
    (16, 19, 22),
    (8, 12, 17),
    (5, 13, 20),
    (2, 14, 23),
]

_GRID_SIZE = 7
_INDEX_TO_COORD: Dict[int, Tuple[int, int]] = {}
_COORD_TO_INDEX: Dict[Tuple[int, int], int] = {}
for _row_idx, _row in enumerate(GRID_7x7):
    for _col_idx, _pos in enumerate(_row):
        if _pos is None:
            continue
        _INDEX_TO_COORD[_pos] = (_row_idx, _col_idx)
        _COORD_TO_INDEX[(_row_idx, _col_idx)] = _pos


def _identity(r: int, c: int) -> Tuple[int, int]:
    return (r, c)


def _rot90(r: int, c: int) -> Tuple[int, int]:
    return (c, _GRID_SIZE - 1 - r)


def _rot180(r: int, c: int) -> Tuple[int, int]:
    return (_GRID_SIZE - 1 - r, _GRID_SIZE - 1 - c)


def _rot270(r: int, c: int) -> Tuple[int, int]:
    return (_GRID_SIZE - 1 - c, r)


def _reflect(r: int, c: int) -> Tuple[int, int]:
    return (r, _GRID_SIZE - 1 - c)


def _compose(
    first: Callable[[int, int], Tuple[int, int]],
    second: Callable[[int, int], Tuple[int, int]],
) -> Callable[[int, int], Tuple[int, int]]:
    def _composed(r: int, c: int) -> Tuple[int, int]:
        r2, c2 = first(r, c)
        return second(r2, c2)

    return _composed


def _build_symmetry_maps() -> List[Tuple[int, ...]]:
    transforms = [
        _identity,
        _rot90,
        _rot180,
        _rot270,
        _reflect,
        _compose(_reflect, _rot90),
        _compose(_reflect, _rot180),
        _compose(_reflect, _rot270),
    ]
    maps: List[Tuple[int, ...]] = []
    for transform in transforms:
        mapping: List[int] = [0] * 24
        for idx, (r, c) in _INDEX_TO_COORD.items():
            r2, c2 = transform(r, c)
            mapped = _COORD_TO_INDEX[(r2, c2)]
            mapping[idx] = mapped
        maps.append(tuple(mapping))
    return maps


SYMMETRY_MAPS: List[Tuple[int, ...]] = _build_symmetry_maps()
