# Dev Notes – Mühle (Streamlit + Custom Component)

## Voraussetzungen
- Windows, PowerShell
- Python (virtuelle Umgebung empfohlen)
- Node.js **optional** (nur falls du später ein echtes Frontend-Build einführst)

## Projekt-Start (lokal)
### 1) Python venv aktivieren
```powershell
cd C:\Users\rohor\Desktop\Robert\06_Projekte\muehle
.\venv\Scripts\Activate.ps1
```

### 2) Streamlit starten
```powershell
streamlit run .\app.py
```

Wenn Port belegt ist:
```powershell
streamlit run .\app.py --server.port 8502
```

## Custom Component (Frontend) – aktueller Stand (static)
Frontend liegt in:
- `muehle_board_component/index.html`
- `muehle_board_component/streamlit-component-lib.js`

**Wichtig:** Da aktuell **kein** `dist/` oder `build/` existiert, darf das Frontend **keine** ESM-Syntax verwenden:
- DONT `import ...`
- DONT `export ...`
- DO klassische `<script src="..."></script>` + globale `window.Streamlit` API

### Mindestanforderungen an `index.html`
- `Streamlit.events.addEventListener(Streamlit.RENDER_EVENT, ...)` registrieren
- danach **genau einmal** `Streamlit.setComponentReady()` aufrufen
- im Render-Handler `args.svg` sichtbar in den DOM schreiben
- Klicks als `Streamlit.setComponentValue({ kind, src?, dst?, nonce })` senden
- `Streamlit.setFrameHeight(...)` **nach** `setComponentReady()` und idealerweise nach DOM-Update setzen

## Typisches Debugging (Component lädt nicht / Board bleibt leer)

### 1) Browser DevTools öffnen
- F12 → **Console** und **Network**

**Wenn du siehst:**
- `Unexpected token 'export'` oder `Unexpected token 'import'`  
  → du lädst ESM als klassisches Script. Entfernen/ersetzen (static-only!).

- `Client Error: Custom Component ... timeout error`  
  → Component hat kein `setComponentReady()` gesendet oder JS ist vorher gecrasht.

- `Got streamlit:setFrameHeight before streamlit:componentReady!`  
  → Reihenfolge fixen: zuerst Listener, dann `setComponentReady()`, dann `setFrameHeight()`.

### 2) Quick-Checks im Terminal
Komponente-Assets vorhanden?
```powershell
dir .\muehle_board_component
```

Hat die JS-Datei noch ESM?
```powershell
Select-String -Path .\muehle_board_component\streamlit-component-lib.js -Pattern "^\s*export\s"
Select-String -Path .\muehle_board_component\streamlit-component-lib.js -Pattern "^\s*import\s"
```

### 3) Render-Args verifizieren
Temporär in `index.html` in den Render-Handler:
```js
console.log("RENDER ARGS", event.detail.args);
```
Erwartet wird u. a.:
- `svg` (string)
- `hotspots` (list)
- `board`, `to_move`, `phase`, `pending_remove`, `removables`, `hints_enabled` (je nach App)

### 4) Cache-Probleme umgehen
Während Dev ist Cache oft die Ursache. Nutze cache-busting:
```html
<script src="./streamlit-component-lib.js?v=5"></script>
```
und dann Hard-Reload: **Ctrl+F5**.

## Backend-Regeln / Typing / Tests

### Leitlinien (wichtig)
- `core/state.py`, `core/rules.py`, `core/graph.py` sind **streamlit-frei**
- Regel-Logik als **pure functions**, z. B.:
  - `apply_action(state, action) -> new_state`
- UI (Streamlit) nur in `ui/streamlit_app.py` und `ui/ui.py` (app.py ist Wrapper)
- `ActionEvent` typisieren als **discriminated union** nach `kind`

## Engine-Design (Kurzfassung)
- Suche: Minimax + Alpha-Beta, Iterative Deepening, TT, Move Ordering.
- API: engine.analyze(...) / engine.best_move(...) -> AnalysisResult (Best Move, Depth, Nodes, PV, Top-N, Breakdown, Threat-Report).
- TT-Symmetrie: kanonische Hashes, symmetrische Treffer nur score-only (kein Best-Move).
- Eval: Tier-1 (Material, Mobility, Mills, Open Mills, Mill-in-1, Blocked).
- Eval: Tier-2 (Double Threats, Initiative, Connectivity).
- Why-Panel: Top-N + Klassifikation (loss) + PV-Satz + Breakdown-Diff.
- Move-Handling: Ply ist Composite (place/move/fly inkl. optionalem remove).

## Analyse / Overlays (read-only)
- TODO: tune initiative weights and consider phase-specific scaling (placing vs moving/flying).

Aktuell gibt es ein bewusst leichtgewichtiges Analyse-Panel und ein Threat-Overlay.

### Analyse-Panel
- Implementiert in `ui/streamlit_app.py` (`render_analysis_panel`), `engine/report.py` und `core/analysis.py`.
- UI: In der rechten Spalte als Expander „Analyse (aktuelle Stellung)“.
- Inhalt (derzeit): Threat-Squares, Mobility (Score/Ø), blockierte Steine, Kandidatenzüge für `to_move`.

### Threat-Overlay (Board)
- UI: Sidebar Toggle „Threat-Overlay“.
- Bedeutung: Es werden die **direkten Drohfelder des Gegners** angezeigt (aus Sicht des Spielers am Zug).
- Technisch:
  - `threat_overlay_targets(state)` (Engine-Fassade)
  - wird als `hint_targets` an `render_board_svg(...)` übergeben.

**Wichtig:** `compute_threat_squares` ist Mustererkennung und prüft bewusst keine Reichweite/Legalität (Place vs Move). Overlays ändern nie den `GameState`.

### Quick-Debugging
- Wenn Overlay/Analyse „leer“ wirkt: Prüfe Phase/Board-State, und ob das Spiel bereits beendet ist (dann werden Board-Clicks/Threat-Overlay deaktiviert).
- Falls nötig temporär in `app.py` loggen: `st.write(st.session_state.get("threat_overlay"))`.

### Tests (pytest)
Empfohlen: Tests für
- Mill-Erkennung
- legal moves (placing/moving/flying)
- removable candidates (wenn Mill entstanden ist)
- state transitions inkl. `pending_remove`

Beispiel-Run:
```powershell
pytest -q
```

## Troubleshooting – Checkliste
1. Component zeigt Timeout?
   - Console: JS error? (rot)
   - `setComponentReady()` wird aufgerufen?
2. Component ready, aber leer?
   - Kommt `streamlit:render` überhaupt an? (`console.log`)
   - Wird `args.svg` gesetzt und in DOM geschrieben?
3. Klicks kommen nicht im Python an?
   - Frontend: `Streamlit.setComponentValue(...)` wird gefeuert?
   - Python: `clicked` ist nicht `None` und nonce wird nicht geblockt?

## Optional: späteres Frontend-Build (nicht aktiv)
Wenn du später auf Vite/webpack gehst:
- Build-Output in `dist/` oder `build/`
- `ui/board_component.py` sollte dann auf diesen Ordner zeigen
- dann darfst du ESM verwenden (über bundling), aber nicht im „static“ Root ohne Build.