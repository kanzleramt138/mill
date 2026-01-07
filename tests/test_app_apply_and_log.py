from types import SimpleNamespace

import app
from mill.rules import Action
from mill.state import GameState


def _make_session(state: GameState) -> SimpleNamespace:
    """Hilfsfunktion: fake session_state für Tests."""
    return SimpleNamespace(state=state, history=[])


def test_apply_and_log_ignores_when_game_finished(monkeypatch) -> None:
    """Wenn Spiel beendet ist, darf apply_and_log nichts mehr ändern."""
    s0 = GameState.initial()
    session = _make_session(s0)

    # fake session_state
    monkeypatch.setattr(app, "st", SimpleNamespace(session_state=session))

    # Spiel ist bereits remis – Guard soll greifen
    monkeypatch.setattr(app, "draw_reason", lambda _s: "no_mill_20")
    monkeypatch.setattr(app, "winner", lambda _s: None)
    monkeypatch.setattr(app, "is_terminal", lambda _s: False)

    # apply_action / advance_draw_tracker dürfen NICHT aufgerufen werden
    def _should_not_be_called(*_args, **_kwargs):
        raise AssertionError("apply_action/advance_draw_tracker should not be called when game is finished")

    monkeypatch.setattr(app, "apply_action", _should_not_be_called)
    monkeypatch.setattr(app, "advance_draw_tracker", _should_not_be_called)
    monkeypatch.setattr(app, "clear_selection", lambda: None)

    act = Action(kind="place", dst=5)

    app.apply_and_log(act)

    # state & history bleiben unverändert
    assert session.state is s0
    assert session.history == []


def test_apply_and_log_updates_state_and_history_normally(monkeypatch) -> None:
    """Im Normalfall soll apply_and_log State, DrawTracker und History aktualisieren."""
    s0 = GameState.initial()
    s1 = GameState.initial()  # Dummy "neuer" State
    session = _make_session(s0)

    monkeypatch.setattr(app, "st", SimpleNamespace(session_state=session))

    # Spiel läuft noch
    monkeypatch.setattr(app, "draw_reason", lambda _s: None)
    monkeypatch.setattr(app, "winner", lambda _s: None)
    monkeypatch.setattr(app, "is_terminal", lambda _s: False)

    called: dict[str, object] = {}

    def fake_apply_action(state: GameState, action: Action) -> GameState:
        called["apply_action"] = action
        assert state is s0
        return s1

    def fake_advance(prev: GameState, nxt: GameState, **kwargs) -> GameState:
        called["advance_draw_tracker"] = kwargs
        assert prev is s0
        assert nxt is s1
        return nxt

    def fake_clear_selection() -> None:
        called["clear_selection"] = True

    monkeypatch.setattr(app, "apply_action", fake_apply_action)
    monkeypatch.setattr(app, "advance_draw_tracker", fake_advance)
    monkeypatch.setattr(app, "clear_selection", fake_clear_selection)

    act = Action(kind="place", dst=3)
    app.apply_and_log(act)

    # neuer State wurde übernommen
    assert session.state is s1
    # History-Eintrag wurde angelegt
    assert session.history, "history should not be empty after a move"
    # Hilfsfunktionen wurden aufgerufen
    assert "apply_action" in called
    assert "advance_draw_tracker" in called
    assert "clear_selection" in called