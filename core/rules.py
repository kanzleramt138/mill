# core/rules.py
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List, Optional, Sequence, Tuple, Literal

from .graph import MILLS, NEIGHBORS
from .hash import position_key_from_state
from .state import GameState, Stone, opponent, DrawTracker, Phase, resolve_phase


# Public API of this module:
__all__ = [
    "Action",
    "DrawReason",
    "DRAW_NO_MILL_MOVES",
    "DRAW_THREEFOLD_REPETITIONS",
    "phase_for",
    "mills_containing",
    "is_pos_in_mill",
    "advance_draw_tracker",
    "draw_reason",
    "forms_mill_after_placement",
    "is_part_of_mill",
    "removable_positions",
    "legal_actions",
    "apply_action",
    "winner",
    "is_terminal",
]



ActionKind = Literal["place", "move", "remove"]


@dataclass(frozen=True)
class Action:
    kind: ActionKind                 # "place" | "move" | "remove"
    src: Optional[int] = None
    dst: Optional[int] = None

    def __str__(self) -> str:
        if self.kind == "place":
            return f"Place({self.dst})"
        if self.kind == "move":
            return f"Move({self.src}->{self.dst})"
        if self.kind == "remove":
            return f"Remove({self.dst})"
        return f"Action({self.kind})"


DRAW_NO_MILL_MOVES = 20
DRAW_THREEFOLD_REPETITIONS = 3

DrawReason = Literal["no_mill_20", "threefold"]


def phase_for(state: GameState, player: Stone) -> Phase:
    """
    Oeffentliche API.
    Wrapper um resolve_phase(), damit andere Module nicht an private Helper gekoppelt sind.
    """
    return resolve_phase(state, player)


def mills_containing(pos: int) -> List[Tuple[int, int, int]]:
    return [m for m in MILLS if pos in m]


def _stone_eq(board_val: object, player: Stone) -> bool:
    try:
        return int(board_val) == int(player)  # type: ignore
    except (TypeError, ValueError):
        return board_val == player


def is_pos_in_mill(board: Sequence[object], player: Stone, pos: int) -> bool:
    for a, b, c in mills_containing(pos):
        if _stone_eq(board[a], player) and _stone_eq(board[b], player) and _stone_eq(board[c], player):
            return True
    return False

def advance_draw_tracker(
    prev: GameState,
    nxt: GameState,
    *,
    action_kind: Literal["place", "move", "remove"],
    dst: int | None,
) -> GameState:
    """
    Aktualisiert die DrawTracker-Daten *nach* einer bereits angewendeten Aktion.
    - no_mill_moves: zählt nur move/flying-Züge ohne Mühle (place/remove zählt nicht)
    - position_history: deterministisch, seeded mit initialer Position
    """
    mover: Stone = getattr(prev, "to_move")
    prev_phase = phase_for(prev, mover)

    # seed history with initial position if missing
    hist = prev.draw.position_history
    if not hist:
        hist = (position_key_from_state(prev),)

    # did we form a mill on dst?
    formed_mill = False
    if action_kind in ("place", "move") and dst is not None:
        board_next = list(getattr(nxt, "board"))
        formed_mill = is_pos_in_mill(board_next, mover, dst)

    # update "20 moves without mill" counter:
    no_mill = prev.draw.no_mill_moves
    if action_kind == "move" and prev_phase in ("moving", "flying"):
        no_mill = 0 if formed_mill else (no_mill + 1)
    elif formed_mill:
        # if you decide later that placing should also reset: it already does
        no_mill = 0

    new_hist = hist + (position_key_from_state(nxt),)
    return type(nxt)(
        **{**nxt.__dict__, "draw": DrawTracker(no_mill_moves=no_mill, position_history=new_hist)}
    )


def draw_reason(state: GameState) -> Optional[DrawReason]:
    """Returns draw reason if any, else None."""
    # 20 moves without mill
    if state.draw.no_mill_moves >= DRAW_NO_MILL_MOVES:
        return "no_mill_20"

    # threefold repetition
    hist = state.draw.position_history
    if hist:
        cur = hist[-1]
        if hist.count(cur) >= DRAW_THREEFOLD_REPETITIONS:
            return "threefold"

    return None


def forms_mill_after_placement(board: Sequence[Stone], p: Stone, placed_pos: int) -> bool:
    # Check only mills that contain placed_pos
    for a, b, c in mills_containing(placed_pos):
        if board[a] == board[b] == board[c] == p:
            return True
    return False


def is_part_of_mill(board: Sequence[Stone], p: Stone, pos: int) -> bool:
    if board[pos] != p:
        return False
    for a, b, c in mills_containing(pos):
        if board[a] == board[b] == board[c] == p:
            return True
    return False


def removable_positions(state: GameState, victim: Stone) -> List[int]:
    # Standard rule: you may not remove a stone in a mill if there exists any victim stone not in a mill.
    victim_positions = [i for i, x in enumerate(state.board) if x == victim]
    if not victim_positions:
        return []
    non_mill = [i for i in victim_positions if not is_part_of_mill(state.board, victim, i)]
    return non_mill if non_mill else victim_positions


def legal_actions(state: GameState) -> List[Action]:
    p = state.to_move
    if state.pending_remove:
        # must remove opponent stone
        victim = opponent(p)
        return [Action(kind="remove", dst=i) for i in removable_positions(state, victim)]

    phase = phase_for(state, p)

    if phase == "placing":
        # place on any empty
        return [Action(kind="place", dst=i) for i, x in enumerate(state.board) if x == Stone.EMPTY]

    # moving or flying
    own_positions = [i for i, x in enumerate(state.board) if x == p]
    empties = [i for i, x in enumerate(state.board) if x == Stone.EMPTY]

    actions: List[Action] = []
    if phase == "moving":
        for src in own_positions:
            for dst in NEIGHBORS[src]:
                if state.board[dst] == Stone.EMPTY:
                    actions.append(Action(kind="move", src=src, dst=dst))
    else:  # flying
        for src in own_positions:
            for dst in empties:
                actions.append(Action(kind="move", src=src, dst=dst))

    return actions


def apply_action(state: GameState, action: Action) -> GameState:
    p = state.to_move

    # quick legality check (defensive)
    if action not in legal_actions(state):
        raise ValueError(f"Illegal action: {action}")

    board = list(state.board)

    if action.kind == "place":
        assert action.dst is not None
        board[action.dst] = p
        # decrement hand
        new_state = state.with_in_hand(p, state.in_hand(p) - 1)
        # check mill
        if forms_mill_after_placement(board, p, action.dst):
            return GameState(
                board=tuple(board),
                to_move=p,  # same player removes
                in_hand_white=new_state.in_hand_white,
                in_hand_black=new_state.in_hand_black,
                pending_remove=True,
                turn_no=state.turn_no,
            )
        # switch turn
        return GameState(
            board=tuple(board),
            to_move=opponent(p),
            in_hand_white=new_state.in_hand_white,
            in_hand_black=new_state.in_hand_black,
            pending_remove=False,
            turn_no=state.turn_no + 1,
        )

    if action.kind == "move":
        assert action.src is not None and action.dst is not None
        board[action.src] = Stone.EMPTY
        board[action.dst] = p
        # check mill on dst
        if forms_mill_after_placement(board, p, action.dst):
            return GameState(
                board=tuple(board),
                to_move=p,  # same player removes
                in_hand_white=state.in_hand_white,
                in_hand_black=state.in_hand_black,
                pending_remove=True,
                turn_no=state.turn_no,
            )
        return GameState(
            board=tuple(board),
            to_move=opponent(p),
            in_hand_white=state.in_hand_white,
            in_hand_black=state.in_hand_black,
            pending_remove=False,
            turn_no=state.turn_no + 1,
        )

    if action.kind == "remove":
        assert action.dst is not None
        victim = opponent(p)
        if board[action.dst] != victim:
            raise ValueError("Remove must target opponent stone")
        board[action.dst] = Stone.EMPTY
        # end removal step: switch turn
        return GameState(
            board=tuple(board),
            to_move=victim,  # after p removes, victim moves next
            in_hand_white=state.in_hand_white,
            in_hand_black=state.in_hand_black,
            pending_remove=False,
            turn_no=state.turn_no + 1,
        )

    raise ValueError(f"Unknown action kind: {action.kind}")


def _stones_on_board(state: GameState, player: Stone) -> int:
    """Zählt die Steine eines Spielers auf dem Brett (unabhängig von Phase)."""
    return sum(1 for x in state.board if int(x) == int(player))


def winner(state: GameState) -> Optional[Stone]:
    """
    Gewinner gemäß Mühle-Regeln:

    - Ein Spieler verliert, wenn er (in MOVING/FLYING) weniger als 3 Steine auf dem Brett hat.
    - Ein Spieler verliert, wenn er (in MOVING/FLYING) keinen legalen Zug mehr hat
      und kein pending_remove mehr offen ist.

    Gibt den Gewinner oder None zurück.
    """
    # 1) <3 Steine → Gegner gewinnt (nur außerhalb der Placing-Phase sinnvoll)
    for player in (Stone.WHITE, Stone.BLACK):
        phase_p = phase_for(state, player)
        if phase_p in ("moving", "flying"):
            if _stones_on_board(state, player) < 3:
                return opponent(player)

    # 2) keine legalen Züge für side-to-move in moving/flying (kein pending_remove)
    if not state.pending_remove:
        tm = state.to_move
        phase_tm = phase_for(state, tm)
        if phase_tm in ("moving", "flying"):
            if len(legal_actions(state)) == 0:
                return opponent(tm)

    return None


def is_terminal(state: GameState) -> bool:
    """
    Terminal, wenn:
    - ein Sieger feststeht (winner != None), oder
    - eine Remis-Regel greift (draw_reason != None).
    """
    if draw_reason(state) is not None:
        return True
    if winner(state) is not None:
        return True
    return False
