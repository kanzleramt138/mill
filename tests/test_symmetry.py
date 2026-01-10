from __future__ import annotations

from engine import Limits, analyze
from core.graph import SYMMETRY_MAPS
from core.rules import position_key_with_symmetry
from core.state import GameState, Stone


def _apply_symmetry(board: list[Stone], mapping: tuple[int, ...]) -> list[Stone]:
    sym_board = [Stone.EMPTY] * len(board)
    for idx, mapped in enumerate(mapping):
        sym_board[mapped] = board[idx]
    return sym_board


def _make_state(board: list[Stone]) -> GameState:
    white_on_board = sum(1 for x in board if x == Stone.WHITE)
    black_on_board = sum(1 for x in board if x == Stone.BLACK)
    return GameState(
        board=tuple(board),
        to_move=Stone.WHITE,
        in_hand_white=9 - white_on_board,
        in_hand_black=9 - black_on_board,
        pending_remove=False,
        turn_no=1,
    )


def test_position_key_with_symmetry_is_canonical() -> None:
    board = [Stone.EMPTY] * 24
    board[0] = Stone.WHITE
    board[1] = Stone.WHITE
    board[9] = Stone.BLACK

    mapping = SYMMETRY_MAPS[1]
    sym_board = _apply_symmetry(board, mapping)

    state = _make_state(board)
    sym_state = _make_state(sym_board)

    assert position_key_with_symmetry(state) == position_key_with_symmetry(sym_state)


def test_analyze_score_matches_for_symmetric_positions() -> None:
    board = [Stone.EMPTY] * 24
    board[0] = Stone.WHITE
    board[9] = Stone.WHITE
    board[2] = Stone.BLACK
    board[14] = Stone.BLACK

    mapping = SYMMETRY_MAPS[2]
    sym_board = _apply_symmetry(board, mapping)

    state = _make_state(board)
    sym_state = _make_state(sym_board)

    result = analyze(state, limits=Limits(max_depth=1), for_player=Stone.WHITE)
    sym_result = analyze(sym_state, limits=Limits(max_depth=1), for_player=Stone.WHITE)

    assert result.score == sym_result.score
