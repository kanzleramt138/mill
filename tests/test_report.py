from __future__ import annotations

from engine import Limits, analyze, classify_move_loss, score_ply
from engine.report import summarize_last_move
from engine.movegen import legal_plies
from core.state import GameState


def _thresholds() -> dict[str, float]:
    return {
        "best": 0.1,
        "good": 0.5,
        "inaccuracy": 1.0,
        "mistake": 2.0,
    }


def test_summarize_last_move_in_top_n() -> None:
    state = GameState.initial()
    limits = Limits(max_depth=1, top_n=3)
    thresholds = _thresholds()

    result = analyze(state, limits=limits, for_player=state.to_move)
    last_ply = result.top_moves[0].ply

    summary = summarize_last_move(
        state,
        last_ply,
        limits=limits,
        thresholds=thresholds,
    )

    assert summary.in_top_n is True
    assert summary.score == result.top_moves[0].score
    assert summary.pv == result.top_moves[0].pv
    assert summary.loss >= 0.0
    assert summary.label == classify_move_loss(summary.loss, thresholds)


def test_summarize_last_move_not_in_top_n_uses_score_ply() -> None:
    state = GameState.initial()
    limits = Limits(max_depth=1, top_n=1)
    thresholds = _thresholds()

    result = analyze(state, limits=limits, for_player=state.to_move)
    plies = legal_plies(state)
    assert len(plies) > 1

    last_ply = next(p for p in plies if p != result.top_moves[0].ply)
    summary = summarize_last_move(
        state,
        last_ply,
        limits=limits,
        thresholds=thresholds,
    )

    expected_score, expected_pv = score_ply(
        state,
        last_ply,
        limits=limits,
        for_player=state.to_move,
    )
    expected_loss = max(0.0, result.score - expected_score)

    assert summary.in_top_n is False
    assert summary.score == expected_score
    assert summary.pv == expected_pv
    assert summary.loss == expected_loss
    assert summary.label == classify_move_loss(summary.loss, thresholds)
