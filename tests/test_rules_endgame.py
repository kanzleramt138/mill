from dataclasses import replace
from typing import List

from core.graph import MILLS, NEIGHBORS
from core.state import GameState, Stone
import core.rules as rules
from core.rules import (
    removable_positions,
    is_terminal,
    winner,
    legal_actions,
)


def _state_with_board(board_vals: List[Stone], *, to_move: Stone) -> GameState:
    """Hilfsfunktion: baut einen GameState aus GameState.initial() + neuem Board."""
    base = GameState.initial()
    return replace(
        base,
        board=tuple(board_vals),
        to_move=to_move,
        in_hand_white=0,
        in_hand_black=0,
        pending_remove=False,
    )


def test_removable_positions_prefers_non_mill_stones() -> None:
    """Wenn Opfer-Steine außerhalb von Mühlen existieren, dürfen nur diese entfernt werden."""
    base = GameState.initial()
    board = list(base.board)

    # Eine komplette WHITE-Mühle auf dem ersten MILLS-Triple
    a, b, c = MILLS[0]
    board[a] = board[b] = board[c] = Stone.WHITE

    # Ein weiterer WHITE-Stein außerhalb einer vollen Mühle
    outside = 3  # liegt in keiner vollen Mühle, da Nachbarn leer bleiben
    board[outside] = Stone.WHITE

    state = replace(base, board=tuple(board))

    rem = removable_positions(state, Stone.WHITE)
    assert rem == [outside]


def test_removable_positions_all_in_mills_returns_all() -> None:
    """Sind alle Opfer-Steine in Mühlen, dürfen alle entfernt werden."""
    base = GameState.initial()
    board = list(base.board)

    # Fülle zwei (ggf. überlappende) Mühlen komplett mit WHITE
    for line in MILLS[:2]:
        for pos in line:
            board[pos] = Stone.WHITE

    state = replace(base, board=tuple(board))

    victim_positions = sorted(i for i, x in enumerate(state.board) if x == Stone.WHITE)
    rem = sorted(removable_positions(state, Stone.WHITE))
    assert rem == victim_positions


def test_terminal_and_winner_when_player_has_less_than_three_stones() -> None:
    """Hat ein Spieler nach dem Setzen <3 Steine, ist das Spiel terminal und der Gegner gewinnt."""
    base = GameState.initial()
    board = list(base.board)

    # WHITE: nur 2 Steine
    board[0] = Stone.WHITE
    board[1] = Stone.WHITE

    # BLACK: genügend Steine (>=3)
    board[10] = Stone.BLACK
    board[11] = Stone.BLACK
    board[12] = Stone.BLACK

    state = _state_with_board(board, to_move=Stone.WHITE)

    assert is_terminal(state) is True
    assert winner(state) == Stone.BLACK


def test_terminal_and_winner_when_to_move_has_no_legal_moves(monkeypatch) -> None:
    """Hat to_move keine legalen Züge (moving/flying) obwohl er >=3 Steine hat, verliert er."""
    base = GameState.initial()
    board = list(base.board)

    # to_move (WHITE) hat mindestens 3 Steine auf dem Brett
    board[0] = Stone.WHITE
    board[1] = Stone.WHITE
    board[2] = Stone.WHITE

    # Gegner (BLACK) hat ebenfalls >=3 Steine, damit nicht durch "<3 Steine" verliert
    board[10] = Stone.BLACK
    board[11] = Stone.BLACK
    board[12] = Stone.BLACK

    state = _state_with_board(board, to_move=Stone.WHITE)

    # Simuliere: es gibt keine legalen Aktionen
    import core.rules as rules
    monkeypatch.setattr(rules, "legal_actions", lambda _s: [])

    assert rules.legal_actions(state) == []

    assert is_terminal(state) is True
    assert winner(state) == Stone.BLACK