from __future__ import annotations

from core import (
    GameState,
    Stone,
    Phase,
    opponent,
    DrawTracker,
    MILLS,
    NEIGHBORS,
    GRID_7x7,
    Action,
    phase_for,
    legal_actions,
)

def test_public_api_imports() -> None:
    # Nur Existenz prüfen (kein Verhalten ändern)
    assert Stone.WHITE != Stone.BLACK
    assert isinstance(MILLS, (list, tuple))
    assert isinstance(NEIGHBORS, dict)
    assert isinstance(GRID_7x7, list)
    _ = (GameState, Phase, opponent, DrawTracker, Action, phase_for, legal_actions)