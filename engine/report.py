from __future__ import annotations

from dataclasses import dataclass
from typing import List

from core.analysis import (
    blocked_stones,
    compute_threat_squares,
    fork_threat_squares,
    evaluate_light as _evaluate_light,
    mobility_profile,
    mobility_score,
    scored_actions_for_to_move,
    tactic_hints_for_ply as _tactic_hints_for_ply,
)
from core.rules import Action
from core.state import GameState, Stone, opponent
from .types import Limits, Ply
from .analysis_helpers import classify_move_loss


@dataclass(frozen=True)
class PlayerOverlay:
    threats: set[int]
    fork_threats: set[int]
    mobility: int
    blocked: set[int]
    profile: dict[str, float]


@dataclass(frozen=True)
class CandidateMove:
    action: Action
    score: float
    delta: float


@dataclass(frozen=True)
class AnalysisOverlay:
    base_eval_white: float
    base_eval_black: float
    white: PlayerOverlay
    black: PlayerOverlay
    candidates: List[CandidateMove]

@dataclass(frozen=True)
class LastMoveSummary:
    score: float
    loss: float
    label: str
    pv: List[Ply]
    in_top_n: bool


def evaluate_light(state: GameState, player: Stone) -> float:
    return _evaluate_light(state, player)


def tactic_hints_for_ply(state: GameState, ply):
    return _tactic_hints_for_ply(state, ply)


def threat_overlay_targets(state: GameState) -> set[int]:
    return compute_threat_squares(state, opponent(state.to_move))


def build_analysis_overlay(state: GameState, *, max_candidates: int = 5) -> AnalysisOverlay:
    base_eval_white = _evaluate_light(state, Stone.WHITE)
    base_eval_black = _evaluate_light(state, Stone.BLACK)

    white = PlayerOverlay(
        threats=compute_threat_squares(state, Stone.WHITE, use_fallback=False),
        fork_threats=fork_threat_squares(state, Stone.WHITE),
        mobility=mobility_score(state, Stone.WHITE),
        blocked=blocked_stones(state, Stone.WHITE),
        profile=mobility_profile(state, Stone.WHITE),
    )
    black = PlayerOverlay(
        threats=compute_threat_squares(state, Stone.BLACK, use_fallback=False),
        fork_threats=fork_threat_squares(state, Stone.BLACK),
        mobility=mobility_score(state, Stone.BLACK),
        blocked=blocked_stones(state, Stone.BLACK),
        profile=mobility_profile(state, Stone.BLACK),
    )

    candidates: List[CandidateMove] = []
    base_eval = base_eval_white if state.to_move == Stone.WHITE else base_eval_black
    for act, score in scored_actions_for_to_move(state, max_candidates=max_candidates):
        candidates.append(
            CandidateMove(action=act, score=score, delta=score - base_eval)
        )

    return AnalysisOverlay(
        base_eval_white=base_eval_white,
        base_eval_black=base_eval_black,
        white=white,
        black=black,
        candidates=candidates,
    )


def summarize_last_move(
    prev_state: GameState,
    last_ply: Ply,
    *,
    limits: Limits,
    thresholds: dict[str, float],
) -> LastMoveSummary:
    from .search import analyze, score_ply

    result = analyze(prev_state, limits=limits, for_player=prev_state.to_move)
    last_score = None
    last_pv: List[Ply] = []
    in_top_n = False
    for sm in result.top_moves:
        if sm.ply == last_ply:
            last_score = sm.score
            last_pv = sm.pv
            in_top_n = True
            break

    if last_score is None:
        last_score, last_pv = score_ply(
            prev_state,
            last_ply,
            limits=limits,
            for_player=prev_state.to_move,
        )

    loss = max(0.0, result.score - last_score)
    label = classify_move_loss(loss, thresholds)
    return LastMoveSummary(
        score=last_score,
        loss=loss,
        label=label,
        pv=last_pv,
        in_top_n=in_top_n,
    )
