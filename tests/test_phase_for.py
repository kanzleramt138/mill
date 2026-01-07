from __future__ import annotations

from mill.rules import phase_for
from mill.state import GameState, Stone


def _empty_board() -> list[Stone]:
    return [Stone.EMPTY] * 24


def test_phase_for_placing_when_in_hand_gt_0() -> None:
    board = tuple(_empty_board())
    state = GameState(
        board=board,
        to_move=Stone.WHITE,
        in_hand_white=9,
        in_hand_black=9,
        pending_remove=False,
        turn_no=0,
    )

    assert phase_for(state, Stone.WHITE) == "placing"
    assert phase_for(state, Stone.BLACK) == "placing"


def test_phase_for_moving_when_no_in_hand_and_more_than_3_on_board() -> None:
    b = _empty_board()
    # 4 weiße Steine
    for i in (0, 1, 2, 3):
        b[i] = Stone.WHITE

    state = GameState(
        board=tuple(b),
        to_move=Stone.WHITE,
        in_hand_white=0,
        in_hand_black=0,
        pending_remove=False,
        turn_no=0,
    )

    assert phase_for(state, Stone.WHITE) == "moving"


def test_phase_for_flying_when_no_in_hand_and_exactly_3_on_board() -> None:
    b = _empty_board()
    # 3 weiße Steine
    for i in (0, 1, 2):
        b[i] = Stone.WHITE

    state = GameState(
        board=tuple(b),
        to_move=Stone.WHITE,
        in_hand_white=0,
        in_hand_black=0,
        pending_remove=False,
        turn_no=0,
    )

    assert phase_for(state, Stone.WHITE) == "flying"