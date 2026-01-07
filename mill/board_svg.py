# mill/board_svg.py
from __future__ import annotations

from typing import Dict, Tuple, Set, Optional

from .state import GameState, Stone

# Coordinate system: 0..600 (square)
# Classic Nine Men's Morris: 3 squares + midpoints
# 24 nodes in standard indexing matching your graph.py
POS: Dict[int, Tuple[int, int]] = {
    0:  (60, 60),    1: (300, 60),   2: (540, 60),
    3:  (140, 140),  4: (300, 140),  5: (460, 140),
    6:  (220, 220),  7: (300, 220),  8: (380, 220),
    9:  (60, 300),   10:(140, 300),  11:(220, 300),
    12: (380, 300),  13:(460, 300),  14:(540, 300),
    15: (220, 380),  16:(300, 380),  17:(380, 380),
    18: (140, 460),  19:(300, 460),  20:(460, 460),
    21: (60, 540),   22:(300, 540),  23:(540, 540),
}

# Edges to draw (undirected). Must reflect your NEIGHBORS.
# List each edge once.
EDGES = [
    (0,1),(1,2),
    (3,4),(4,5),
    (6,7),(7,8),
    (9,10),(10,11),
    (12,13),(13,14),
    (15,16),(16,17),
    (18,19),(19,20),
    (21,22),(22,23),

    (0,9),(9,21),
    (3,10),(10,18),
    (6,11),(11,15),
    (1,4),(4,7),
    (16,19),(19,22),
    (8,12),(12,17),
    (5,13),(13,20),
    (2,14),(14,23),
]

def _stone_svg(x: int, y: int, stone: Stone, selected: bool=False) -> str:
    # iOS-like light mode: subtle shadow, clean border
    if stone == Stone.WHITE:
        fill = "#FFFFFF"
        stroke = "rgba(0,0,0,0.18)"
    elif stone == Stone.BLACK:
        fill = "#111827"  # near-black
        stroke = "rgba(0,0,0,0.22)"
    else:
        return ""

    ring = ""
    if selected:
        ring = f'<circle cx="{x}" cy="{y}" r="24" fill="none" stroke="rgba(0,122,255,0.33)" stroke-width="3"/>'

    return f"""
    <g>
      {ring}
      <circle cx="{x}" cy="{y}" r="18" fill="{fill}" stroke="{stroke}" stroke-width="1.5"/>
      <circle cx="{x}" cy="{y}" r="18" fill="none" stroke="rgba(0,0,0,0.06)" stroke-width="2"/>
    </g>
    """

def render_board_svg(state: GameState, selected_src: Optional[int]=None, size: int = 640, hint_targets: Optional[Set[int]]=None, hint_removables: Optional[Set[int]]=None) -> str:

    # Avoid mutable default args
    hint_targets = hint_targets or set()
    hint_removables = hint_removables or set()

    # ViewBox is 0..600; scale via width/height
    # Light mode styling
    bg = "#F5F5F7"
    line = "rgba(60,60,67,0.28)"        # thin lines
    node = "rgba(60,60,67,0.22)"        # node ring
    node_fill = "#BCBABA"

    # Build edges
    edge_svg = []
    for a,b in EDGES:
        x1,y1 = POS[a]
        x2,y2 = POS[b]
        edge_svg.append(
            f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{line}" stroke-width="5" stroke-linecap="round"/>'
        )

    # Nodes (click targets visually)
    node_svg = []
    for i,(x,y) in POS.items():
        node_svg.append(
            f'<circle cx="{x}" cy="{y}" r="8" fill="{node_fill}" stroke="{node}" stroke-width="2"/>'
        )

    # Overlays: legal targets (blue), removable (red)
    targets_svg = []
    for pos in hint_targets:
        x,y = POS[pos]
        targets_svg.append(
            f'<circle cx="{x}" cy="{y}" r="13" fill="rgba(0,122,255,0.18)" stroke="rgba(0,122,255,0.33)" stroke-width="3"/>'
        )

    removables_svg = []
    for pos in hint_removables:
        x,y = POS[pos]
        removables_svg.append(
            f'<circle cx="{x}" cy="{y}" r="24" fill="rgba(255,0,0,0.18)" stroke="rgba(255,0,0,0.33)" stroke-width="3"/>'
        )

    # Stones
    stones_svg = []
    for i, stone in enumerate(state.board):
        if stone == Stone.EMPTY:
            continue
        x,y = POS[i]
        stones_svg.append(_stone_svg(x, y, stone, selected=(selected_src == i)))

    svg = f"""
    <svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 600 600">
      <rect x="0" y="0" width="600" height="600" rx="24" fill="{bg}"/>
      <g>{''.join(edge_svg)}</g>
      <g>{''.join(node_svg)}</g>
      <g>{''.join(targets_svg)}</g>
      <g>{''.join(removables_svg)}</g>
      <g>{''.join(stones_svg)}</g>
    </svg>
    """
    return svg
