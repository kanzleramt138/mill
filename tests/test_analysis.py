from dataclasses import replace

from mill.state import GameState, Stone
from mill.graph import MILLS, NEIGHBORS
from mill.analysis import (
    compute_threat_squares,
    mobility_by_pos,
    blocked_stones,
    mobility_profile,
    mobility_score,
    evaluate_light,
)


def _state_with_board(board_vals, to_move: Stone = Stone.WHITE) -> GameState:
    base = GameState.initial()
    return replace(
        base,
        board=tuple(board_vals),
        to_move=to_move,
        in_hand_white=0,
        in_hand_black=0,
        pending_remove=False,
    )


def test_compute_threat_squares_finds_single_open_mill_for_player() -> None:
    base = GameState.initial()
    board = list(base.board)

    a, b, c = MILLS[0]
    board[a] = Stone.WHITE
    board[b] = Stone.WHITE
    # c bleibt leer → offene Mühle

    state = _state_with_board(board, to_move=Stone.WHITE)

    threats = compute_threat_squares(state, Stone.WHITE)
    assert threats == {c}


def test_compute_threat_squares_ignores_lines_with_less_than_two_stones() -> None:
    base = GameState.initial()
    board = list(base.board)

    a, b, c = MILLS[0]
    board[a] = Stone.WHITE  # nur ein Stein

    state = _state_with_board(board, to_move=Stone.WHITE)

    threats = compute_threat_squares(state, Stone.WHITE)
    assert threats == set()


def test_compute_threat_squares_handles_multiple_open_mills() -> None:
    base = GameState.initial()
    board = list(base.board)

    (a1, b1, c1) = MILLS[0]
    (a2, b2, c2) = MILLS[1]

    board[a1] = board[b1] = Stone.BLACK
    board[a2] = board[b2] = Stone.BLACK

    state = _state_with_board(board, to_move=Stone.BLACK)

    threats = compute_threat_squares(state, Stone.BLACK)
    assert {c1, c2}.issubset(threats)

def test_mobility_by_pos_moving_counts_empty_neighbors() -> None:
    base = GameState.initial()
    board = list(base.board)

    pos = 0
    board[pos] = Stone.WHITE

    # ein paar zusätzliche WHITE-Steine (damit wir sicher nicht in FLYING sind)
    board[1] = Stone.WHITE
    board[2] = Stone.WHITE
    board[3] = Stone.WHITE

    state = replace(
        base,
        board=tuple(board),
        to_move=Stone.WHITE,
        in_hand_white=0,
        in_hand_black=0,
        pending_remove=False,
    )

    neighbors = NEIGHBORS[pos]
    expected = len([n for n in neighbors if state.board[n] == Stone.EMPTY])

    mob = mobility_by_pos(state, Stone.WHITE)
    assert mob[pos] == expected


def test_blocked_stones_finds_completely_blocked_piece() -> None:
    base = GameState.initial()
    board = list(base.board)

    pos = 0
    board[pos] = Stone.WHITE

    # alle Nachbarn von pos mit BLACK blockieren
    for n in NEIGHBORS[pos]:
        board[n] = Stone.BLACK

    # weitere WHITE-Steine, damit wir sicher nicht in FLYING sind
    board[5] = Stone.WHITE
    board[6] = Stone.WHITE
    board[7] = Stone.WHITE

    state = replace(
        base,
        board=tuple(board),
        to_move=Stone.WHITE,
        in_hand_white=0,
        in_hand_black=0,
        pending_remove=False,
    )

    blocked = blocked_stones(state, Stone.WHITE)
    assert pos in blocked


def test_mobility_flying_counts_all_empty_squares() -> None:
    base = GameState.initial()
    board = list(base.board)

    # genau drei WHITE-Steine → typischerweise FLYING
    stones = [0, 9, 21]
    for p in stones:
        board[p] = Stone.WHITE

    state = replace(
        base,
        board=tuple(board),
        to_move=Stone.WHITE,
        in_hand_white=0,
        in_hand_black=0,
        pending_remove=False,
    )

    empties = sum(1 for v in state.board if v == Stone.EMPTY)

    mob = mobility_by_pos(state, Stone.WHITE)
    # alle drei Steine sollten die gleiche Mobilität haben: alle leeren Felder
    for p in stones:
        assert mob[p] == empties

    # globaler Score = 3 * empties
    assert mobility_score(state, Stone.WHITE) == 3 * empties

def test_mobility_profile_counts_stones_and_blocked_ratio() -> None:
    base = GameState.initial()
    board = list(base.board)

    # Wähle eine Position für einen Stein
    blocked_pos = 0

    # blockiere alle Nachbarn von blocked_pos
    for n in NEIGHBORS[blocked_pos]:
        board[n] = Stone.BLACK

    # finde zwei weitere freie Positionen, die nicht blocked_pos sind
    free_positions: list[int] = []
    for i, v in enumerate(board):
        if v == Stone.EMPTY and i != blocked_pos:
            free_positions.append(i)
        if len(free_positions) == 2:
            break

    free_pos, another_free = free_positions

    # Drei WHITE-Steine
    board[blocked_pos] = Stone.WHITE
    board[free_pos] = Stone.WHITE
    board[another_free] = Stone.WHITE

    state = replace(
        base,
        board=tuple(board),
        to_move=Stone.WHITE,
        in_hand_white=0,
        in_hand_black=0,
        pending_remove=False,
    )

    prof = mobility_profile(state, Stone.WHITE)

    assert prof["total_stones"] == 3.0
    # Verhältnis ist immer wohldefiniert
    assert 0.0 <= prof["blocked_ratio"] <= 1.0
    # Konsistenz: movable + blocked darf total nicht überschreiten
    assert prof["movable_count"] + prof["blocked_count"] <= prof["total_stones"]

def test_evaluate_light_prefers_state_with_more_threats() -> None:
    base = GameState.initial()

    # s0: keine besonderen Drohungen
    s0 = _state_with_board(list(base.board), to_move=Stone.WHITE)

    # s1: WHITE hat eine offene Mühle
    board1 = list(base.board)
    a, b, c = MILLS[0]
    board1[a] = Stone.WHITE
    board1[b] = Stone.WHITE
    s1 = _state_with_board(board1, to_move=Stone.WHITE)

    assert evaluate_light(s1, Stone.WHITE) > evaluate_light(s0, Stone.WHITE)


def test_evaluate_light_prefers_state_with_more_mobility() -> None:
    base = GameState.initial()

    # s_blocked: ein WHITE-Stein komplett blockiert
    board_blocked = list(base.board)
    pos = 0
    board_blocked[pos] = Stone.WHITE
    for n in NEIGHBORS[pos]:
        board_blocked[n] = Stone.BLACK
    s_blocked = _state_with_board(board_blocked, to_move=Stone.WHITE)

    # s_free: derselbe Stein, aber Nachbarn frei
    board_free = list(base.board)
    board_free[pos] = Stone.WHITE
    s_free = _state_with_board(board_free, to_move=Stone.WHITE)

    assert evaluate_light(s_free, Stone.WHITE) > evaluate_light(s_blocked, Stone.WHITE)