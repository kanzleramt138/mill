# mill/board_component.py
from __future__ import annotations


from pathlib import Path
from typing import Optional, TypedDict, Literal
import streamlit.components.v1 as components

class ActionEvent(TypedDict, total=False):
    kind: Literal["place", "move", "remove"]
    src: int
    dst: int
    nonce: int

# mill/board_component.py  -> mill/ (this file) -> project root -> muehle_board_component/
_COMPONENT_DIR = (Path(__file__).resolve().parent.parent / "muehle_board_component").resolve()

# Optional: helpful assertion (can comment out later)
if not (_COMPONENT_DIR / "index.html").exists():
    raise FileNotFoundError(f"Component frontend not found: {_COMPONENT_DIR / 'index.html'}")

_muehle_board = components.declare_component("muehle_board", path=str(_COMPONENT_DIR))

def muehle_board(
        *,
        svg: str,
        hotspots: list[dict],
        board: list[int],
        to_move: int,
        phase: str,
        pending_remove: bool,
        removables: list[int],
        hints_enabled: bool,
        key: str = "muehle_board") -> Optional[ActionEvent]:
     return _muehle_board(
         svg=svg,
         hotspots=hotspots,
         board=board,
         to_move=to_move,
         phase=phase,
         pending_remove=pending_remove,
         removables=removables,
         hints_enabled=hints_enabled,
         key=key,
         default=None,
    )