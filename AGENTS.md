# GitHub Copilot ƒ?" Repo Instructions (MÇ¬hle)

## Kontext
Dieses Repo implementiert ƒ?zMÇ¬hleƒ?o (Nine Men's Morris) als Streamlit-App mit einem Custom Component Board.

**Sprache:** Bitte Antworten standardmÇÏÇYig auf Deutsch. (Englisch nur, wenn ausdrÇ¬cklich gewÇ¬nscht oder fÇ¬r kurze Fachbegriffe/Bezeichner nÇôtig.)

**Produktziel:** Trainings- und Analyse-Tool (ÇÏhnlich ƒ?zchess.comƒ?o-Denke), nicht nur ein Spiel.  
**Oberziel:** robust, deterministisch, testbar; KI-bereit (spÇÏter), aber zunÇÏchst ohne KI-Suche.

## Architektur (Quelle der Wahrheit)
### Frontend (Custom Component `muehle_board`)
- rendert SVG-Board + Hotspots
- verwaltet **lokale Selection** (z. B. `selected_src`) nur fÇ¬r Interaktion
- berechnet **legal targets** ausschlieÇYlich fÇ¬r **Hints/Overlays** (visuell)
- sendet fertige Aktionen: `place`, `move`, `remove`
- **kein Double-Click-Flow**, keine Backend-Selections

### Backend (Domain/Engine)
- hÇÏlt den `GameState`
- validiert Regeln und verhindert illegale States (auch wenn Frontend fehlerhaft ist)
- wendet fertige Aktionen deterministisch an

## Dateien & Verantwortlichkeiten
- `core/state.py`: DomÇÏnenmodell (`GameState`, `Stone`, helpers). Kein Streamlit.
- `core/graph.py`: Konstanten (`NEIGHBORS`, `MILLS`, Positionen).
- `core/rules.py`: Regel-Engine (Legal moves, mills, remove, end conditions). Bevorzugt pure functions.
- `core/analysis.py`: Read-only Analyse/Heuristik/Planung (kein State-Mutieren).
- `ui/board_svg.py`: SVG Rendering (keine Regel-Logik erzwingen).
- `ui/board_component.py`: Component bridge + Event-Typing.
- `engine/report.py`: Engine-Fassade fuer read-only Analyse/Overlays (Threats, Mobility, Kandidaten).
- `ui/`: UI-Fassade (Re-Exports fuer Board/History/Notation/UI-Helper).
- `muehle_board_component/`: Frontend (static). Keine ESM `import/export` verwenden, auÇYer es gibt ein Build (`dist/`/`build/`).
- `app.py`: Streamlit-Orchestrator (Wiring, Session-State, EventƒÅ'Action, rerun).

## Regelanforderungen (Domain)
- Phasen: `PLACING`, `MOVING`, `FLYING`
  - `PLACING ƒÅ' MOVING`, wenn Spieler keine Steine mehr ƒ?zin Handƒ?o hat
  - `MOVING ƒÅ' FLYING`, wenn Spieler nur noch 3 Steine besitzt
- Constraints:
  - max. 9 Steine pro Spieler
  - keine illegalen States zulassen (Backend validiert)
- MÇ¬hlenlogik:
  - MÇ¬hle erkennen nach place und move
  - Entfernen:
    - nur Steine auÇYerhalb von MÇ¬hlen
    - Ausnahme: sind alle gegnerischen Steine in MÇ¬hlen, darf jeder entfernt werden
    - pro ƒ?zMÇ¬hle schlieÇYenƒ?o-Aktion maximal 1 Remove (keine Mehrfach-Entfernung)
- Spielende:
  - Spieler hat < 3 Steine oder keinen legalen Zug mehr

## Coding Guidelines
- Regel-Logik als pure functions: `apply_action(state, action) -> new_state`.
- Keine Streamlit-AbhÇÏngigkeit in `core/rules.py`, `core/state.py`, `core/graph.py`.
- `GameState` snapshot-fÇÏhig, immutability bevorzugt.
- Move-History/Undo/Redo:
  - jede Aktion erzeugt einen neuen Snapshot
  - kein Mutieren alter States
  - optional: PGN-ÇÏhnliche Notation (`P:a7`, `M:a7-d7`, `R:b4`)
- Typed Events: `ActionEvent` als discriminated union nach `kind`:
  - `place`: `dst`, `nonce`
  - `move`: `src`, `dst`, `nonce`
  - `remove`: `dst`, `nonce`
- Defensive Guards im UI: Event-Keys prÇ¬fen, `nonce` gegen Doppel-Events.
- Tests mit `pytest` fÇ¬r Regel-Engine (mills, removables, legal moves, transitions).

## Analyse-/Training-Features (read-only)
Overlays sollen **keinen** GameState ÇÏndern, nur visualisieren:
- legal targets (bereits)
- removables (bereits)
- threat overlay (direkte Drohfelder: Gegner kann dort im nÇÏchsten Zug eine MÇ¬hle schlieÇYen)
- mobility overlay (Anzahl legaler ZÇ¬ge pro Stein)
- mill participation (potenzielle MÇ¬hlen pro Stein)
Alle Overlays togglebar.

## Component/Frontend Guidelines
- `index.html` muss:
  - `Streamlit.setComponentReady()` genau einmal nach Event-Listener-Setup aufrufen
  - auf `streamlit:render` reagieren und `args.svg` sichtbar rendern
  - `Streamlit.setComponentValue({...})` fÇ¬r Events verwenden
- Asset-Pfade relativ halten (./file.js).
- Cache-Busting wÇÏhrend Dev zulÇÏssig (`?v=...`).

## ƒ?oSkillsƒ?? / typische Aufgaben
- Neue Regeln implementieren + Unit Tests hinzufÇ¬gen
- Typing-Probleme (Pyright) beheben, ohne Runtime-Verhalten zu ÇÏndern
- SVG Rendering erweitern (Highlights/Hints)
- Component Events debuggen (Render args, frame height, nonce)
- Vorbereitung KI: `evaluate(state, player) -> score` (ohne Suche)

## Do / Donƒ?Tt
- DO: kleine, nachvollziehbare Ç"nderungen; Tests mitliefern.
- DO: Code klar trennen (rules vs UI).
- DON'T: Logik in `ui/board_svg.py` duplizieren, die in `core/rules.py` gehoert.
- DONƒ?TT: Frontend ESM verwenden, solange kein Build-Output (`dist/`/`build/`) existiert.

---

## Session-Protokoll (fÇ¬r effizientes Arbeiten mit Copilot)
Diese Regeln gelten, wenn der User explizit **ƒ?zsession startƒ?o** oder **ƒ?zsession endƒ?o** sagt.

### Trigger: ƒ?zsession start: <titel>ƒ?o
- Lies [docs/SESSION_LATEST.md](../docs/SESSION_LATEST.md) und die verlinkte letzte Note.
- Erzeuge eine neue Session Note unter `docs/sessions/` auf Basis von [docs/SESSION_TEMPLATE.md](../docs/SESSION_TEMPLATE.md).
- FÇ¬lle Abschnitt ƒ?z0) Kontextƒ?o mit einem kompakten Stand (Quelle: letzte Note).
- Çobernimm die dortigen ƒ?zNÇÏchste Schritteƒ?o als ToDo-Liste/Plan fÇ¬r diese Session.

### Trigger: ƒ?zsession endƒ?o
- Aktualisiere die aktuelle Session Note so, dass ein neues Kontextfenster genÇ¬gt:
  - ƒ?zKontextƒ?o + ƒ?zNÇÏchste Schritteƒ?o sind Pflicht.
  - Wichtige Semantik-Entscheidungen/Edge-Cases knapp festhalten.
- Optional Tests laufen lassen, falls der User das wÇ¬nscht.
- Doc-Sync nur bei Bedarf (PROJECT_OVERVIEW / DEV_NOTES / copilot-instructions).
- Update [docs/SESSION_LATEST.md](../docs/SESSION_LATEST.md) auf die aktuelle Note.
