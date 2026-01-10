from __future__ import annotations
from dataclasses import dataclass
from typing import Literal, Optional, TypedDict, List

MoveKind = Literal["place", "move", "fly", "remove"]

@dataclass(frozen=True)
class Ply:
    kind: MoveKind
    src: Optional[int] = None
    dst: Optional[int] = None
    remove: Optional[int] = None  # Composite: optional Remove in gleichem Halbzug

@dataclass(frozen=True)
class Limits:
    time_ms: Optional[int] = None
    max_depth: Optional[int] = None
    max_nodes: Optional[int] = None
    use_tt: Optional[bool] = None
    top_n: Optional[int] = None
    eval_weights: Optional["EvalWeights"] = None

class EvalBreakdown(TypedDict, total=False):
    material: float
    mobility: float
    mills: float
    open_mills: float
    threats_mill_in_1: float
    blocked_opponent: float

@dataclass(frozen=True)
class ThreatReport:
    for_player: set[int]
    opponent: set[int]

@dataclass(frozen=True)
class AnalysisResult:
    best_move: Optional[Ply]
    score: float
    depth: int
    nodes: int
    tt_hits: int
    tt_misses: int
    pv: List[Ply]
    top_moves: List["ScoredMove"]
    breakdown: EvalBreakdown
    threat_report: ThreatReport


@dataclass(frozen=True)
class ScoredMove:
    ply: Ply
    score: float
    pv: List[Ply]
    breakdown: EvalBreakdown
    breakdown_diff: Optional[EvalBreakdown] = None



@dataclass(frozen=True)
class EvalWeights:
    material: float = 10.0
    mills: float = 5.0
    open_mills: float = 2.0
    mobility: float = 1.0
    threats_mill_in_1: float = 2.0
    blocked_opponent: float = 0.5
