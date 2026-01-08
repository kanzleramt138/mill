# Session Note - 2026-01-08 (Why Panel)

## 0) Kontext (fuer "neues Chat-Fenster")
- Ziel dieser Session (1-3 Bulletpoints):
  - Why-Panel: Move-Klassifikation anhand Score-Delta
  - Why-Panel: Eval-Breakdown-Diff anzeigen
  - Why-Panel: Taktik-Hinweise (Mill-in-1 erlaubt/verpasst, blockierte Steine)
- Ausgangszustand: Branch `feature/why-panel`, Analyse-Fixes gemergt
- Aktueller Scope: Analyse/Why-Panel (UI + Engine-Auswertung)
- Definition of Done fuer heute: Why-Panel zeigt Klassifikation, Breakdown-Diff und erste Taktik-Hints; UI stabil

## 1) Was ist funktional (User-Sicht)
- Board-Rendering, legale Zuege, Mills, Phasenwechsel, Remove, Game-End-Bedingungen ok.

## 2) Engine/Domain Aenderungen (Backend)
- Betroffene Dateien:
- Neue/angepasste Invarianten:
- Regelentscheidungen/Edge-Cases:

## 3) UI / Component Aenderungen (Frontend/Streamlit)
- Betroffene Dateien:
- Event-Pipeline (kind/src/dst/nonce) Aenderungen:
- Guards / UX-Entscheidungen:

## 4) Analyse/Training Features (read-only)
- Neue Overlays/Panelwerte:
- Semantik (wichtig!):

## 5) Tests / Status
- `pytest -q`:
- Neue Tests:
- Bekannte Failing/Skipped:

## 6) Offene Punkte / Risiken
-

## 7) Naechste Schritte (konkret)
1. Why-Panel: Move-Klassifikation (Best/Good/Inaccuracy/Mistake/Blunder) anhand Score-Delta
2. Why-Panel: Eval-Breakdown-Diff (Feature-Aenderungen vs. Best-Move) anzeigen
3. Why-Panel: Taktische Hinweise (Mill-in-1 erlaubt/verpasst, blockierte Steine, etc.)

## 8) Doc-Sync Checklist (Ende der Session)
- [ ] [docs/PROJECT_OVERVIEW.md](PROJECT_OVERVIEW.md) aktualisiert (falls Architektur/Module sich geaendert haben)
- [ ] [.github/copilot-instructions.md](../.github/copilot-instructions.md) nur angepasst, wenn Repo-Regeln/Do-Donts sich geaendert haben
- [ ] [docs/DEV_NOTES.md](DEV_NOTES.md) aktualisiert, wenn neue Debug-/Run-Infos dazukommen
- [ ] "Context-Reset"-Abschnitt in der Note ausgefuellt (siehe Abschnitt 0)
