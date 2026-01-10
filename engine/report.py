from __future__ import annotations

from dataclasses import dataclass
from typing import List

from mill.analysis import (
    blocked_stones,
    compute_threat_squares,
    evaluate_light as _evaluate_light,
    mobility_profile,
    mobility_score,
    scored_actions_for_to_move,
    tactic_hints_for_ply as _tactic_hints_for_ply,
)
from mill.rules import Action
from mill.state import GameState, Stone, opponent


@dataclass(frozen=True)
class PlayerOverlay:
    threats: set[int]
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
        mobility=mobility_score(state, Stone.WHITE),
        blocked=blocked_stones(state, Stone.WHITE),
        profile=mobility_profile(state, Stone.WHITE),
    )
    black = PlayerOverlay(
        threats=compute_threat_squares(state, Stone.BLACK, use_fallback=False),
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
