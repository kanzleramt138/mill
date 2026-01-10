# core/hash.py
from __future__ import annotations

import hashlib
from typing import List, Sequence, cast

from .graph import SYMMETRY_MAPS
from .state import GameState, Phase, Stone, resolve_phase

__all__ = [
    "position_key_from_state",
    "position_key_with_symmetry",
]

BoardVal = int | Stone


def position_key_from_state(state: GameState) -> int:
    """
    Deterministischer Key fuer Wiederholungen.
    Bezieht ein: board, to_move, phase(to_move), pending_remove.
    """
    board_seq = _board_seq_from_state(state)
    to_move = cast(Stone, getattr(state, "to_move"))
    pending_remove = bool(getattr(state, "pending_remove", False))
    phase = resolve_phase(state, to_move)

    return _position_key_from_board(board_seq, to_move, phase, pending_remove)


def position_key_with_symmetry(state: GameState) -> int:
    """
    Deterministischer Key, kanonisiert ueber alle 8 Symmetrien.
    """
    board_seq = _board_seq_from_state(state)
    to_move = cast(Stone, getattr(state, "to_move"))
    pending_remove = bool(getattr(state, "pending_remove", False))
    phase = resolve_phase(state, to_move)

    best_key = _position_key_from_board(board_seq, to_move, phase, pending_remove)
    for mapping in SYMMETRY_MAPS:
        sym_board = _apply_symmetry(board_seq, mapping)
        sym_key = _position_key_from_board(sym_board, to_move, phase, pending_remove)
        if sym_key < best_key:
            best_key = sym_key
    return best_key


def _position_key_from_board(
    board_seq: Sequence[BoardVal],
    to_move: Stone,
    phase: Phase,
    pending_remove: bool,
) -> int:
    payload = "|".join(
        [
            f"tm={int(to_move)}",
            f"ph={phase}",
            f"pr={1 if pending_remove else 0}",
            "bd=" + ",".join(str(int(x)) for x in board_seq),
        ]
    ).encode("utf-8")

    return int.from_bytes(hashlib.blake2b(payload, digest_size=8).digest(), "big")


def _apply_symmetry(board_seq: Sequence[BoardVal], mapping: Sequence[int]) -> List[BoardVal]:
    sym_board: List[BoardVal] = [0] * len(board_seq)
    for idx, mapped in enumerate(mapping):
        sym_board[mapped] = board_seq[idx]
    return sym_board


def _board_seq_from_state(state: GameState) -> List[BoardVal]:
    return list(cast(Sequence[BoardVal], getattr(state, "board")))
