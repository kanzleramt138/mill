from __future__ import annotations

import pytest

from engine import Ply, apply_ply, legal_plies
from mill.state import GameState, Stone


def test_legal_plies_place_includes_removes_on_mill() -> None:
    board = [Stone.EMPTY] * 24
    board[0] = Stone.WHITE
    board[1] = Stone.WHITE
    board[3] = Stone.BLACK

    state = GameState(
        board=tuple(board),
        to_move=Stone.WHITE,
        in_hand_white=7,
        in_hand_black=7,
        pending_remove=False,
        turn_no=1,
    )

    plies = legal_plies(state)
    closing = [p for p in plies if p.kind == "place" and p.dst == 2]

    assert closing, "Placement auf 2 muss angeboten werden"
    assert all(p.remove is not None for p in closing), "Mill-Schluss erfordert Remove-Kandidaten"
    assert any(p.remove == 3 for p in closing)


def test_legal_plies_only_remove_when_pending() -> None:
    board = [Stone.EMPTY] * 24
    board[0] = Stone.WHITE
    board[1] = Stone.WHITE
    board[2] = Stone.WHITE
    board[3] = Stone.BLACK

    state = GameState(
        board=tuple(board),
        to_move=Stone.WHITE,
        in_hand_white=6,
        in_hand_black=7,
        pending_remove=True,
        turn_no=2,
    )

    plies = legal_plies(state)

    assert plies
    assert all(p.kind == "remove" for p in plies)
    assert any(p.remove == 3 for p in plies)


def test_apply_ply_move_with_remove_executes_both_steps() -> None:
    board = [Stone.EMPTY] * 24
    board[0] = Stone.WHITE
    board[21] = Stone.WHITE
    board[10] = Stone.WHITE
    board[3] = Stone.BLACK
    board[3] = Stone.BLACK

    state = GameState(
        board=tuple(board),
        to_move=Stone.WHITE,
        in_hand_white=0,
        in_hand_black=0,
        pending_remove=False,
        turn_no=5,
    )

    ply = Ply(kind="move", src=10, dst=9, remove=3)
    nxt = apply_ply(state, ply)

    assert nxt.board[21] == Stone.WHITE
    assert nxt.board[9] == Stone.WHITE
    assert nxt.board[10] == Stone.EMPTY
    assert nxt.board[3] == Stone.EMPTY
    assert nxt.to_move == Stone.BLACK
    assert not nxt.pending_remove


def test_apply_ply_raises_when_remove_missing_on_mill() -> None:
    board = [Stone.EMPTY] * 24
    board[0] = Stone.WHITE
    board[21] = Stone.WHITE
    board[10] = Stone.WHITE
    board[3] = Stone.BLACK

    state = GameState(
        board=tuple(board),
        to_move=Stone.WHITE,
        in_hand_white=0,
        in_hand_black=0,
        pending_remove=False,
        turn_no=5,
    )

    ply = Ply(kind="move", src=10, dst=9)

    with pytest.raises(ValueError):
        apply_ply(state, ply)
