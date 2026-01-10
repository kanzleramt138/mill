from __future__ import annotations

from typing import Dict

from .graph import GRID_7x7
from .rules import Action
from .state import GameState

# Lazy-berechnete Map: Position (0..23) -> Koordinate wie a1..g7
_POS_LABEL_CACHE: Dict[int, str] = {}


def pos_label(pos: int) -> str:
    """
    Mappt eine Board-Position (0..23) auf eine Koordinate wie 'a7', 'd4'.
    Nutzt GRID_7x7, damit die Zuordnung konsistent mit der Domänen-Topologie ist.
    Oben ist Rank 7, unten Rank 1 (ähnlich Schach).
    """
    if pos in _POS_LABEL_CACHE:
        return _POS_LABEL_CACHE[pos]

    for row_idx, row in enumerate(GRID_7x7):
        for col_idx, cell in enumerate(row):
            if cell == pos:
                file_char = chr(ord("a") + col_idx)      # a..g
                rank = 7 - row_idx                       # 7..1
                label = f"{file_char}{rank}"
                _POS_LABEL_CACHE[pos] = label
                return label

    raise ValueError(f"No coordinate mapping for board position {pos}")


def action_to_notation(action: Action, *, before: GameState) -> str:
    """
    Erzeugt eine kompakte Notation:
      - P:a7   (place)
      - M:a7-d7 (move)
      - R:b4   (remove)
    """
    kind = action.kind
    dst = getattr(action, "dst", None)
    src = getattr(action, "src", None)

    if kind == "place" and dst is not None:
        return f"P:{pos_label(dst)}"
    if kind == "move" and src is not None and dst is not None:
        return f"M:{pos_label(src)}-{pos_label(dst)}"
    if kind == "remove" and dst is not None:
        return f"R:{pos_label(dst)}"

    # Fallback – sollte im Normalfall nicht auftreten
    return repr(action)