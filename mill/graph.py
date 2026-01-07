# mill/graph.py
from __future__ import annotations

from typing import Dict, List, Tuple

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
