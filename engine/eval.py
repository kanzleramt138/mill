from __future__ import annotations

from typing import Tuple

from core.analysis import blocked_stones, compute_threat_squares, mobility_score
from core.graph import MILLS
from core.state import GameState, Stone, opponent

from .types import EvalBreakdown, EvalWeights


def evaluate(state: GameState, player: Stone, weights: EvalWeights | None = None) -> Tuple[float, EvalBreakdown]:
    """
    Light, explainable evaluation. Returns (score, breakdown) from player's POV.
    """
    if weights is None:
        weights = EvalWeights()
    opp = opponent(player)
    w_mat = weights.material
    w_mill = weights.mills
    w_open = weights.open_mills
    w_mob = weights.mobility
    w_thr = weights.threats_mill_in_1
    w_blk = weights.blocked_opponent

    mat = state.stones_on_board(player) - state.stones_on_board(opp)
    mills = _count_mills(state, player) - _count_mills(state, opp)
    open_mills = _count_open_mills(state, player) - _count_open_mills(state, opp)
    mob = mobility_score(state, player) - mobility_score(state, opp)
    thr = len(compute_threat_squares(state, opp, use_fallback=False)) - len(compute_threat_squares(state, player, use_fallback=False))
    blk = len(blocked_stones(state, opp)) - len(blocked_stones(state, player))

    breakdown: EvalBreakdown = {
        "material": w_mat * mat,
        "mills": w_mill * mills,
        "open_mills": w_open * open_mills,
        "mobility": w_mob * mob,
        "threats_mill_in_1": w_thr * thr,
        "blocked_opponent": w_blk * blk,
    }

    score = (
        breakdown["material"]
        + breakdown["mills"]
        + breakdown["open_mills"]
        + breakdown["mobility"]
        + breakdown["threats_mill_in_1"]
        + breakdown["blocked_opponent"]
    )
    return score, breakdown


def _count_open_mills(state: GameState, player: Stone) -> int:
    count = 0
    board = state.board
    for a, b, c in MILLS:
        vals = (board[a], board[b], board[c])
        own = sum(1 for v in vals if v == player)
        empty = sum(1 for v in vals if v == Stone.EMPTY)
        if own == 2 and empty == 1:
            count += 1
    return count


def _count_mills(state: GameState, player: Stone) -> int:
    count = 0
    board = state.board
    for a, b, c in MILLS:
        if board[a] == board[b] == board[c] == player:
            count += 1
    return count
