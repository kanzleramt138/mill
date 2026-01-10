# Mühle (Nine Men's Morris) – Projektüberblick

## Ziel
Eine Streamlit-App für „Mühle“ mit:
- sauberer Spielzustands- und Regel-Engine (Backend)
- SVG-Rendering (Backend)
- interaktivem Board via Streamlit Custom Component (Frontend)
- stabiler Event-/Action-Pipeline (UI → Action → State Transition → UI)

---

## Repository-Struktur (Ist-Zustand)

### `app.py`
**Rolle:** Streamlit-Orchestrator.
- initialisiert UI/Session-State
- rendert Board-SVG über `ui/board_svg.py`
- ruft Custom Component `muehle_board(...)` auf
- übersetzt Click-Events in `Action` und wendet sie an (`apply_and_log(...)`), dann `st.rerun()`

### `core/state.py`
**Rolle:** Domänenmodell.
- `Stone` (EMPTY/WHITE/BLACK)
- `GameState` (immutable dataclass, z. B. Board, `to_move`, `pending_remove`, etc.)
- Hilfsfunktionen wie `opponent(...)`

**Leitlinie:** Keine UI- oder Frontend-Abhängigkeiten. Kein Streamlit.

### `core/graph.py`
**Rolle:** Spielfeld-Konstanten / Topologie.
- Positionen 0..23
- `NEIGHBORS` (Adjazenzen)
- `MILLS` (Dreier-Linien)

**Leitlinie:** Rein statisch, deterministisch.

### `core/rules.py`
**Rolle:** Regel-Engine.
- Mill-Erkennung (nach `place` und `move`)
- Legal Actions für `PLACING`, `MOVING`, `FLYING`
- Remove-Regeln inkl. Ausnahme (wenn alle gegnerischen Steine in Mills)
- Endbedingungen (Gewinn: <3 Steine oder keine legalen Züge, Draw: Tracking separat)

**Leitlinie:** Pure Functions bevorzugen:
`apply_action(state, action) -> new_state`

### `core/history.py`
**Rolle:** Undo/Redo-History (immutable).
- `History(past, future)` als Snapshot-Stacks
- `push(current)` legt Snapshot ab und leert Redo
- `undo/redo` liefern jeweils `(new_history, state)` oder `None`

### `core/notation.py`
**Rolle:** Notation/Logging.
- `pos_label(pos) -> "a1" .. "g7"`
- `action_to_notation(action, before) -> "P:a7" | "M:a7-d7" | "R:b4"`

### `core/analysis.py`
**Rolle:** Read-only Analyse/Heuristik/Planung (kein State-Mutieren).
- Threat-Squares & Pre-Threat-Squares
- Mobility (pro Stein, blockierte Steine, Profile)
- Light-Evaluation (`evaluate_light`)
- Kandidatenzüge (`scored_actions_for_to_move`)

### `engine/report.py`
**Rolle:** Engine-Fassade fuer read-only Analyse/Overlays.
- aggregiert Threats/Mobility/Blocked/Kandidaten fuer die UI
- kapselt `core/analysis.py` fuer saubere UI-Engine-Grenze


### `ui/board_svg.py`
**Rolle:** Rendering (SVG).
- zeichnet Board + Steine
- optional: Highlights/Hints (Targets/Removables)
- liefert `svg: str`

**Leitlinie:** Kein Regelwissen erzwingen; nur „darstellen“.

### `ui/ui.py`
**Rolle:** Streamlit UI Helper (WIP).
- Session-State Keys (z. B. selected source)
- UI-Hilfsfunktionen (Label/Glyphs)

### `ui/board_component.py`
**Rolle:** Python-Bridge zum Custom Component.
- `declare_component` auf `muehle_board_component/`
- Typing für Events (`ActionEvent`) – ideal als „discriminated union“

### `ui/`
**Rolle:** UI-Fassade (Re-Exports fuer Board/History/Notation/UI-Helper).

### `muehle_board_component/`
**Rolle:** Frontend-Assets des Streamlit Components (aktuell „static“).
- `index.html` (rendert SVG + Hotspots, sendet Events zurück)
- `streamlit-component-lib.js` (shim/API)
- optional (später): bundling via Vite/webpack → `dist/`/`build/`

---

## Datenfluss (UI → Engine)
1. Backend erzeugt `svg` + `hotspots` + State-Args → `muehle_board(...)`
2. Frontend rendert, Nutzer klickt → Event `{kind, src?, dst?, nonce}`
3. `app.py` validiert / guardet (u. a. Terminal/Draw/Nonce), baut `Action`
4. Backend `apply_action`/`apply_and_log` → neuer `GameState` (+ Draw-Tracking) + History-Snapshot + Log-Notation
5. `st.rerun()` → neues Render

---

## Qualitätsziele / Prinzipien
- Regeln sind testbar (pytest), deterministisch, ohne Streamlit.
- Rendering ist getrennt von Regeln.
- Component-Events sind typ-sicher und robust (nonce gegen Doppelclicks).
- Minimaler State im Frontend (nur Interaktionszustand wie selected src), GameState bleibt Backend-Quelle der Wahrheit.
- Analyse-/Overlays sind read-only (ändern nie den GameState).

---

## Nächste Schritte (Empfehlung)
1. Analyse-/Overlay-Feinschliff (z. B. Mobility/Blocked-Overlay im Board)
2. Kleine Suche skizzieren: „forced mills“ (ohne KI-Suche als Engine-Feature)
3. `ActionEvent` Typing/Guards weiter härten (Event-Keys + Nonce)
4. Optional: Frontend-Build (dist/build) statt „static“, falls ESM/Bundling nötig wird