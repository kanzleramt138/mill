# tests/test_eval_initiative.py
from __future__ import annotations

from core.state import GameState, Stone
from engine.eval import evaluate
from engine.types import EvalWeights


def test_initiative_strategic_suppresses_overlap() -> None:
    board = [Stone.EMPTY] * 24
    board[4] = Stone.WHITE
    state = GameState(
        board=tuple(board),
        to_move=Stone.WHITE,
        in_hand_white=8,
        in_hand_black=9,
        pending_remove=False,
        turn_no=1,
    )

    weights = EvalWeights(
        material=0.0,
        mills=0.0,
        open_mills=0.0,
        mobility=0.0,
        threats_mill_in_1=0.0,
        blocked_opponent=0.0,
        double_threats=0.0,
        connectivity=5.0,
        initiative_strategic=2.0,
        initiative_tactical=0.0,
    )

    score, breakdown = evaluate(state, Stone.WHITE, weights)

    assert breakdown["connectivity"] == 0.0
    assert breakdown["initiative_strategic"] == 8.0
    assert score == 8.0
