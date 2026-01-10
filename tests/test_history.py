from core.state import GameState
from core.history import History


def test_history_push_creates_new_snapshot() -> None:
    s0 = GameState.initial()
    h0 = History()

    h1 = h0.push(s0)

    assert h0.past == ()
    assert h1.past == (s0,)
    assert h1.future == ()


def test_undo_returns_previous_state_and_builds_redo_stack() -> None:
    s0 = GameState.initial()
    s1 = GameState.initial()  # in echten Tests könnte man hier leicht variieren

    h = History().push(s0).push(s1)

    res = h.undo(s1)
    assert res is not None
    h_new, prev = res

    assert prev == s0
    assert h_new.past == (s0,)
    assert h_new.future == (s1,)


def test_redo_returns_next_state_and_extends_past() -> None:
    s0 = GameState.initial()
    s1 = GameState.initial()

    # Zustand nach einem Undo: past=[s0], future=[s1]
    h = History(past=(s0,), future=(s1,))

    res = h.redo(s0)
    assert res is not None
    h_new, nxt = res

    assert nxt is s1
    assert h_new.past == (s0, s1)
    assert h_new.future == ()


def test_undo_redo_on_empty_history_returns_none() -> None:
    s0 = GameState.initial()
    h = History()

    assert h.undo(s0) is None
    assert h.redo(s0) is None