# GitHub Copilot – Repo Instructions (Mühle)

## Kontext
Dieses Repo implementiert „Mühle“ (Nine Men's Morris) als Streamlit-App mit einem Custom Component Board.

**Sprache:** Bitte Antworten standardmäßig auf Deutsch. (Englisch nur, wenn ausdrücklich gewünscht oder für kurze Fachbegriffe/Bezeichner nötig.)

**Produktziel:** Trainings- und Analyse-Tool (ähnlich „chess.com“-Denke), nicht nur ein Spiel.  
**Oberziel:** robust, deterministisch, testbar; KI-bereit (später), aber zunächst ohne KI-Suche.

## Architektur (Quelle der Wahrheit)
### Frontend (Custom Component `muehle_board`)
- rendert SVG-Board + Hotspots
- verwaltet **lokale Selection** (z. B. `selected_src`) nur für Interaktion
- berechnet **legal targets** ausschließlich für **Hints/Overlays** (visuell)
- sendet fertige Aktionen: `place`, `move`, `remove`
- **kein Double-Click-Flow**, keine Backend-Selections

### Backend (Domain/Engine)
- hält den `GameState`
- validiert Regeln und verhindert illegale States (auch wenn Frontend fehlerhaft ist)
- wendet fertige Aktionen deterministisch an

## Dateien & Verantwortlichkeiten
- `mill/state.py`: Domänenmodell (`GameState`, `Stone`, helpers). Kein Streamlit.
- `mill/graph.py`: Konstanten (`NEIGHBORS`, `MILLS`, Positionen).
- `mill/rules.py`: Regel-Engine (Legal moves, mills, remove, end conditions). Bevorzugt pure functions.
- `mill/board_svg.py`: SVG Rendering (keine Regel-Logik erzwingen).
- `mill/board_component.py`: Component bridge + Event-Typing.
- `muehle_board_component/`: Frontend (static). Keine ESM `import/export` verwenden, außer es gibt ein Build (`dist/`/`build/`).
- `app.py`: Streamlit-Orchestrator (Wiring, Session-State, Event→Action, rerun).

## Regelanforderungen (Domain)
- Phasen: `PLACING`, `MOVING`, `FLYING`
  - `PLACING → MOVING`, wenn Spieler keine Steine mehr „in Hand“ hat
  - `MOVING → FLYING`, wenn Spieler nur noch 3 Steine besitzt
- Constraints:
  - max. 9 Steine pro Spieler
  - keine illegalen States zulassen (Backend validiert)
- Mühlenlogik:
  - Mühle erkennen nach place und move
  - Entfernen:
    - nur Steine außerhalb von Mühlen
    - Ausnahme: sind alle gegnerischen Steine in Mühlen, darf jeder entfernt werden
    - pro „Mühle schließen“-Aktion maximal 1 Remove (keine Mehrfach-Entfernung)
- Spielende:
  - Spieler hat < 3 Steine oder keinen legalen Zug mehr

## Coding Guidelines
- Regel-Logik als pure functions: `apply_action(state, action) -> new_state`.
- Keine Streamlit-Abhängigkeit in `mill/rules.py`, `mill/state.py`, `mill/graph.py`.
- `GameState` snapshot-fähig, immutability bevorzugt.
- Move-History/Undo/Redo:
  - jede Aktion erzeugt einen neuen Snapshot
  - kein Mutieren alter States
  - optional: PGN-ähnliche Notation (`P:a7`, `M:a7-d7`, `R:b4`)
- Typed Events: `ActionEvent` als discriminated union nach `kind`:
  - `place`: `dst`, `nonce`
  - `move`: `src`, `dst`, `nonce`
  - `remove`: `dst`, `nonce`
- Defensive Guards im UI: Event-Keys prüfen, `nonce` gegen Doppel-Events.
- Tests mit `pytest` für Regel-Engine (mills, removables, legal moves, transitions).

## Analyse-/Training-Features (read-only)
Overlays sollen **keinen** GameState ändern, nur visualisieren:
- legal targets (bereits)
- removables (bereits)
- threat overlay (direkte Drohfelder: Gegner kann dort im nächsten Zug eine Mühle schließen)
- mobility overlay (Anzahl legaler Züge pro Stein)
- mill participation (potenzielle Mühlen pro Stein)
Alle Overlays togglebar.

## Component/Frontend Guidelines
- `index.html` muss:
  - `Streamlit.setComponentReady()` genau einmal nach Event-Listener-Setup aufrufen
  - auf `streamlit:render` reagieren und `args.svg` sichtbar rendern
  - `Streamlit.setComponentValue({...})` für Events verwenden
- Asset-Pfade relativ halten (./file.js).
- Cache-Busting während Dev zulässig (`?v=...`).

## “Skills” / typische Aufgaben
- Neue Regeln implementieren + Unit Tests hinzufügen
- Typing-Probleme (Pyright) beheben, ohne Runtime-Verhalten zu ändern
- SVG Rendering erweitern (Highlights/Hints)
- Component Events debuggen (Render args, frame height, nonce)
- Vorbereitung KI: `evaluate(state, player) -> score` (ohne Suche)

## Do / Don’t
- DO: kleine, nachvollziehbare Änderungen; Tests mitliefern.
- DO: Code klar trennen (rules vs UI).
- DON’T: Logik in `board_svg.py` duplizieren, die in `rules.py` gehört.
- DON’T: Frontend ESM verwenden, solange kein Build-Output (`dist/`/`build/`) existiert.

---

## Session-Protokoll (für effizientes Arbeiten mit Copilot)
Diese Regeln gelten, wenn der User explizit **„session start“** oder **„session end“** sagt.

### Trigger: „session start: <titel>“
- Lies [docs/SESSION_LATEST.md](../docs/SESSION_LATEST.md) und die verlinkte letzte Note.
- Erzeuge eine neue Session Note unter `docs/sessions/` auf Basis von [docs/SESSION_TEMPLATE.md](../docs/SESSION_TEMPLATE.md).
- Fülle Abschnitt „0) Kontext“ mit einem kompakten Stand (Quelle: letzte Note).
- Übernimm die dortigen „Nächste Schritte“ als ToDo-Liste/Plan für diese Session.

### Trigger: „session end“
- Aktualisiere die aktuelle Session Note so, dass ein neues Kontextfenster genügt:
  - „Kontext“ + „Nächste Schritte“ sind Pflicht.
  - Wichtige Semantik-Entscheidungen/Edge-Cases knapp festhalten.
- Optional Tests laufen lassen, falls der User das wünscht.
- Doc-Sync nur bei Bedarf (PROJECT_OVERVIEW / DEV_NOTES / copilot-instructions).
- Update [docs/SESSION_LATEST.md](../docs/SESSION_LATEST.md) auf die aktuelle Note.