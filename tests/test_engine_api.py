from __future__ import annotations
from mill.state import GameState, Stone
from engine import analyze, best_move, Limits, AnalysisResult, Ply

def test_engine_analyze_shape() -> None:
    s = GameState  # nur Typzugriff; konkrete Instanziierung ist projektspezifisch
    limits = Limits(time_ms=300, max_depth=3)
    # Wir prüfen nur, dass analyze ein AnalysisResult liefert
    result = analyze(s, limits=limits, for_player=Stone.WHITE)  # type: ignore[arg-type]
    assert isinstance(result, AnalysisResult) or hasattr(result, "best_move")

def test_engine_best_move_none_for_stub() -> None:
    s = GameState  # Stub-Call, keine echte Suche
    mv = best_move(s, limits=Limits(time_ms=200), for_player=Stone.BLACK)  # type: ignore[arg-type]
    assert mv is None