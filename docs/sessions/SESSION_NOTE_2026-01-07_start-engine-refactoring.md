# Session Note – 2026-01-07 (start-engine-refactoring)

## 0) Kontext (für „neues Chat-Fenster“)
- Ziel dieser Session (1–3 Bulletpoints):
  - Engine-Refactoring nach Zielbild anstoßen (State/Rules klar trennen, Move-Generator erweitern)
  - Suche-Scaffold vorbereiten (API-Skizze, Schnittstellen)
- Ausgangszustand: Branch main, Analyse-Fixes aus letzter Session grün und merge-bereit
- Aktueller Scope: Engine/Domain Refactoring + vorbereitende Search-API
- Definition of Done für heute: Refactoring-Plan fixiert, erste Engine-Skelettteile angelegt/tests grün

## 1) Was ist funktional (User-Sicht)
- Board-Rendering, legale Züge, Mills, Phasenwechsel, Remove, Game-End-Bedingungen ✅

## 2) Engine/Domain Änderungen (Backend)
- Betroffene Dateien:
- Neue/angepasste Invarianten:
- Regelentscheidungen/Edge-Cases:

## 3) UI / Component Änderungen (Frontend/Streamlit)
- Betroffene Dateien:
- Event-Pipeline (kind/src/dst/nonce) Änderungen:
- Guards / UX-Entscheidungen:

## 4) Analyse/Training Features (read-only)
- Neue Overlays/Panelwerte:
- Semantik (wichtig!):

## 5) Tests / Status
- `pytest -q`:
- Neue Tests:
- Bekannte Failing/Skipped:

## 6) Offene Punkte / Risiken
- Merge des Analyse-Fix-Branches auf main ggf. noch ausstehend
- Engine-API/Search-Stubs weiterhin offen

## 7) Nächste Schritte (konkret)
1. Branch/PR mit Analyse-Fixes (`mill/analysis.py`) nach main mergen
2. Engine-Refactoring starten gemäß Zielbild (State/Rules isolieren, Move-Generator für alle Phasen inkl. Remove als Teilzug)
3. Search-Scaffold aufsetzen (Alpha-Beta/ID, Eval-Breakdown, API `engine.analyze`/`engine.best_move`), gemäß Notizen in txt.txt

## 8) Doc-Sync Checklist (Ende der Session)
- [ ] [docs/PROJECT_OVERVIEW.md](PROJECT_OVERVIEW.md) aktualisiert (falls Architektur/Module sich geändert haben)
- [ ] [.github/copilot-instructions.md](../.github/copilot-instructions.md) nur angepasst, wenn Repo-Regeln/Do-Donts sich geändert haben)
- [ ] [docs/DEV_NOTES.md](DEV_NOTES.md) aktualisiert, wenn neue Debug-/Run-Infos dazukommen
- [ ] „Context-Reset“-Abschnitt in der Note ausgefüllt (siehe Abschnitt 0)
