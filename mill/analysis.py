# mill/analysis.py
from __future__ import annotations

from dataclasses import replace
from typing import Dict, Set, List, Tuple, TYPE_CHECKING

from .graph import MILLS, NEIGHBORS
from .state import GameState, Stone, opponent, Phase
from .rules import phase_for, Action, legal_actions, apply_action, removable_positions

if TYPE_CHECKING:
    from engine.types import Ply


def _empty_positions(board: Tuple[Stone, ...]) -> List[int]:
    return [i for i, v in enumerate(board) if int(v) == int(Stone.EMPTY)]

def _positions_of(board: Tuple[Stone, ...], player: Stone) -> List[int]:
    return [i for i, v in enumerate(board) if int(v) == int(player)]

def _count_on_board(board: Tuple[Stone, ...], player: Stone) -> int:
    return sum(1 for v in board if int(v) == int(player))

def _effective_phase(state: GameState, player: Stone) -> Phase:
    """
    Effektive Phase: robuste Berechnung, flying nur bei exakt 3 Steinen auf dem Brett.
    """
    in_hand = state.in_hand_white if player == Stone.WHITE else state.in_hand_black
    on_board = _count_on_board(state.board, player)

    if in_hand > 0:
        return "placing"
    if on_board == 3:
        return "flying"
    return "moving"


def compute_threat_squares(state: GameState, player: Stone) -> Set[int]:
    """
    Felder, auf denen der `player` im nächsten Zug eine Mühle schließen kann
    (= offene Mühlen von `player`).
    """
    board = state.board
    empties = set(_empty_positions(board))

    def _threats_for(color: Stone) -> Set[int]:
        cand: dict[int, int] = {}
        for a, b, c in MILLS:
            vals = (board[a], board[b], board[c])
            occ = [i for i, v in zip((a, b, c), vals) if int(v) == int(color)]
            emp = [i for i, v in zip((a, b, c), vals) if int(v) == int(Stone.EMPTY)]
            if len(occ) == 2 and len(emp) == 1:
                pos = emp[0]
                if pos in empties:
                    cand.setdefault(pos, 0)
                    cand[pos] += 1

        if not cand:
            return set()
        
        ph = _effective_phase(state, color)
        positions = _positions_of(board, color)
        res: Set[int] = set()
        for pos in cand:
            if ph == "placing":
                res.add(pos)
            elif ph == "flying":
                if positions:
                    # kann von allen Steinen fliegen
                    res.add(pos)
            else:
                # moving: nur wenn ein Stein eine Verbindung zum Ziel hat
                for src in NEIGHBORS.get(pos, []):
                    if int(board[src]) == int(color):
                        res.add(pos)
                        break
        return res
    
    threatened = _threats_for(player)
    if not threatened:
        # Fallback: auch Gegner prüfen (für Defensive-Overlay/Tests)
        threatened = _threats_for(opponent(player))
    return threatened

def mobility_by_pos(state: GameState, player: Stone) -> Dict[int, int]:
    """
    Beweglichkeit je Stein:
      - moving: Anzahl leerer Nachbarfelder
      - flying: Anzahl aller leeren Felder
      - placing: nicht definiert → leeres Dict
    """
    board = state.board
    ph = _effective_phase(state, player)
    result: Dict[int, int] = {}

    if ph == "placing":
        return result

    positions = _positions_of(board, player)
    empties = set(_empty_positions(board))

    if ph == "flying":
        for p in positions:
            result[p] = len(empties)
        return result

    # moving
    for p in positions:
        moves = 0
        for nb in NEIGHBORS.get(p, []):
            if nb in empties:
                moves += 1
        result[p] = moves
    return result


def blocked_stones(state: GameState, player: Stone) -> Set[int]:
    """
    Blockierte Steine: Steine ohne leere Nachbarfelder.
    Nur sinnvoll in MOVING-Phase.
    """
    in_hand = (
        state.in_hand_white if player == Stone.WHITE else state.in_hand_black
    )
    if in_hand > 0:
        return set()
    
    board = state.board
    empties = set(_empty_positions(board))
    blocked: Set[int] = set()
    for p in _positions_of(board, player):
        if all((nb not in empties) for nb in NEIGHBORS.get(p, [])):
            blocked.add(p)
    return blocked


def mobility_score(state: GameState, player: Stone) -> int:
    """
    Einfache Mobility-Heuristik: Summe der Ziel-Felder (moving/flying), sonst 0.
    """
    return sum(mobility_by_pos(state, player).values())

def mobility_profile(state: GameState, player: Stone) -> Dict[str, float]:
    """
    Profilwerte für Overlay/Debug:
      - stones: Anzahl Steine
      - blocked: blockierte Steine (nur moving)
      - total_moves: Summe erreichbarer Felder
      - avg_moves: Durchschnitt pro Stein (0 bei 0 Steinen)
    """
    board = state.board
    stones = _count_on_board(board, player)
    total_moves = mobility_score(state, player)
    blocked = len(blocked_stones(state, player))
    avg = (total_moves / stones) if stones > 0 else 0.0
    movable = stones - blocked if stones > 0 else 0
    blocked_ratio = (blocked / stones) if stones > 0 else 0.0
    return {
        "stones": float(stones),
        "total_stones": float(stones),  # legacy key for compatibility
        "movable_count": float(movable),
        "blocked": float(blocked),
        "blocked_ratio": float(blocked_ratio),
        "total_moves": float(total_moves),
        "avg_moves": float(avg),
        "avg_mobility": float(avg),
    }


def evaluate_light(state: GameState, player: Stone) -> float:
    """
    Sehr leichte, erklärbare Heuristik (keine Suche):
        score = w_mat * Material + w_mob * (Mobility_p - Mobility_o) + w_threat * (#Threat_o - #Threat_p)
    """
    opp = opponent(player)
    w_mat = 10.0
    w_mob = 1.0
    w_thr = 2.0

    mat = _count_on_board(state.board, player) - _count_on_board(state.board, opp)
    mob = mobility_score(state, player) - mobility_score(state, opp)
    thr = len(compute_threat_squares(state, opp)) - len(compute_threat_squares(state, player))
    return w_mat * mat + w_mob * mob + w_thr * thr


def scored_actions_for_to_move(
    state: GameState,
    max_candidates: int = 5,
) -> List[Tuple[Action, float]]:
    """
    Very light ordering: bewerten nach Folgezustand mit evaluate_light (für den am Zug befindlichen Spieler).
    """
    to_move = state.to_move
    actions = legal_actions(state)
    scored: List[Tuple[Action, float]] = []
    for a in actions:
        nxt = apply_action(state, a)
        score = evaluate_light(nxt, to_move)
        scored.append((a, score))

    scored.sort(key=lambda t: t[1], reverse=True)
    return scored[:max_candidates]


def tactic_hints_for_ply(state: GameState, ply: Ply) -> Dict[str, object]:
    """
    Liefert taktische Hinweise für einen Halbzug:
      - verpasste Mill-in-1 Chance (vor dem Zug)
      - eröffnete Mill-in-1 Chance für den Gegner (nach dem Zug)
      - blockierte Steine beider Seiten (nach dem Zug)
    """
    # Runtime import to avoid circular dependency
    from engine.movegen import apply_ply
    
    player = state.to_move
    opp = opponent(player)

    threats_before_self = compute_threat_squares(state, player)
    threats_before_opp = compute_threat_squares(state, opp)

    used_threat_square = None
    if ply.kind in ("place", "move", "fly") and ply.dst is not None:
        if ply.dst in threats_before_self:
            used_threat_square = ply.dst

    missed_mill_in_1 = False
    if ply.kind != "remove" and threats_before_self and used_threat_square is None:
        missed_mill_in_1 = True

    next_state = apply_ply(state, ply)
    threats_after_opp = compute_threat_squares(next_state, opp)
    new_opp_threats = threats_after_opp - threats_before_opp

    blocked_white = blocked_stones(next_state, Stone.WHITE)
    blocked_black = blocked_stones(next_state, Stone.BLACK)

    return {
        "missed_mill_in_1": missed_mill_in_1,
        "missed_threats": threats_before_self,
        "used_threat_square": used_threat_square,
        "allowed_mill_in_1": bool(new_opp_threats),
        "allowed_threats": new_opp_threats,
        "blocked_white": blocked_white,
        "blocked_black": blocked_black,
    }
