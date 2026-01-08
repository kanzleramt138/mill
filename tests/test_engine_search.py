from __future__ import annotations

from engine import Ply, Limits, analyze, best_move
from engine.eval import evaluate
from engine.movegen import legal_plies
from engine.search import _order_plies
from mill.state import GameState, Stone


def test_best_move_returns_legal_ply() -> None:
    board = [Stone.EMPTY] * 24
    board[0] = Stone.WHITE
    board[9] = Stone.BLACK

    state = GameState(
        board=tuple(board),
        to_move=Stone.WHITE,
        in_hand_white=8,
        in_hand_black=8,
        pending_remove=False,
        turn_no=1,
    )

    mv = best_move(state, limits=Limits(max_depth=1), for_player=Stone.WHITE)
    assert mv is not None
    assert mv in legal_plies(state)


def test_order_plies_prefers_tt_then_captures() -> None:
    plies = [
        Ply(kind="move", src=0, dst=1),
        Ply(kind="move", src=2, dst=3, remove=4),
        Ply(kind="move", src=5, dst=6),
    ]
    tt_best = plies[2]
    board = [Stone.EMPTY] * 24
    state = GameState(
        board=tuple(board),
        to_move=Stone.WHITE,
        in_hand_white=9,
        in_hand_black=9,
        pending_remove=False,
        turn_no=1,
    )
    ordered = _order_plies(state, plies, tt_best)
    assert ordered[0] == tt_best
    assert ordered[1].remove is not None


def test_evaluate_breakdown_includes_mills_keys() -> None:
    state = GameState.initial()
    _, breakdown = evaluate(state, Stone.WHITE)

    assert "mills" in breakdown
    assert "open_mills" in breakdown


def test_analyze_returns_top_moves_with_pv() -> None:
    board = [Stone.EMPTY] * 24
    board[0] = Stone.WHITE
    board[9] = Stone.BLACK

    state = GameState(
        board=tuple(board),
        to_move=Stone.WHITE,
        in_hand_white=8,
        in_hand_black=8,
        pending_remove=False,
        turn_no=1,
    )

    result = analyze(state, limits=Limits(max_depth=1), for_player=Stone.WHITE)

    assert result.top_moves
    assert all(tm.ply in legal_plies(state) for tm in result.top_moves)
    assert all(tm.pv and tm.pv[0] == tm.ply for tm in result.top_moves)
