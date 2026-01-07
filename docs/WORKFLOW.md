# Workflow: Copilot-gesteuerte Session-Pipeline

Ziel: Du sagst nur **„session start“** oder **„session end“** – Copilot pflegt Notes/Dokus so, dass du nach einem Kontext-Reset sofort weiterarbeiten kannst.

## 1) Session Start (du tippst nur)
Prompt an Copilot:
- **`session start: <kurzer titel>`**

Optional (wenn Copilot das File automatisch anlegen soll):
- Copilot kann dafür `./scripts/session.ps1 start -Title "<titel>"` ausführen.

Copilot erledigt dann:
- liest [docs/SESSION_LATEST.md](SESSION_LATEST.md) und die zuletzt verlinkte Note
- erstellt eine **neue** Session Note unter [docs/sessions/](sessions/) (aus [docs/SESSION_TEMPLATE.md](SESSION_TEMPLATE.md))
- schreibt oben in Abschnitt „Kontext“ eine kompakte Zusammenfassung aus der letzten Note
- übernimmt „Nächste Schritte“ als ToDo-Liste für die aktuelle Session (und fragt kurz nach Priorität, falls nötig)
- optional: kurzer Check `pytest -q` (nur wenn du es willst)

## 2) Session End (du tippst nur)
Prompt an Copilot:
- **`session end`**

Optional (nur Pointer aktualisieren):
- Copilot kann `./scripts/session.ps1 end` ausführen (setzt [docs/SESSION_LATEST.md](SESSION_LATEST.md)).

Optional genauer:
- **`session end: <titel> (mit tests)`**

Copilot erledigt dann:
- schreibt/aktualisiert die aktuelle Session Note:
  - „Was ist funktional“, wichtigste Entscheidungen, Edge-Cases
  - **Kontext-Abschnitt** so, dass ein neues Chat-Fenster genügt
  - „Nächste Schritte“ (die wir im Chat beschlossen haben)
- optional: führt `pytest -q` aus und trägt den Status ein
- macht **Doc-Sync nur bei Bedarf**:
  - [docs/PROJECT_OVERVIEW.md](PROJECT_OVERVIEW.md) (nur bei Architektur/Module-Änderungen)
  - [.github/copilot-instructions.md](../.github/copilot-instructions.md) (nur bei Repo-Regel-Änderungen)
  - [docs/DEV_NOTES.md](DEV_NOTES.md) (nur bei neuen Debug-Fallen)
- aktualisiert [docs/SESSION_LATEST.md](SESSION_LATEST.md)

## 3) Kontext-Reset / neues Chat-Fenster
Prompt an Copilot (Minimal):
- „Bitte lies [docs/SESSION_LATEST.md](SESSION_LATEST.md) und die verlinkte Note. Arbeite dann `Nächste Schritte #1` ab.“

Wenn du nur einen Ausschnitt schicken willst:
- Abschnitt „0) Kontext“ + „7) Nächste Schritte“ aus der letzten Note.

## 4) Konventionen
- Notes liegen unter [docs/sessions/](sessions/).
- [docs/SESSION_LATEST.md](SESSION_LATEST.md) zeigt auf die **aktuell relevante** Note.

---

## 5) PR-Workflow (solo + Copilot) – pragmatisch
Warum PRs auch solo helfen:
- Du bekommst eine „Review“-Ansicht (Diff), eine klare Feature-Grenze und automatische Tests (CI).
- Du kannst jederzeit auf `main` zurück, ohne Angst vor einem halbfertigen Stand.

### Grundprinzip
- `main` bleibt stabil („grün“): nur mergen, wenn `pytest -q` lokal und in GitHub Actions grün ist.
- Jede Session / jedes Ziel bekommt einen Branch + PR.

### Schrittfolge (Copy/Paste)
1) Branch für das Session-Ziel anlegen
  - `git checkout main`
  - `git pull`
  - `git checkout -b session/2026-01-08-kurzer-slug`

2) Copilot arbeiten lassen
  - Du sagst z. B. „Implementiere X“.
  - Copilot ändert Dateien im Workspace.
  - Du commitest in sinnvollen Häppchen (nicht erst am Ende).

3) Lokal testen
  - `pytest -q`

4) Push + PR öffnen
  - `git push -u origin session/2026-01-08-kurzer-slug`
  - Auf GitHub: „Compare & pull request“ (anfangs gern als Draft).

5) CI abwarten
  - Im PR siehst du den GitHub Actions Check „tests“.
  - Rot = Fixen im Branch, erneut pushen (der PR aktualisiert sich automatisch).

6) Mergen
  - Wenn grün: „Squash and merge“ ist ein guter Default (ein sauberer Commit auf `main`).
  - Danach lokal: `git checkout main` + `git pull`.

### Mini-Checklist (Ende einer Session / vor Merge)
- `pytest -q` lokal grün
- PR: GitHub Actions „tests“ grün
- Session Note: Abschnitt „0) Kontext“ + „7) Nächste Schritte“ aktuell
- Optional: Docs nur wenn nötig (PROJECT_OVERVIEW / DEV_NOTES / copilot-instructions)

### Wie das mit dem Copilot-Session-Workflow zusammenspielt
- `session start: <titel>`: Copilot liest die letzte Note und macht einen Plan.
- Dann: Branch erstellen (oben) und Copilot die Aufgaben abarbeiten lassen.
- `session end`: Copilot fasst zusammen + schreibt Next Steps in die Note.
- Wenn du mitten drin ein neues Chat-Fenster brauchst: Copilot soll [docs/SESSION_LATEST.md](SESSION_LATEST.md) lesen und weiter bei „Nächste Schritte #1“ machen.
