# tests/test_eval_tier2.py
from __future__ import annotations

import pytest

from core.graph import MILLS, RING_WEIGHT_BY_INDEX
from core.state import GameState, Stone
from engine.eval import evaluate
from engine.types import EvalWeights


def _make_state(
    board: list[Stone],
    *,
    in_hand_white: int,
    in_hand_black: int,
    to_move: Stone = Stone.WHITE,
) -> GameState:
    return GameState(
        board=tuple(board),
        to_move=to_move,
        in_hand_white=in_hand_white,
        in_hand_black=in_hand_black,
        pending_remove=False,
        turn_no=1,
    )


def test_evaluate_rewards_double_threats() -> None:
    board0 = [Stone.EMPTY] * 24
    a, _, c = MILLS[0]
    board0[a] = Stone.WHITE
    board0[c] = Stone.WHITE
    board0[4] = Stone.WHITE

    board1 = list(board0)
    board1[7] = Stone.WHITE

    state0 = _make_state(board0, in_hand_white=6, in_hand_black=9)
    state1 = _make_state(board1, in_hand_white=5, in_hand_black=9)

    weights = EvalWeights(
        material=0.0,
        mills=0.0,
        open_mills=0.0,
        mobility=0.0,
        threats_mill_in_1=0.0,
        blocked_opponent=0.0,
        double_threats=1.0,
        fork_threats=0.0,
        connectivity=0.0,
    )

    score0, _ = evaluate(state0, Stone.WHITE, weights)
    score1, _ = evaluate(state1, Stone.WHITE, weights)
    assert score1 > score0


def test_evaluate_rewards_fork_threats() -> None:
    board0 = [Stone.EMPTY] * 24
    a1, b1, c1 = MILLS[0]
    board0[a1] = Stone.WHITE
    board0[b1] = Stone.WHITE

    board1 = list(board0)
    a2, b2, c2 = MILLS[4]
    board1[a2] = Stone.WHITE
    board1[b2] = Stone.WHITE

    state0 = _make_state(board0, in_hand_white=7, in_hand_black=9)
    state1 = _make_state(board1, in_hand_white=6, in_hand_black=9)

    weights = EvalWeights(
        material=0.0,
        mills=0.0,
        open_mills=0.0,
        mobility=0.0,
        threats_mill_in_1=0.0,
        blocked_opponent=0.0,
        double_threats=0.0,
        fork_threats=1.0,
        connectivity=0.0,
    )

    score0, _ = evaluate(state0, Stone.WHITE, weights)
    score1, _ = evaluate(state1, Stone.WHITE, weights)

    expected = RING_WEIGHT_BY_INDEX[c1] + RING_WEIGHT_BY_INDEX[c2]
    assert score0 == 0.0
    assert score1 == pytest.approx(expected)


def test_evaluate_rewards_connectivity() -> None:
    board_low = [Stone.EMPTY] * 24
    board_low[0] = Stone.WHITE

    board_high = [Stone.EMPTY] * 24
    board_high[4] = Stone.WHITE

    state0 = _make_state(board_low, in_hand_white=8, in_hand_black=9)
    state1 = _make_state(board_high, in_hand_white=8, in_hand_black=9)

    weights = EvalWeights(
        material=0.0,
        mills=0.0,
        open_mills=0.0,
        mobility=0.0,
        threats_mill_in_1=0.0,
        blocked_opponent=0.0,
        double_threats=0.0,
        fork_threats=0.0,
        connectivity=1.0,
    )

    score0, _ = evaluate(state0, Stone.WHITE, weights)
    score1, _ = evaluate(state1, Stone.WHITE, weights)
    assert score1 > score0
