# tests/test_analysis_basic.py
from __future__ import annotations
from mill.state import GameState, Stone
from mill.analysis import (
    compute_threat_squares,
    mobility_by_pos,
    blocked_stones,
    mobility_score,
    mobility_profile,
    evaluate_light,
)
from mill.graph import NEIGHBORS

def _empty_board() -> list[Stone]:
    return [Stone.EMPTY] * 24

def _state(board: list[Stone], to_move: Stone = Stone.WHITE) -> GameState:
    return GameState(
        board=tuple(board),
        to_move=to_move,
        in_hand_white=0,
        in_hand_black=0,
        pending_remove=False,
        turn_no=0,
    )

def test_threat_squares_detect_simple_closure_place_phase() -> None:
    b = _empty_board()
    # Gegner (BLACK) hat zwei Steine in einer Reihe (0,1,2), drittes Feld leer
    b[0] = Stone.BLACK
    b[1] = Stone.BLACK
    s = GameState(
        board=tuple(b),
        to_move=Stone.WHITE,
        in_hand_white=9,   # WHITE noch in placing, egal
        in_hand_black=9,   # BLACK ist in placing → kann überall setzen
        pending_remove=False,
        turn_no=0,
    )
    threats_vs_white = compute_threat_squares(s, Stone.WHITE)
    assert 2 in threats_vs_white

def test_mobility_by_pos_moving_and_blocked() -> None:
    # WHITE moving mit einem Stein p, alle Nachbarn von p sind belegt → blocked
    b = _empty_board()
    p = 10
    b[p] = Stone.WHITE
    for nb in NEIGHBORS[p]:
        b[nb] = Stone.BLACK
    s = _state(b, to_move=Stone.WHITE)
    moves = mobility_by_pos(s, Stone.WHITE)
    assert moves.get(p, 0) == 0
    blocked = blocked_stones(s, Stone.WHITE)
    assert p in blocked

def test_mobility_profile_consistency() -> None:
    b = _empty_board()
    b[0] = Stone.WHITE
    b[9] = Stone.WHITE
    s = _state(b)
    prof = mobility_profile(s, Stone.WHITE)
    assert prof["stones"] == 2.0
    assert prof["total_moves"] >= 0.0

def test_evaluate_light_material_monotonic() -> None:
    b1 = _empty_board()
    b2 = _empty_board()
    b1[0] = Stone.WHITE
    # b2 hat zusätzlich einen weiteren weißen Stein
    b2[0] = Stone.WHITE
    b2[1] = Stone.WHITE
    s1 = _state(b1)
    s2 = _state(b2)
    assert evaluate_light(s2, Stone.WHITE) > evaluate_light(s1, Stone.WHITE)