from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple, Optional

from .state import GameState


@dataclass(frozen=True)
class History:
    """Immutable Undo/Redo-Stack für GameStates."""
    past: Tuple[GameState, ...] = ()
    future: Tuple[GameState, ...] = ()

    def push(self, current: GameState) -> "History":
        """Aktuellen State auf den Undo-Stack legen, Redo-Stack leeren."""
        return History(past=self.past + (current,), future=())

    def undo(self, current: GameState) -> Optional[tuple["History", GameState]]:
        """Einen Schritt zurück; liefert neuen History-Status + vorherigen State."""
        if not self.past:
            return None
        prev = self.past[-1]
        new_hist = History(past=self.past[:-1], future=(current,) + self.future)
        return new_hist, prev

    def redo(self, current: GameState) -> Optional[tuple["History", GameState]]:
        """Einen Schritt vor; liefert neuen History-Status + nächsten State."""
        if not self.future:
            return None
        nxt = self.future[0]
        new_hist = History(past=self.past + (current,), future=self.future[1:])
        return new_hist, nxt