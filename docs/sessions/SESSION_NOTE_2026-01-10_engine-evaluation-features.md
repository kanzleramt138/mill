# Session Note - 2026-01-10 (Engine Evaluation Features)

## 0) Kontext (fuer "neues Chat-Fenster")
- Ziel dieser Session (1-3 Bulletpoints):
  - Engine-Evaluation-Features konsolidieren und dokumentieren.
  - Offene Punkte priorisieren (Eval-Tuning, UI-Feinschliff, Search-Refactor, Tests, Overlays).
- Ausgangszustand: main synced; Why-Panel + Tier-2 Eval fertig; 75 tests passed.
- Aktueller Scope: Dokumentation + Evaluation/Analyse-Verbesserungen.
- Definition of Done fuer heute: Session-Plan festgehalten, naechste Schritte klar.

## 1) Was ist funktional (User-Sicht)
- 

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
1. Eval-Tuning (Initiative-Gewichte, Phasen-Skalierung).
2. UI-Feinschliff (Why-Panel/Hint-Labels, Legenden, Lesbarkeit).
3. Search-Refactor (Duplicate eval im Root entfernen).
4. Why-Panel-Tests (Klassifikation/Breakdown-Diff verifizieren).
5. Board-Overlay erweitern (Mobility/Blocked auf dem Board).

## 8) Doc-Sync Checklist (Ende der Session)
- [ ] [docs/PROJECT_OVERVIEW.md](PROJECT_OVERVIEW.md) aktualisiert (falls Architektur/Module sich geaendert haben)
- [ ] [.github/copilot-instructions.md](../.github/copilot-instructions.md) nur angepasst, wenn Repo-Regeln/Do-Donts sich geaendert haben
- [ ] [docs/DEV_NOTES.md](DEV_NOTES.md) aktualisiert, wenn neue Debug-/Run-Infos dazukommen
- [ ] "Context-Reset"-Abschnitt in der Note ausgefuellt (siehe Abschnitt 0)
