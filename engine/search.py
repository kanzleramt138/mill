from __future__ import annotations

from dataclasses import dataclass, field
import time
from typing import Dict, List, Optional, Tuple, Literal

from mill.graph import MILLS
from mill.rules import draw_reason, forms_mill_after_placement, winner
from mill.rules import position_key_from_state, position_key_with_symmetry
from mill.state import GameState, Stone

from .eval import evaluate
from .movegen import apply_ply, legal_plies
from .types import AnalysisResult, Limits, Ply, ScoredMove, EvalBreakdown, EvalWeights

MATE_SCORE = 1_000_000.0
DEFAULT_TOP_N_MOVES = 5


@dataclass
class _SearchContext:
    for_player: Stone
    deadline: float | None
    max_nodes: int | None
    tt: Dict[int, "_TTEntry"] | None = field(default_factory=dict)
    eval_weights: EvalWeights = field(default_factory=EvalWeights)
    nodes: int = 0
    tt_hits: int = 0
    tt_misses: int = 0
    stopped: bool = False


@dataclass
class _TTEntry:
    depth: int
    score: float
    flag: Literal["exact", "lower", "upper"]
    best_ply: Ply | None
    score_only: bool = False


def analyze(state: GameState, limits: Limits | None = None, for_player: Stone | None = None) -> AnalysisResult:
    """
    Alpha-Beta + Iterative Deepening. Score ist aus Sicht von for_player.
    """
    if not _is_valid_state(state):
        return AnalysisResult(
            best_move=None,
            score=0.0,
            depth=0,
            nodes=0,
            tt_hits=0,
            tt_misses=0,
            pv=[],
            top_moves=[],
            breakdown={},
        )

    if limits is None:
        limits = Limits()

    max_depth = limits.max_depth or 1
    for_player = for_player or state.to_move
    deadline = (
        time.perf_counter() + (limits.time_ms / 1000.0)
        if limits.time_ms
        else None
    )

    use_tt = True if limits.use_tt is None else limits.use_tt
    top_n = DEFAULT_TOP_N_MOVES if limits.top_n is None else limits.top_n
    eval_weights = limits.eval_weights or EvalWeights()
    ctx = _SearchContext(
        for_player=for_player,
        deadline=deadline,
        max_nodes=limits.max_nodes,
        tt={} if use_tt else None,
        eval_weights=eval_weights,
    )

    best_move: Optional[Ply] = None
    best_score = 0.0
    best_pv: List[Ply] = []
    reached_depth = 0
    top_moves: List[ScoredMove] = []

    for depth in range(1, max_depth + 1):
        score, pv, depth_top_moves, stopped = _negamax_root(state, depth, ctx, best_move, top_n)
        if stopped:
            break
        reached_depth = depth
        best_score = score
        best_pv = pv
        top_moves = depth_top_moves
        best_move = pv[0] if pv else None

    _, breakdown = evaluate(state, for_player, ctx.eval_weights)
    return AnalysisResult(
        best_move=best_move,
        score=best_score,
        depth=reached_depth,
        nodes=ctx.nodes,
        tt_hits=ctx.tt_hits,
        tt_misses=ctx.tt_misses,
        pv=best_pv,
        top_moves=top_moves,
        breakdown=breakdown,
    )


def best_move(state: GameState, limits: Limits | None = None, for_player: Stone | None = None) -> Optional[Ply]:
    if not _is_valid_state(state):
        return None
    result = analyze(state, limits=limits, for_player=for_player)
    return result.best_move


def score_ply(
    state: GameState,
    ply: Ply,
    limits: Limits | None = None,
    for_player: Stone | None = None,
) -> Tuple[float, List[Ply]]:
    """
    Bewertet einen vorgegebenen Halbzug: Ply anwenden, dann Suche mit depth-1.
    Score ist aus Sicht von for_player.
    """
    if not _is_valid_state(state):
        return 0.0, []

    if limits is None:
        limits = Limits()

    max_depth = limits.max_depth or 1
    depth = max(0, max_depth - 1)
    for_player = for_player or state.to_move
    deadline = (
        time.perf_counter() + (limits.time_ms / 1000.0)
        if limits.time_ms
        else None
    )
    use_tt = True if limits.use_tt is None else limits.use_tt
    eval_weights = limits.eval_weights or EvalWeights()

    ctx = _SearchContext(
        for_player=for_player,
        deadline=deadline,
        max_nodes=limits.max_nodes,
        tt={} if use_tt else None,
        eval_weights=eval_weights,
    )

    nxt = apply_ply(state, ply)
    color = 1.0 if state.to_move == for_player else -1.0
    score, child_pv, stopped = _negamax(
        nxt,
        depth,
        float("-inf"),
        float("inf"),
        -color,
        ctx,
    )
    if stopped:
        return 0.0, []
    score = -score
    return score, [ply] + child_pv


def _negamax_root(
    state: GameState,
    depth: int,
    ctx: _SearchContext,
    prev_best: Ply | None,
    top_n: int,
) -> Tuple[float, List[Ply], List[ScoredMove], bool]:
    alpha = float("-inf")
    beta = float("inf")
    color = 1.0 if state.to_move == ctx.for_player else -1.0
    plies = _order_plies(state, legal_plies(state), prev_best)
    best_score = float("-inf")
    best_pv: List[Ply] = []
    scored_raw: List[Tuple[Ply, float, List[Ply], EvalBreakdown]] = []
    scored: List[ScoredMove] = []
    for ply in plies:
        nxt = apply_ply(state, ply)
        _, breakdown = evaluate(nxt, ctx.for_player, ctx.eval_weights)
        score, child_pv, stopped = _negamax(nxt, depth - 1, -beta, -alpha, -color, ctx)
        if stopped:
            return best_score, best_pv, [], True
        score = -score

        _, breakdown = evaluate(nxt, ctx.for_player, ctx.eval_weights)
        scored_raw.append((ply, score, [ply] + child_pv, breakdown))

        if score > best_score:
            best_score = score
            best_pv = [ply] + child_pv
        if score > alpha:
            alpha = score
    best_breakdown = _best_breakdown(scored_raw)
    scored: List[ScoredMove] = []
    for ply, score, pv, breakdown in scored_raw:
        scored.append(
            ScoredMove(
                ply=ply,
                score=score,
                pv=pv,
                breakdown=breakdown,
                breakdown_diff=_diff_breakdowns(best_breakdown, breakdown),
            )
        )
    scored.sort(key=lambda s: s.score, reverse=True)
    
    return best_score, best_pv, scored[:top_n], False


def _negamax(
    state: GameState,
    depth: int,
    alpha: float,
    beta: float,
    color: float,
    ctx: _SearchContext,
    root_hint: Ply | None = None,
) -> Tuple[float, List[Ply], bool]:
    if _should_stop(ctx):
        return 0.0, [], True

    ctx.nodes += 1
    if _should_stop(ctx):
        return 0.0, [], True

    term_score = _terminal_score(state, ctx.for_player)
    if term_score is not None:
        return color * term_score, [], False

    if depth == 0:
        eval_score, _ = evaluate(state, ctx.for_player, ctx.eval_weights)
        return color * eval_score, [], False

    key = position_key_from_state(state)
    sym_key = position_key_with_symmetry(state)
    tt_entry = None
    tt_hit_was_symmetric = False
    if ctx.tt is not None:
        tt_entry = ctx.tt.get(key)
        if tt_entry is None and sym_key != key:
            tt_entry = ctx.tt.get(sym_key)
            if tt_entry is not None:
                tt_hit_was_symmetric = True
        if tt_entry is None:
            ctx.tt_misses += 1
        else:
            ctx.tt_hits += 1
    if tt_entry is not None and tt_entry.depth >= depth:
        pv = []
        # Suppress best_ply if the hit came from a symmetric key
        if not tt_entry.score_only and tt_entry.best_ply is not None and not tt_hit_was_symmetric:
            pv = [tt_entry.best_ply]
        if tt_entry.flag == "exact":
            return tt_entry.score, pv, False
        if tt_entry.flag == "lower" and tt_entry.score >= beta:
            return tt_entry.score, pv, False
        if tt_entry.flag == "upper" and tt_entry.score <= alpha:
            return tt_entry.score, pv, False

    # Suppress best_ply for move ordering if the hit came from a symmetric key
    tt_best = None
    if tt_entry and not tt_hit_was_symmetric:
        tt_best = tt_entry.best_ply
    plies = _order_plies(state, legal_plies(state), root_hint or tt_best)
    if not plies:
        eval_score, _ = evaluate(state, ctx.for_player, ctx.eval_weights)
        return color * eval_score, [], False
    best_score = float("-inf")
    best_pv: List[Ply] = []
    alpha_orig = alpha
    for ply in plies:
        nxt = apply_ply(state, ply)
        score, child_pv, stopped = _negamax(nxt, depth - 1, -beta, -alpha, -color, ctx)
        if stopped:
            return best_score, best_pv, True
        score = -score
        if score > best_score:
            best_score = score
            best_pv = [ply] + child_pv
        if score > alpha:
            alpha = score
        if alpha >= beta:
            break

    if not ctx.stopped and ctx.tt is not None:
        flag: Literal["exact", "lower", "upper"]
        if best_score <= alpha_orig:
            flag = "upper"
        elif best_score >= beta:
            flag = "lower"
        else:
            flag = "exact"
        entry = _TTEntry(
            depth=depth,
            score=best_score,
            flag=flag,
            best_ply=best_pv[0] if best_pv else None,
        )
        _store_tt_entry(ctx.tt, key, entry)
        if sym_key != key:
            _store_tt_entry(
                ctx.tt,
                sym_key,
                _TTEntry(
                    depth=depth,
                    score=best_score,
                    flag=flag,
                    best_ply=None,
                    score_only=True,
                ),
            )

    return best_score, best_pv, False


def _terminal_score(state: GameState, for_player: Stone) -> float | None:
    if draw_reason(state) is not None:
        return 0.0
    w = winner(state)
    if w is None:
        return None
    return MATE_SCORE if w == for_player else -MATE_SCORE


def _store_tt_entry(tt: Dict[int, "_TTEntry"], key: int, entry: "_TTEntry") -> None:
    existing = tt.get(key)
    if existing is None or entry.depth >= existing.depth:
        tt[key] = entry


def _order_plies(state: GameState, plies: List[Ply], tt_best: Ply | None) -> List[Ply]:
    # Prefer TT-best, captures, mill-forming moves, then blocks to opponent threats.
    player = state.to_move
    opponent = Stone.BLACK if player == Stone.WHITE else Stone.WHITE
    threats = _open_mill_squares(state.board, opponent)

    def _score(ply: Ply) -> Tuple[int, int, int, int]:
        tt = 1 if tt_best is not None and ply == tt_best else 0
        capture = 1 if ply.remove is not None or ply.kind == "remove" else 0
        formed = 1 if _forms_mill_after_ply(state, ply, player) else 0
        block = 1 if ply.dst is not None and ply.dst in threats else 0
        return (tt, capture, formed, block)

    return sorted(plies, key=_score, reverse=True)


def _forms_mill_after_ply(state: GameState, ply: Ply, player: Stone) -> bool:
    if ply.kind not in ("place", "move", "fly"):
        return False
    if ply.dst is None:
        return False
    board = list(state.board)
    if ply.kind in ("move", "fly"):
        if ply.src is None:
            return False
        board[ply.src] = Stone.EMPTY
    board[ply.dst] = player
    return forms_mill_after_placement(board, player, ply.dst)


def _open_mill_squares(board: Tuple[Stone, ...], player: Stone) -> List[int]:
    squares: set[int] = set()
    for a, b, c in MILLS:
        vals = (board[a], board[b], board[c])
        own = sum(1 for v in vals if v == player)
        empty = [i for i, v in zip((a, b, c), vals) if v == Stone.EMPTY]
        if own == 2 and len(empty) == 1:
            squares.add(empty[0])
    return list(squares)


def _should_stop(ctx: _SearchContext) -> bool:
    if ctx.stopped:
        return True
    if ctx.deadline is not None and time.perf_counter() >= ctx.deadline:
        ctx.stopped = True
        return True
    if ctx.max_nodes is not None and ctx.nodes >= ctx.max_nodes:
        ctx.stopped = True
        return True
    return False


def _is_valid_state(state: object) -> bool:
    return hasattr(state, "to_move") and hasattr(state, "board")


def _best_breakdown(scored_raw: List[Tuple[Ply, float, List[Ply], EvalBreakdown]]) -> EvalBreakdown:
    if not scored_raw:
        return {}
    best = max(scored_raw, key=lambda item: item[1])
    return best[3]


def _diff_breakdowns(best: EvalBreakdown, other: EvalBreakdown) -> EvalBreakdown:
    keys = set(best) | set(other)
    return {key: best.get(key, 0.0) - other.get(key, 0.0) for key in keys}
