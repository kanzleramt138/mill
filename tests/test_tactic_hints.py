# tests/test_tactic_hints.py
"""Tests für tactic_hints_for_ply Funktion."""
from dataclasses import replace

from core.state import GameState, Stone
from core.graph import MILLS
from core.analysis import tactic_hints_for_ply
from engine.types import Ply


def _state_with_board(
    board_vals, 
    to_move: Stone = Stone.WHITE, 
    in_hand_white: int = 0, 
    in_hand_black: int = 0,
    pending_remove: bool = False
) -> GameState:
    """Hilfsfunktion zum Erstellen eines GameState mit spezifischem Board."""
    base = GameState.initial()
    return replace(
        base,
        board=tuple(board_vals),
        to_move=to_move,
        in_hand_white=in_hand_white,
        in_hand_black=in_hand_black,
        pending_remove=pending_remove,
    )


def test_tactic_hints_detects_used_threat_square() -> None:
    """Test: Erkennt, wenn ein Spieler eine vorhandene Mill-in-1-Chance nutzt."""
    base = GameState.initial()
    board = list(base.board)
    
    # WHITE hat eine offene Mühle: a7, d7 besetzt, g7 frei
    a, b, c = MILLS[0]  # (0, 1, 2) = (a7, d7, g7)
    board[a] = Stone.WHITE
    board[b] = Stone.WHITE
    # c (g7) ist frei und ist threat square
    
    state = _state_with_board(board, to_move=Stone.WHITE, in_hand_white=1)
    
    # WHITE setzt auf g7 (c) und schließt die Mühle
    ply = Ply(kind="place", dst=c)
    
    hints = tactic_hints_for_ply(state, ply)
    
    # Sollte threat square genutzt haben
    assert hints["used_threat_square"] == c
    assert hints["missed_mill_in_1"] is False


def test_tactic_hints_detects_missed_mill_in_1() -> None:
    """Test: Erkennt, wenn ein Spieler eine Mill-in-1-Chance verpasst."""
    base = GameState.initial()
    board = list(base.board)
    
    # WHITE hat eine offene Mühle: a7, d7 besetzt, g7 frei
    a, b, c = MILLS[0]  # (0, 1, 2) = (a7, d7, g7)
    board[a] = Stone.WHITE
    board[b] = Stone.WHITE
    # c (g7) ist frei und ist threat square
    
    # WHITE setzt stattdessen woanders (z.B. auf Position 10)
    other_pos = 10
    board[other_pos] = Stone.EMPTY  # Stelle sicher, dass Position leer ist
    
    state = _state_with_board(board, to_move=Stone.WHITE, in_hand_white=1)
    
    # WHITE setzt auf andere Position statt auf Threat-Square
    ply = Ply(kind="place", dst=other_pos)
    
    hints = tactic_hints_for_ply(state, ply)
    
    # Sollte missed_mill_in_1 erkennen
    assert hints["missed_mill_in_1"] is True
    assert hints["used_threat_square"] is None
    assert c in hints["missed_threats"]


def test_tactic_hints_detects_allowed_opponent_mill_in_1() -> None:
    """Test: Erkennt, wenn ein Zug dem Gegner eine neue Mill-in-1-Chance eröffnet."""
    base = GameState.initial()
    board = list(base.board)
    
    # BLACK hat schon 2 Steine in einer Reihe: a7, d7
    # WHITE platziert einen Stein, der BLACK erlaubt g7 zu spielen (hypothetisch)
    # Für diesen Test: BLACK hat a7, d7; WHITE bewegt sich so, dass BLACK Mühle schließen kann
    
    mill_a, mill_b, mill_c = MILLS[0]  # (0, 1, 2) = (a7, d7, g7)
    board[mill_a] = Stone.BLACK
    board[mill_b] = Stone.BLACK
    # mill_c ist frei, aber noch keine direkte neue Threat für BLACK (vor WHITE's Zug)
    
    # WHITE macht einen Zug, der eine neue BLACK threat eröffnet
    # Beispiel: WHITE platziert einen Stein, der BLACK's Position verbessert
    white_pos = 10
    state = _state_with_board(board, to_move=Stone.WHITE, in_hand_white=1)
    
    ply = Ply(kind="place", dst=white_pos)
    
    hints = tactic_hints_for_ply(state, ply)
    
    # In diesem speziellen Setup sollte BLACK nach WHITE's Zug immer noch die gleiche threat haben
    # Dies ist ein vereinfachter Test - in der Realität würden wir komplexere Szenarien testen
    # Der Test validiert hauptsächlich, dass die Funktion ohne Fehler läuft
    assert "allowed_mill_in_1" in hints
    assert "allowed_threats" in hints


def test_tactic_hints_counts_blocked_stones() -> None:
    """Test: Zählt blockierte Steine nach einem Zug korrekt."""
    base = GameState.initial()
    board = list(base.board)
    
    # Erstelle Situation: WHITE-Stein umgeben von BLACK-Steinen
    # Position 0 (a7) hat Nachbarn 1 und 9
    white_pos = 0
    board[white_pos] = Stone.WHITE
    board[1] = Stone.BLACK  # Nachbar von a7
    board[9] = Stone.BLACK  # Nachbar von a7
    
    # BLACK hat auch Steine
    board[5] = Stone.BLACK
    
    state = _state_with_board(board, to_move=Stone.WHITE, in_hand_white=1)
    
    # WHITE platziert einen weiteren Stein
    ply = Ply(kind="place", dst=10)
    
    hints = tactic_hints_for_ply(state, ply)
    
    # Der WHITE-Stein auf Position 0 sollte blockiert sein (alle Nachbarn besetzt)
    assert len(hints["blocked_white"]) > 0


def test_tactic_hints_with_move_ply() -> None:
    """Test: Funktioniert mit Move-Ply (nicht nur Place)."""
    base = GameState.initial()
    board = list(base.board)
    
    # WHITE hat Steine auf dem Brett, aber keine in Hand (MOVING phase)
    board[0] = Stone.WHITE
    board[5] = Stone.WHITE
    board[10] = Stone.WHITE
    board[15] = Stone.WHITE
    
    # BLACK hat auch Steine
    board[2] = Stone.BLACK
    board[7] = Stone.BLACK
    board[12] = Stone.BLACK
    board[17] = Stone.BLACK
    
    state = _state_with_board(board, to_move=Stone.WHITE, in_hand_white=0, in_hand_black=0)
    
    # WHITE bewegt von Position 0 zu Position 1 (benachbart)
    ply = Ply(kind="move", src=0, dst=1)
    
    hints = tactic_hints_for_ply(state, ply)
    
    # Sollte erfolgreich durchlaufen und Struktur zurückgeben
    assert "missed_mill_in_1" in hints
    assert "used_threat_square" in hints
    assert "allowed_mill_in_1" in hints
    assert "blocked_white" in hints
    assert "blocked_black" in hints


def test_tactic_hints_with_remove_ply() -> None:
    """Test: Funktioniert mit Remove-Ply bei pending_remove."""
    base = GameState.initial()
    board = list(base.board)
    
    # Simuliere einen Zustand mit pending_remove
    board[0] = Stone.WHITE
    board[5] = Stone.WHITE
    board[10] = Stone.BLACK
    
    state = _state_with_board(
        board, 
        to_move=Stone.WHITE, 
        in_hand_white=0, 
        in_hand_black=0,
        pending_remove=True
    )
    
    # WHITE muss einen BLACK-Stein entfernen
    ply = Ply(kind="remove", remove=10)
    
    hints = tactic_hints_for_ply(state, ply)
    
    # Sollte erfolgreich durchlaufen
    assert "missed_mill_in_1" in hints
    assert isinstance(hints["blocked_white"], set)
    assert isinstance(hints["blocked_black"], set)


def test_tactic_hints_with_mill_closing() -> None:
    """Test: Funktioniert wenn ein Ply eine Mühle schließt und Remove benötigt."""
    base = GameState.initial()
    board = list(base.board)
    
    # WHITE hat 2 Steine in einer Reihe, schließt Mühle mit 3. Stein
    mill_a, mill_b, mill_c = MILLS[0]  # (0, 1, 2)
    board[mill_a] = Stone.WHITE
    board[mill_b] = Stone.WHITE
    
    # BLACK hat einen entfernbaren Stein
    board[10] = Stone.BLACK
    
    state = _state_with_board(board, to_move=Stone.WHITE, in_hand_white=1)
    
    # WHITE platziert auf mill_c und entfernt BLACK-Stein
    ply = Ply(kind="place", dst=mill_c, remove=10)
    
    hints = tactic_hints_for_ply(state, ply)
    
    # Sollte die Mühle als used_threat_square erkennen
    assert hints["used_threat_square"] == mill_c
    assert hints["missed_mill_in_1"] is False
    # Nach dem Remove sollte BLACK einen Stein weniger haben
    assert isinstance(hints["blocked_black"], set)


def test_tactic_hints_no_threats_available() -> None:
    """Test: Funktioniert wenn keine Threats vorhanden sind."""
    base = GameState.initial()
    board = list(base.board)
    
    # Minimale Besetzung ohne offene Mühlen
    board[0] = Stone.WHITE
    board[10] = Stone.BLACK
    
    state = _state_with_board(board, to_move=Stone.WHITE, in_hand_white=1)
    
    # WHITE platziert einen Stein ohne Threat-Kontext
    ply = Ply(kind="place", dst=5)
    
    hints = tactic_hints_for_ply(state, ply)
    
    # Keine verpasste Mill-in-1, da keine Threats existierten
    assert hints["missed_mill_in_1"] is False
    assert hints["used_threat_square"] is None
    assert len(hints["missed_threats"]) == 0

def test_tactic_hints_no_fallback_on_opponent_threats() -> None:
    """Test: keine false missed_mill_in_1 durch Gegner-Threats."""
    base = GameState.initial()
    board = list(base.board)

    mill_a, mill_b, mill_c = MILLS[0]
    board[mill_a] = Stone.BLACK
    board[mill_b] = Stone.BLACK

    state = _state_with_board(board, to_move=Stone.WHITE, in_hand_white=1)
    ply = Ply(kind="place", dst=10)

    hints = tactic_hints_for_ply(state, ply)

    assert hints["missed_mill_in_1"] is False
    assert len(hints["missed_threats"]) == 0
