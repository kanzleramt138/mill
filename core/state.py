# core/state.py
from __future__ import annotations

from dataclasses import dataclass, replace
from enum import IntEnum
from typing import Callable, Literal, Tuple, cast


__all__ = [
    "Stone",
    "Phase",
    "opponent",
    "resolve_phase",
    "DrawTracker",
    "GameState",
]

class Stone(IntEnum):
    EMPTY = 0
    WHITE = 1
    BLACK = 2

# Type alias: phases are strictly typesafe
Phase = Literal["placing", "moving", "flying"]
PHASE_STRS: Tuple[str, str, str] = ("placing", "moving", "flying")


def _as_phase(val: str) -> Phase:
    if val in PHASE_STRS:
        return cast(Phase, val)
    raise ValueError(f"Unknown phase string: {val!r}")


def resolve_phase(state: "GameState", player: Stone) -> Phase:
    """Best effort: supports both method-based and attribute-based phase."""
    phase_attr: Callable[[Stone], Phase] | Phase | str | None = getattr(state, "phase", None)

    if callable(phase_attr):
        return phase_attr(player)

    if isinstance(phase_attr, str):
        return _as_phase(phase_attr)

    phase_str = getattr(state, "phase_str", None)
    if isinstance(phase_str, str):
        return _as_phase(phase_str)

    raise TypeError("GameState must provide phase information via method or attribute.")


def opponent(p: Stone) -> Stone:
    if p == Stone.WHITE:
        return Stone.BLACK
    if p == Stone.BLACK:
        return Stone.WHITE
    raise ValueError("EMPTY has no opponent")


@dataclass(frozen=True)
class DrawTracker:
    """UI-unabhängige Draw-Regeln (immutable, snapshot-fähig)."""
    no_mill_moves: int = 0
    position_history: Tuple[int, ...] = ()


@dataclass(frozen=True)
class GameState:
    board: Tuple[Stone, ...]            # length 24
    to_move: Stone                      # WHITE/BLACK
    in_hand_white: int                  # stones left to place
    in_hand_black: int
    pending_remove: bool                # after forming a mill
    turn_no: int                        # increments when a full turn completes

    # Draw bookkeeping (added at end to minimize constructor breakage):
    draw: DrawTracker = DrawTracker()

    @staticmethod
    def initial() -> "GameState":
        return GameState(
            board=tuple([Stone.EMPTY] * 24),
            to_move=Stone.WHITE,
            in_hand_white=9,
            in_hand_black=9,
            pending_remove=False,
            turn_no=1,
        )

    def in_hand(self, p: Stone) -> int:
        return self.in_hand_white if p == Stone.WHITE else self.in_hand_black

    def with_in_hand(self, p: Stone, value: int) -> "GameState":
        if p == Stone.WHITE:
            return replace(self, in_hand_white=value)
        return replace(self, in_hand_black=value)

    def stones_on_board(self, p: Stone) -> int:
        return sum(1 for x in self.board if x == p)

    def phase(self, p: Stone) -> Phase:
        # Classic:
        # - placing while in_hand > 0
        # - moving when in_hand == 0 and stones_on_board > 3
        # - flying when stones_on_board == 3
        if self.in_hand(p) > 0:
            return "placing"
        count = self.stones_on_board(p)
        if count <= 3:
            return "flying"
        return "moving"

    def is_empty(self, pos: int) -> bool:
        return self.board[pos] == Stone.EMPTY
