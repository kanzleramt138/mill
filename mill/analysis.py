from __future__ import annotations

from typing import Dict, Set, List, Tuple

from .graph import MILLS, NEIGHBORS
from .state import GameState, Stone, opponent
from .rules import _phase_for, Action, legal_actions, apply_action

def compute_threat_squares(state: GameState, player: Stone) -> Set[int]:
    """
    Liefert alle Felder, auf denen `player` durch einen Stein dort
    eine Mühle vollenden würde (2 Steine des Spielers + 1 leeres Feld
    in derselben Mill-Linie). Bewegungs-Reichweite wird hier bewusst
    nicht geprüft – es geht um Mustererkennung, nicht um Legalität.
    """
    board = state.board
    threats: Set[int] = set()

    for a, b, c in MILLS:
        line = (a, b, c)
        stones = [p for p in line if board[p] == player]
        empties = [p for p in line if board[p] == Stone.EMPTY]

        if len(stones) == 2 and len(empties) == 1:
            threats.add(empties[0])

    return threats

def mobility_by_pos(state: GameState, player: Stone) -> Dict[int, int]:
    """
    Liefert für jeden Stein von `player` die Anzahl seiner potentiellen Ziel-Felder
    (reine Topologie, keine Mühlen-/Remove-Regeln):

      - in MOVING: Anzahl leerer Nachbarfelder
      - in FLYING: Anzahl aller leeren Felder
      - sonst (PLACING): 0 für alle (nicht definiert)
    """
    board = state.board
    phase = _phase_for(state, player)
    result: Dict[int, int] = {}

    if phase not in ("moving", "flying"):
        return result

    empties = [i for i, v in enumerate(board) if v == Stone.EMPTY]

    for idx, val in enumerate(board):
        if val != player:
            continue

        if phase == "moving":
            count = sum(1 for n in NEIGHBORS[idx] if board[n] == Stone.EMPTY)
        else:  # flying
            count = len(empties)

        result[idx] = count

    return result


def blocked_stones(state: GameState, player: Stone) -> Set[int]:
    """
    Alle Steine von `player`, die im aktuellen Zustand keine Bewegungsmöglichkeit haben.
    (Nur relevant für MOVING, ansonsten leere Menge.)
    """
    mob = mobility_by_pos(state, player)
    return {pos for pos, count in mob.items() if count == 0}


def mobility_score(state: GameState, player: Stone) -> int:
    """
    Ein einfacher globaler Mobilitäts-Score: Summe aller per-Stein-Mobilitäten.
    Eignet sich später als Feature für evaluate(state, player).
    """
    return sum(mobility_by_pos(state, player).values())

def mobility_profile(state: GameState, player: Stone) -> Dict[str, float]:
    """
    Liefert ein kleines Profil:
      - total_stones: Anzahl Steine von player
      - movable_count: Anzahl Steine mit mob > 0
      - blocked_count: Anzahl Steine mit mob == 0
      - blocked_ratio: blocked_count / total_stones
      - score: globaler mobility_score
      - avg_mobility: score / movable_count
    """
    board = state.board
    total_stones = sum(1 for v in board if v == player)

    mob = mobility_by_pos(state, player)
    score = sum(mob.values())

    # WICHTIG: nur Steine mit mob > 0 gelten als „beweglich“
    movable_count = sum(1 for count in mob.values() if count > 0)
    blocked_count = max(total_stones - movable_count, 0)

    blocked_ratio = (blocked_count / total_stones) if total_stones > 0 else 0.0
    avg_mobility = (score / movable_count) if movable_count > 0 else 0.0

    return {
        "total_stones": float(total_stones),
        "movable_count": float(movable_count),
        "blocked_count": float(blocked_count),
        "blocked_ratio": blocked_ratio,
        "score": float(score),
        "avg_mobility": avg_mobility,
    }

def evaluate_light(state: GameState, player: Stone) -> float:
    """
    Sehr einfache Heuristik, nur für Training/Analyse:

      score(player) =
        3.0 * (own_threats - opp_threats)
      + 0.5 * (own_mob_score - opp_mob_score)
      - 1.0 * (own_blocked - opp_blocked)

    Kein Material, keine Mill-Zählung – nur Strukturgefühl.
    """
    opp = opponent(player)

    own_threats = len(compute_threat_squares(state, player))
    opp_threats = len(compute_threat_squares(state, opp))

    own_mob = mobility_score(state, player)
    opp_mob = mobility_score(state, opp)

    own_prof = mobility_profile(state, player)
    opp_prof = mobility_profile(state, opp)

    own_blocked = own_prof["blocked_count"]
    opp_blocked = opp_prof["blocked_count"]

    threat_term = 3.0 * (own_threats - opp_threats)
    mob_term = 0.5 * (own_mob - opp_mob)
    blocked_term = 1.0 * (own_blocked - opp_blocked)

    return threat_term + mob_term - blocked_term

def scored_actions_for_to_move(
    state: GameState,
    max_candidates: int = 5,
) -> List[Tuple[Action, float]]:
    """
    Scort alle legal_actions(state) aus Sicht von state.to_move mit evaluate_light
    und gibt die besten max_candidates zurück (absteigend sortiert).
    """
    player = state.to_move
    actions = legal_actions(state)
    scored: List[Tuple[Action, float]] = []

    for act in actions:
        next_state = apply_action(state, act)
        score = evaluate_light(next_state, player)
        scored.append((act, score))

    scored.sort(key=lambda x: x[1], reverse=True)
    return scored[:max_candidates]