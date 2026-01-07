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

class EvalBreakdown(TypedDict, total=False):
    material: float
    mobility: float
    mills: float
    open_mills: float
    threats_mill_in_1: float
    blocked_opponent: float

@dataclass(frozen=True)
class AnalysisResult:
    best_move: Optional[Ply]
    score: float
    depth: int
    nodes: int
    pv: List[Ply]
    breakdown: EvalBreakdown