from __future__ import annotations

from typing import Tuple

from core.analysis import (
    blocked_stones,
    compute_threat_squares,
    double_threat_squares,
    fork_threat_score,
    mobility_score,
)
from core.graph import MILLS, NEIGHBORS
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
    w_double = weights.double_threats
    w_fork = weights.fork_threats
    w_conn = weights.connectivity
    w_init_strat = weights.initiative_strategic
    w_init_tact = weights.initiative_tactical

    use_initiative = w_init_strat != 0.0 or w_init_tact != 0.0
    if use_initiative:
        w_mob = 0.0
        w_open = 0.0
        w_thr = 0.0
        w_blk = 0.0
        w_double = 0.0
        w_fork = 0.0
        w_conn = 0.0

    mat = state.stones_on_board(player) - state.stones_on_board(opp)
    mills = _count_mills(state, player) - _count_mills(state, opp)
    open_mills = _count_open_mills(state, player) - _count_open_mills(state, opp)
    mob = mobility_score(state, player) - mobility_score(state, opp)
    thr = len(compute_threat_squares(state, opp, use_fallback=False)) - len(compute_threat_squares(state, player, use_fallback=False))
    blk = len(blocked_stones(state, opp)) - len(blocked_stones(state, player))
    double_thr = len(double_threat_squares(state, player)) - len(double_threat_squares(state, opp))
    fork_thr = fork_threat_score(state, player) - fork_threat_score(state, opp)
    conn = _connectivity_score(state, player) - _connectivity_score(state, opp)
    init_strat = mob + open_mills + blk + conn
    init_tact = thr + double_thr + fork_thr

    breakdown: EvalBreakdown = {
        "material": w_mat * mat,
        "mills": w_mill * mills,
        "open_mills": w_open * open_mills,
        "mobility": w_mob * mob,
        "threats_mill_in_1": w_thr * thr,
        "blocked_opponent": w_blk * blk,
        "double_threats": w_double * double_thr,
        "fork_threats": w_fork * fork_thr,
        "connectivity": w_conn * conn,
        "initiative_strategic": w_init_strat * init_strat,
        "initiative_tactical": w_init_tact * init_tact,
    }

    score = (
        breakdown["material"]
        + breakdown["mills"]
        + breakdown["open_mills"]
        + breakdown["mobility"]
        + breakdown["threats_mill_in_1"]
        + breakdown["blocked_opponent"]
        + breakdown["double_threats"]
        + breakdown["fork_threats"]
        + breakdown["connectivity"]
        + breakdown["initiative_strategic"]
        + breakdown["initiative_tactical"]
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


def _connectivity_score(state: GameState, player: Stone) -> int:
    total = 0
    for idx, stone in enumerate(state.board):
        if stone == player:
            total += len(NEIGHBORS[idx])
    return total
