from __future__ import annotations

from typing import List, Optional

from mill.state import GameState, Stone
from .types import AnalysisResult, Limits, Ply

def analyze(state: GameState, limits: Limits | None = None, for_player: Stone | None = None) -> AnalysisResult:
    # Stub: keine Suche, nur API-Form
    _ = (limits, for_player)
    return AnalysisResult(
        best_move=None,
        score=0.0,
        depth=0,
        nodes=0,
        pv=[],
        breakdown={},
    )

def best_move(state: GameState, limits: Limits | None = None, for_player: Stone | None = None) -> Optional[Ply]:
    # Stub: keine Suche, liefert None
    _ = (limits, for_player)
    return None