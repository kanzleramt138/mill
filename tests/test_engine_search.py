from __future__ import annotations

from engine import Ply, Limits, analyze, best_move, classify_move_loss
from engine.eval import evaluate
from engine.movegen import legal_plies
from engine.search import _order_plies
from core.graph import MILLS
from core.state import GameState, Stone


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
    assert "double_threats" in breakdown
    assert "fork_threats" in breakdown
    assert "connectivity" in breakdown
    assert "initiative_strategic" in breakdown
    assert "initiative_tactical" in breakdown


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


def test_analyze_includes_threat_report() -> None:
    board = [Stone.EMPTY] * 24
    a, b, c = MILLS[0]
    board[a] = Stone.WHITE
    board[b] = Stone.WHITE

    state = GameState(
        board=tuple(board),
        to_move=Stone.WHITE,
        in_hand_white=7,
        in_hand_black=9,
        pending_remove=False,
        turn_no=1,
    )

    result = analyze(state, limits=Limits(max_depth=1), for_player=Stone.WHITE)

    assert result.threat_report.for_player == {c}
    assert result.threat_report.opponent == set()


def test_classify_move_loss_thresholds() -> None:
    thresholds = {
        "best": 0.1,
        "good": 0.5,
        "inaccuracy": 1.0,
        "mistake": 2.0,
    }

    assert classify_move_loss(0.0, thresholds) == "Best"
    assert classify_move_loss(0.1, thresholds) == "Best"
    assert classify_move_loss(0.4, thresholds) == "Good"
    assert classify_move_loss(0.9, thresholds) == "Inaccuracy"
    assert classify_move_loss(1.5, thresholds) == "Mistake"
    assert classify_move_loss(2.5, thresholds) == "Blunder"


def test_top_moves_breakdown_diff_matches_best_move() -> None:
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

    result = analyze(
        state,
        limits=Limits(max_depth=1, top_n=3),
        for_player=Stone.WHITE,
    )

    assert result.top_moves
    best = result.top_moves[0]
    assert best.breakdown
    for sm in result.top_moves:
        assert sm.breakdown
        assert sm.breakdown_diff
        # Verify that breakdown_diff includes keys from union of both breakdowns
        all_keys = set(best.breakdown) | set(sm.breakdown)
        assert set(sm.breakdown_diff.keys()) == all_keys
        # Verify the diff values are correct for all keys
        for key in all_keys:
            expected = best.breakdown.get(key, 0.0) - sm.breakdown.get(key, 0.0)
            assert sm.breakdown_diff.get(key, 0.0) == expected
