# app.py
from __future__ import annotations

import streamlit as st
import time

from mill.rules import (
    Action,
    apply_action,
    winner,
    is_terminal,
    legal_actions,
    removable_positions,
    advance_draw_tracker,
    draw_reason,
)
from mill.state import GameState, Stone, opponent
from mill.ui import ensure_ui_state, clear_selection
from mill.board_svg import render_board_svg, POS
from mill.board_component import muehle_board
from mill.history import History
from mill.notation import action_to_notation, pos_label
from mill.analysis import (
    compute_threat_squares,
    mobility_score,
    mobility_profile,
    blocked_stones,
    scored_actions_for_to_move,
    evaluate_light,
)
from engine import analyze, AnalysisResult, EvalWeights, Limits
from mill.rules import position_key_from_state


def compute_hints(state: GameState, selected_src: int | None, show_legal_targets: bool) -> tuple[set[int], set[int]]:
    '''
    Returns:
        legal_targets: positions that are legal targets for the selected source (if any)
        removable: positions that can be removed (if any)
    '''
    legal_targets: set[int] = set()
    removable: set[int] = set()

    if state.pending_remove:
        victim = opponent(state.to_move)
        removable = set(removable_positions(state, victim))
        return legal_targets, removable
    
    if show_legal_targets and selected_src is not None:
        phase = state.phase(state.to_move)
        if phase in ("moving", "flying"):
            for act in legal_actions(state):
                if act.kind == "move" and act.src == selected_src and act.dst is not None:
                    legal_targets.add(act.dst)

    return legal_targets, removable


def render_svg_board_interactive(state: GameState) -> None:
    # Toggle: hints on/off
    hints_enabled = st.session_state.get("hints_enabled", False)

    # Spiel bereits beendet? → Board nur noch anzeigen, keine neuen Züge
    game_finished = (
        draw_reason(state) is not None
        or winner(state) is not None
        or is_terminal(state)
    )

    # Threat-Overlay: Drohfelder des Gegners von to_move
    threat_targets: set[int] = set()
    if st.session_state.get("threat_overlay", False) and not game_finished:
        threat_targets = compute_threat_squares(state, opponent(state.to_move))

    # removables list only needed for validation and optional hint rendering
    victim_removables = []
    if state.pending_remove:
        victim = opponent(state.to_move)
        victim_removables = sorted(removable_positions(state, victim))

    svg = render_board_svg(
        state,
        selected_src=None,                  # frontend now
        size=640,
        hint_targets=threat_targets,       # hier: Threat-Overlay (read-only)
        hint_removables=set(),             # toggle (derzeit nicht genutzt)
    )

    hotspots = [{"pos": p, "left": (x/600)*100, "top": (y/600)*100} for p,(x,y) in POS.items()]

    clicked = muehle_board(
        svg=svg,
        hotspots=hotspots,
        board=[int(x) for x in state.board],
        to_move=int(state.to_move),
        phase=state.phase(state.to_move),
        pending_remove=bool(state.pending_remove),
        removables=victim_removables,
        hints_enabled=hints_enabled,
        key="muehle_board",
    )

    # nach Spielende alle Clicks ignorieren
    if clicked is None or game_finished:
        return

    # clicked = {"kind": "place"/"move"/"remove", ... , "nonce": ...}
    kind = clicked.get("kind")
    nonce = int(clicked.get("nonce", -1))

    if "last_nonce" not in st.session_state:
        st.session_state.last_nonce = None
    if nonce == st.session_state.last_nonce:
        return  # already processed this click
    st.session_state.last_nonce = nonce

    if kind == "place":
        dst = clicked.get("dst")
        if dst is None:
            return
        act = Action(kind="place", dst=int(dst))

    elif kind == "move":
        src = clicked.get("src")
        dst = clicked.get("dst")
        if src is None or dst is None:
            return
        act = Action(kind="move", src=int(src), dst=int(dst))

    elif kind == "remove":
        dst = clicked.get("dst")
        if dst is None:
            return
        act = Action(kind="remove", dst=int(dst))
    else:
        return
    
    apply_and_log(act)
    st.rerun()


def player_label(p: Stone) -> str:
    return "WHITE" if p == Stone.WHITE else "BLACK"


def init_session() -> None:
    if "state" not in st.session_state:
        st.session_state.state = GameState.initial()
    if "history" not in st.session_state:
        st.session_state.history = []  # list[str]
    if "state_history" not in st.session_state:
        st.session_state.state_history = History()
    ensure_ui_state()


def push_history(text: str) -> None:
    st.session_state.history.append(text)


def apply_and_log(action: Action) -> None:
    s: GameState = st.session_state.state

    # Sicherheitsnetz: nach Spielende keine neuen Züge anwenden
    if draw_reason(s) is not None or winner(s) is not None or is_terminal(s):
        return

    # 0) Snapshot vor dem Zug für Undo/Redo merken (falls History aktiv ist)
    hist: History | None = getattr(st.session_state, "state_history", None)
    if hist is not None:
        st.session_state.state_history = hist.push(s)

    # 1) Regel-Engine anwenden
    new_s = apply_action(s, action)

    # 2) Draw-Tracker fortschreiben (20 Züge / 3-fach)
    dst = getattr(action, "dst", None)
    new_s = advance_draw_tracker(s, new_s, action_kind=action.kind, dst=dst)  # type: ignore[arg-type]

    # 3) State & History aktualisieren
    st.session_state.state = new_s

    # Move-Log-Eintrag in PGN-ähnlicher Notation
    notation = action_to_notation(action, before=s)
    entry = f"#{s.turn_no} {player_label(s.to_move)}: {notation}"
    push_history(entry)

    if new_s.to_move != s.to_move or not new_s.pending_remove:
        clear_selection()


def current_instructions(s: GameState) -> str:
    if s.pending_remove:
        return f"{player_label(s.to_move)}: Entferne einen gegnerischen Stein."
    phase = s.phase(s.to_move)
    if phase == "placing":
        return f"{player_label(s.to_move)}: Setzphase – klicke ein freies Feld."
    if phase == "moving":
        return f"{player_label(s.to_move)}: Zugphase – wähle Quelle, dann Ziel (Nachbarfeld)."
    return f"{player_label(s.to_move)}: Flugphase – wähle Quelle, dann Ziel (beliebig frei)."


def sidebar_controls() -> None:
    s: GameState = st.session_state.state
    hist: History = getattr(st.session_state, "state_history", History())
    st.session_state.state_history = hist

    undo_col, redo_col = st.sidebar.columns(2)
    if undo_col.button("Undo", use_container_width=True):
        res = hist.undo(s)
        if res is not None:
            new_hist, prev_state = res
            st.session_state.state_history = new_hist
            st.session_state.state = prev_state
            clear_selection()
            st.rerun()

    if redo_col.button("Redo", use_container_width=True):
        res = hist.redo(s)
        if res is not None:
            new_hist, next_state = res
            st.session_state.state_history = new_hist
            st.session_state.state = next_state
            clear_selection()
            st.rerun()

    st.sidebar.header("Kontrollen")

    if st.sidebar.button("Neues Spiel", use_container_width=True):
        st.session_state.state = GameState.initial()
        st.session_state.history = []
        clear_selection()
        st.rerun()

    if st.sidebar.button("Auswahl zurücksetzen", use_container_width=True):
        clear_selection()
        st.rerun()

    if "hints_enabled" not in st.session_state:
        st.session_state.hints_enabled = False

    st.sidebar.toggle("Hinweise anzeigen", key="hints_enabled")

    if "threat_overlay" not in st.session_state:
        st.session_state.threat_overlay = False

    st.sidebar.toggle("Threat-Overlay", key="threat_overlay")

    st.sidebar.subheader("Engine (Search)")
    if "search_depth" not in st.session_state:
        st.session_state.search_depth = 2
    if "search_time_ms" not in st.session_state:
        st.session_state.search_time_ms = 0
    if "search_top_n" not in st.session_state:
        st.session_state.search_top_n = 5
    if "search_use_tt" not in st.session_state:
        st.session_state.search_use_tt = True
    if "search_cache_ttl" not in st.session_state:
        st.session_state.search_cache_ttl = 2
    if "search_cache_size" not in st.session_state:
        st.session_state.search_cache_size = 8

    st.sidebar.number_input("Depth", min_value=1, max_value=8, key="search_depth")
    st.sidebar.number_input("Time (ms, 0=off)", min_value=0, max_value=5000, step=50, key="search_time_ms")
    st.sidebar.number_input("Top-N", min_value=1, max_value=10, key="search_top_n")
    st.sidebar.toggle("Use TT", key="search_use_tt")
    st.sidebar.number_input("Cache TTL (s, 0=off)", min_value=0, max_value=30, key="search_cache_ttl")
    st.sidebar.number_input("Cache Size", min_value=1, max_value=32, key="search_cache_size")

    st.sidebar.subheader("Eval Weights")
    if "w_material" not in st.session_state:
        st.session_state.w_material = 10.0
    if "w_mills" not in st.session_state:
        st.session_state.w_mills = 5.0
    if "w_open_mills" not in st.session_state:
        st.session_state.w_open_mills = 2.0
    if "w_mobility" not in st.session_state:
        st.session_state.w_mobility = 1.0
    if "w_threats_mill_in_1" not in st.session_state:
        st.session_state.w_threats_mill_in_1 = 2.0
    if "w_blocked_opponent" not in st.session_state:
        st.session_state.w_blocked_opponent = 0.5

    st.sidebar.number_input("Material", min_value=0.0, max_value=20.0, step=0.5, key="w_material")
    st.sidebar.number_input("Mills", min_value=0.0, max_value=20.0, step=0.5, key="w_mills")
    st.sidebar.number_input("Open Mills", min_value=0.0, max_value=20.0, step=0.5, key="w_open_mills")
    st.sidebar.number_input("Mobility", min_value=0.0, max_value=10.0, step=0.5, key="w_mobility")
    st.sidebar.number_input("Threats (Mill-in-1)", min_value=0.0, max_value=10.0, step=0.5, key="w_threats_mill_in_1")
    st.sidebar.number_input("Blocked Opponent", min_value=0.0, max_value=10.0, step=0.5, key="w_blocked_opponent")


def _format_positions(positions: set[int]) -> str:
    if not positions:
        return "-"
    return ", ".join(sorted(pos_label(p) for p in positions))


def _format_ply(ply) -> str:
    if ply.kind == "place" and ply.dst is not None:
        base = f"Place {pos_label(ply.dst)}"
    elif ply.kind in ("move", "fly") and ply.src is not None and ply.dst is not None:
        base = f"{ply.kind.title()} {pos_label(ply.src)}->{pos_label(ply.dst)}"
    elif ply.kind == "remove" and ply.remove is not None:
        base = f"Remove {pos_label(ply.remove)}"
    else:
        base = f"{ply.kind}"

    if ply.remove is not None and ply.kind in ("place", "move", "fly"):
        return f"{base} | remove {pos_label(ply.remove)}"
    return base


def _format_pv(pv, *, per_line: int = 4) -> str:
    if not pv:
        return "-"
    chunks = []
    for i in range(0, len(pv), per_line):
        chunk = " ; ".join(_format_ply(p) for p in pv[i : i + per_line])
        chunks.append(chunk)
    return "\n".join(chunks)


def render_analysis_panel(state: GameState) -> None:
    """Seitliches Analyse-Panel (read-only)."""
    import streamlit as st  # lokal halten

    with st.expander("Analyse (aktuelle Stellung)", expanded=False):
        game_finished = (
            draw_reason(state) is not None
            or winner(state) is not None
            or is_terminal(state)
        )

        base_eval_white = evaluate_light(state, Stone.WHITE)
        base_eval_black = evaluate_light(state, Stone.BLACK)

        for player in (Stone.WHITE, Stone.BLACK):
            threats = compute_threat_squares(state, player)
            mobility = mobility_score(state, player)
            blocked = blocked_stones(state, player)
            profile = mobility_profile(state, player)

            st.markdown(f"**{player_label(player)}**")
            st.write(f"Threat-Squares: {_format_positions(threats)}")
            st.write(
                f"Mobility: Score = {mobility:.0f}, "
                f"Steine beweglich = {int(profile['movable_count'])}/{int(profile['total_stones'])}, "
                f"ø-Mobilität={profile['avg_mobility']:.2f}"
            )
            st.write(
                f"Blockierte Steine: {_format_positions(blocked)} "
                f"({profile['blocked_ratio']*100:.1f}% blockiert)"
            )

            # einfache Zug-Vorschau nur für side-to-move
            if player == state.to_move:
                st.write("Kandidatenzüge (Heuristik):")
                base_eval = base_eval_white if player == Stone.WHITE else base_eval_black
                for act, score in scored_actions_for_to_move(state, max_candidates=5):
                    nota = action_to_notation(act, before=state)
                    delta = score - base_eval
                    st.write(f"  {nota}: {score:.2f} (Δ {delta:+.2f})")

            st.markdown("---")

        if not game_finished:
            st.markdown("**Engine (Search)**")
            depth = int(st.session_state.get("search_depth", 2))
            time_ms = int(st.session_state.get("search_time_ms", 0)) or None
            top_n = int(st.session_state.get("search_top_n", 5))
            use_tt = bool(st.session_state.get("search_use_tt", True))
            cache_ttl = int(st.session_state.get("search_cache_ttl", 2))
            cache_size = int(st.session_state.get("search_cache_size", 8))
            weights = EvalWeights(
                material=float(st.session_state.get("w_material", 10.0)),
                mills=float(st.session_state.get("w_mills", 5.0)),
                open_mills=float(st.session_state.get("w_open_mills", 2.0)),
                mobility=float(st.session_state.get("w_mobility", 1.0)),
                threats_mill_in_1=float(st.session_state.get("w_threats_mill_in_1", 2.0)),
                blocked_opponent=float(st.session_state.get("w_blocked_opponent", 0.5)),
            )
            cache_key = (
                position_key_from_state(state),
                depth,
                time_ms,
                top_n,
                use_tt,
                (
                    weights.material,
                    weights.mills,
                    weights.open_mills,
                    weights.mobility,
                    weights.threats_mill_in_1,
                    weights.blocked_opponent,
                ),
                int(state.to_move),
            )
            result: AnalysisResult | None = None
            if "analysis_cache" not in st.session_state:
                st.session_state.analysis_cache = {}
            if "analysis_cache_order" not in st.session_state:
                st.session_state.analysis_cache_order = []

            cache = st.session_state.analysis_cache
            order = st.session_state.analysis_cache_order
            if cache_key in cache:
                cached_result, cached_ts = cache[cache_key]
                if isinstance(cached_result, AnalysisResult):
                    if cache_ttl == 0 or (time.time() - cached_ts) <= cache_ttl:
                        result = cached_result
                        if cache_key in order:
                            order.remove(cache_key)
                        order.append(cache_key)
            if result is None:
                result = analyze(
                    state,
                    limits=Limits(
                        max_depth=depth,
                        time_ms=time_ms,
                        top_n=top_n,
                        use_tt=use_tt,
                        eval_weights=weights,
                    ),
                    for_player=state.to_move,
                )
                cache[cache_key] = (result, time.time())
                if cache_key in order:
                    order.remove(cache_key)
                order.append(cache_key)
                while len(order) > cache_size:
                    old_key = order.pop(0)
                    cache.pop(old_key, None)
            st.write(
                f"Depth={result.depth}, Nodes={result.nodes}, "
                f"TT hits/misses={result.tt_hits}/{result.tt_misses}"
            )
            if result.best_move is not None:
                st.write(f"Best move: {_format_ply(result.best_move)} (score {result.score:.2f})")
            if result.pv:
                st.write("PV:")
                st.code(_format_pv(result.pv), language="text")
            if result.breakdown:
                st.write("Eval breakdown:")
                for k, v in result.breakdown.items():
                    st.write(f"  {k}: {v:.2f}")
            if result.top_moves:
                st.write("Top moves:")
                for sm in result.top_moves:
                    st.write(f"{_format_ply(sm.ply)}: {sm.score:.2f}")
                    if sm.pv:
                        st.code(_format_pv(sm.pv), language="text")


def main() -> None:
    st.set_page_config(page_title="Mühle Trainer (Grundgerüst)", layout="wide")
    init_session()
    sidebar_controls()

    s: GameState = st.session_state.state

    st.title("Mühle (Nine Men's Morris) – UI-first Grundgerüst")

    colA, colB = st.columns([2, 1], gap="large")

    with colA:
        st.subheader("Brett")
        st.info(current_instructions(s))
        render_svg_board_interactive(s)
    with colB:
        st.subheader("Status")
        st.write(f"Turn: **{s.turn_no}**")
        st.write(f"To move: **{player_label(s.to_move)}**")
        st.write(f"Pending remove: **{s.pending_remove}**")

        st.markdown("---")
        st.write("**Stones in hand**")
        st.write(f"WHITE: {s.in_hand_white} | BLACK: {s.in_hand_black}")

        st.write("**Stones on board**")
        st.write(f"WHITE: {s.stones_on_board(Stone.WHITE)} | BLACK: {s.stones_on_board(Stone.BLACK)}")

        st.write("**Phasen**")
        st.write(f"WHITE: {s.phase(Stone.WHITE)}")
        st.write(f"BLACK: {s.phase(Stone.BLACK)}")

        # Ergebnis-Status
        dreason = draw_reason(s)
        if dreason is not None:
            if dreason == "no_mill_20":
                st.info("Spiel beendet: Remis nach 20 Zügen ohne Mühle.")
            elif dreason == "threefold":
                st.info("Spiel beendet: Remis durch dreifache Stellungswiederholung.")
        else:
            w = winner(s)
            if w is not None:
                st.success(f"Spiel beendet. Gewinner: {player_label(w)}")
            elif is_terminal(s):
                st.warning("Spiel beendet (terminal), aber Gewinner nicht eindeutig (Regelvariante/Edge Case).")

        # Leichte Evaluierung ähnlich Schach-Score
        eval_white = evaluate_light(s, Stone.WHITE)
        eval_black = evaluate_light(s, Stone.BLACK)
        eval_diff = eval_white - eval_black # positiv = Vorteil WHITE, negativ = Vorteil BLACK
        st.markdown("---")
        st.subheader("Historie")
        if st.session_state.history:
            st.code("\n".join(st.session_state.history[-30:]))
        else:
            st.write("Noch keine Züge.")

        st.caption("Hinweis: Dieses Grundgerüst ist bewusst minimal. Analyse/Training bauen wir darauf auf.")

        # Analyse-Panel (Threats, Mobility, blockierte Steine)
        render_analysis_panel(s)


if __name__ == "__main__":
    main()
