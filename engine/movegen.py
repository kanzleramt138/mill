from __future__ import annotations

from dataclasses import replace
from typing import List

from core.rules import Action, apply_action, forms_mill_after_placement, legal_actions, phase_for, removable_positions
from core.state import GameState, Stone, opponent

from .types import MoveKind, Ply


def legal_plies(state: GameState) -> List[Ply]:
    """Liefert legale Halbzuege mit optionalem Remove als Composite."""
    player = state.to_move

    if state.pending_remove:
        victim = opponent(player)
        removables = removable_positions(state, victim)
        return [Ply(kind="remove", remove=dst) for dst in removables]

    phase = phase_for(state, player)
    base_actions = legal_actions(state)
    plies: List[Ply] = []

    for act in base_actions:
        if act.kind == "place":
            plies.extend(_plies_for_placement(state, player, act.dst))
        elif act.kind == "move":
            move_kind: MoveKind = "fly" if phase == "flying" else "move"
            plies.extend(_plies_for_move(state, player, move_kind, act.src, act.dst))

    return plies


def apply_ply(state: GameState, ply: Ply) -> GameState:
    """
    Wendet ein einzelnes Ply („Zug inkl. optionalem Remove") auf einen GameState an.

    Diese Funktion bildet die zentrale Ply-Anwendungslogik der Engine:
    Sie arbeitet rein auf dem übergebenen `state` und gibt einen neuen `GameState`
    zurück, ohne weitere Engine-Strukturen (History, Suche, UI) zu berühren.

    Sie validiert dabei:
    - Konsistenz von `ply.kind` mit dem aktuellen Zustand (`pending_remove`,
      Phase „flying" vs. `ply.kind == "fly"`).
    - Vollständigkeit der Felder (`src`, `dst`, `remove`) je nach Ply-Typ.
    - Korrektes Entfernen nach geschlossener Mühle mittels
      :func:`removable_positions`.

    Im Fehlerfall wird ein :class:`ValueError` geworfen (z. B. Remove ohne
    geschlossene Mühle oder fehlendes Remove trotz `pending_remove`).

    :param state: aktueller Spielzustand, auf den das Ply angewendet werden soll.
    :param ply:   zu simulierendes Ply (typischerweise aus dem Engine-/Frontend-
                  Kontext), das bereits grob legal sein sollte.
    :return: neuer :class:`GameState` nach Anwendung des Plys.
    """
    player = state.to_move

    if ply.kind == "fly":
        phase = phase_for(state, player)
        if phase != "flying":
            raise ValueError("Fly-Ply ist nur in der Flying-Phase erlaubt")

    if state.pending_remove:
        if ply.kind != "remove" or ply.remove is None:
            raise ValueError("State verlangt Remove; ply.kind muss 'remove' sein")
        return apply_action(state, Action(kind="remove", dst=ply.remove))

    if ply.kind == "remove":
        raise ValueError("Remove-Ply ist nur erlaubt, wenn pending_remove True ist")

    if ply.kind == "place":
        if ply.dst is None:
            raise ValueError("Place-Ply benötigt dst")
        mid = apply_action(state, Action(kind="place", dst=ply.dst))
    else:
        if ply.src is None or ply.dst is None:
            raise ValueError("Move/Fly-Ply benötigt src und dst")
        mid = apply_action(state, Action(kind="move", src=ply.src, dst=ply.dst))

    if mid.pending_remove:
        if ply.remove is None:
            removables = removable_positions(mid, opponent(player))
            if removables:
                raise ValueError("Ply muss Remove enthalten, da eine Mühle geschlossen wurde")
            return replace(mid, pending_remove=False)
        nxt = apply_action(mid, Action(kind="remove", dst=ply.remove))
    else:
        if ply.remove is not None:
            raise ValueError("Remove nur erlaubt, wenn eine Mühle geschlossen wurde")
        nxt = mid

    return nxt


def _plies_for_placement(state: GameState, player: Stone, dst: int | None) -> List[Ply]:
    if dst is None:
        return []

    board = list(state.board)
    board[dst] = player
    formed_mill = forms_mill_after_placement(board, player, dst)

    if not formed_mill:
        return [Ply(kind="place", dst=dst)]

    victim_state = replace(state, board=tuple(board))
    removables = removable_positions(victim_state, opponent(player))
    if not removables:
        return [Ply(kind="place", dst=dst)]
    return [Ply(kind="place", dst=dst, remove=r) for r in removables]


def _plies_for_move(state: GameState, player: Stone, move_kind: MoveKind, src: int | None, dst: int | None) -> List[Ply]:
    if src is None or dst is None:
        return []

    board = list(state.board)
    board[src] = Stone.EMPTY
    board[dst] = player
    formed_mill = forms_mill_after_placement(board, player, dst)

    if not formed_mill:
        return [Ply(kind=move_kind, src=src, dst=dst)]

    victim_state = replace(state, board=tuple(board))
    removables = removable_positions(victim_state, opponent(player))
    if not removables:
        return [Ply(kind=move_kind, src=src, dst=dst)]
    return [Ply(kind=move_kind, src=src, dst=dst, remove=r) for r in removables]
