# Session Note – 2026-01-07 (Planning future scope and prepare refactoring)

## 0) Kontext (für „neues Chat-Fenster“)
- Ziel dieser Session (1–3 Bulletpoints):
  - Nächste inhaltliche Features/Overlays priorisieren (Training/Analyse-Fokus)
  - Refactoring-Scope festlegen (sicher, testbar, deterministisch; keine UX-Extrafeatures)
  - Konkreten PR-fähigen Next-Step definieren (klein, klar, CI-grün)
- Ausgangszustand: Branch/Commit (optional): Baseline + Workflow/CI stehen; `pytest -q` ist grün (zuletzt verifiziert in CI)
- Aktueller Scope: Planung + Refactoring-Vorbereitung (Engine/Rules/Analysis-Architektur; keine neuen Regeln heute, außer als Folge der Planung)
- Definition of Done für heute:
  - Ein kurzer, konkreter Scope-/Roadmap-Entwurf (1–3 nächste PRs) liegt schriftlich vor
  - Refactoring-Kandidaten (Dateien/Symbole) sind identifiziert inkl. Risiko/Benefit
  - TODO-Liste ist PR-orientiert (kleine Steps, testbar)

## 1) Was ist funktional (User-Sicht)
- Streamlit-App + Board-Component funktionieren als Spiel- und Analyse-Demo.
- Testsuite existiert und läuft via CI (`pytest -q`).

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
- Refactorings dürfen keine Regel- oder State-Invarianten verwässern (Backend bleibt „source of truth“).
- Frontend bleibt „static“ (kein Build) — keine ESM-Umstellung ohne bewusstes Build-Setup.

## 7) Nächste Schritte (konkret)
1. Nächstes Feature als echter Session-Branch + PR: z. B. Mobility/Blocked-Overlay oder „Forced Mills“ (siehe Baseline-Note).
2. Optional: MIT-License hinzufügen, falls Repo public und Weiterverwendung erwünscht.
3. Optional: Demo-Datei `docs/PR_DEMO.md` wieder entfernen, falls sie noch im `main` liegt (zweiter Übungs-PR).

## 8) Doc-Sync Checklist (Ende der Session)
- [ ] [docs/PROJECT_OVERVIEW.md](PROJECT_OVERVIEW.md) aktualisiert (falls Architektur/Module sich geändert haben)
- [ ] [.github/copilot-instructions.md](../.github/copilot-instructions.md) nur angepasst, wenn Repo-Regeln/Do-Donts sich geändert haben
- [ ] [docs/DEV_NOTES.md](DEV_NOTES.md) aktualisiert, wenn neue Debug-/Run-Infos dazukommen
- [ ] „Context-Reset“-Abschnitt in der Note ausgefüllt (siehe Abschnitt 0)
