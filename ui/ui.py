# mill/ui.py
from __future__ import annotations

import streamlit as st

from core.state import GameState, Stone


# ---------- Session state keys ----------
_SELECTED_SRC_KEY = "selected_src"


def ensure_ui_state() -> None:
    """Initialize UI-related session state keys."""
    if _SELECTED_SRC_KEY not in st.session_state:
        st.session_state[_SELECTED_SRC_KEY] = None


def get_selected_src() -> int | None:
    return st.session_state.get(_SELECTED_SRC_KEY, None)


def set_selected_src(pos: int | None) -> None:
    st.session_state[_SELECTED_SRC_KEY] = pos


def clear_selection() -> None:
    set_selected_src(None)


# ---------- Rendering ----------
def stone_glyph(x: Stone) -> str:
    """Return the glyph used for rendering stones on the board."""
    if x == Stone.EMPTY:
        return " "
    if x == Stone.WHITE:
        return "●"
    return "○"


def cell_label(state: GameState, pos: int) -> str:
    """Return the label that should be rendered inside a cell button."""
    glyph = stone_glyph(state.board[pos])

    # Highlight selected source stone (for move/fly phases)
    if get_selected_src() == pos and not state.pending_remove:
        return f"⟦{glyph}⟧"

    return glyph