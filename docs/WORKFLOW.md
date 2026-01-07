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
