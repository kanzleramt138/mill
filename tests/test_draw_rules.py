from dataclasses import dataclass
from typing import Tuple, cast

from mill.graph import MILLS
from mill.state import Stone, DrawTracker, GameState
from mill.rules import (
    advance_draw_tracker,
    draw_reason,
    position_key_from_state,
    DRAW_NO_MILL_MOVES,
)


@dataclass(frozen=True)
class FakeState:
    board: Tuple[int, ...]
    to_move: Stone
    pending_remove: bool = False
    draw: DrawTracker = DrawTracker()

    def phase(self, player: Stone) -> str:
        # tests focus on moving-phase counting
        return "moving"


def test_no_mill_counter_increments_on_move_without_mill() -> None:
    # empty-ish board, move doesn't create a mill
    s0 = FakeState(board=tuple([0] * 24), to_move=Stone.WHITE)
    s1 = FakeState(board=tuple([0] * 24), to_move=Stone.BLACK)  # after move, to_move flips

    s1t = advance_draw_tracker(cast(GameState, s0), cast(GameState, s1), action_kind="move", dst=0)
    assert s1t.draw.no_mill_moves == 1


def test_no_mill_counter_resets_when_mill_formed() -> None:
    a, b, c = MILLS[0]
    board0 = [0] * 24
    # after move/place, WHITE completes a mill on dst=c
    board1 = [0] * 24
    board1[a] = int(Stone.WHITE)
    board1[b] = int(Stone.WHITE)
    board1[c] = int(Stone.WHITE)

    s0 = FakeState(board=tuple(board0), to_move=Stone.WHITE, draw=DrawTracker(no_mill_moves=5, position_history=()))
    s1 = FakeState(board=tuple(board1), to_move=Stone.BLACK)

    s1t = advance_draw_tracker(cast(GameState, s0), cast(GameState, s1), action_kind="move", dst=c)
    assert s1t.draw.no_mill_moves == 0


def test_draw_by_20_moves_without_mill() -> None:
    s = FakeState(board=tuple([0] * 24), to_move=Stone.WHITE, draw=DrawTracker(no_mill_moves=DRAW_NO_MILL_MOVES))
    assert draw_reason(cast(GameState, s)) == "no_mill_20"


def test_threefold_repetition_detected() -> None:
    s0 = FakeState(board=tuple([0] * 24), to_move=Stone.WHITE)
    k = position_key_from_state(cast(GameState, s0))
    s = FakeState(board=s0.board, to_move=s0.to_move, draw=DrawTracker(position_history=(k, k, k)))
    assert draw_reason(cast(GameState, s)) == "threefold"