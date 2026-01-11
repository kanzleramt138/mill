# Eval Tuning Notes (Besprechungsstand)

Ziel: Den aktuellen Stand der Eval-/Metrik-Diskussion festhalten, damit
Phase-Scaling und Weight-Tuning spaeter systematisch umgesetzt werden koennen.

---

## 1) Aktuelle Aenderungen (Stand)

- Neue Metrik **Fork-Threats**: mehrere Mill-in-1-Drohfelder gleichzeitig.
- Fork-Threat-Score ist **ring-gewichtet** (Mittelring > Innen/Aussen).
- `EvalBreakdown`/`EvalWeights` enthalten jetzt `fork_threats`.
- Initiative-Weights schalten Basis-Metriken auf 0, um Double-Counting zu vermeiden
  (Mobility/Open/Threat/Blocked/Double/Fork/Connectivity).

Definitionen (wichtig fuer Interpretation):
- **Open Mills**: 2 eigene Steine + 1 leer, rein strukturell (kein Reachability-Check).
- **Threats (Mill-in-1)**: leere Felder, die im *naechsten* Zug erreichbar sind
  (Phase-Logik: placing/flying = beliebig, moving = adjacent).
- **Double Threats**: ein Feld schliesst *zwei* Muehlen gleichzeitig.
- **Fork Threats**: *mindestens zwei verschiedene* Threat-Squares gleichzeitig.

Ring-Gewichtung (core/graph.py):
- outer = 1.0
- middle = 1.25
- inner = 1.0

---

## 2) Phase-Scaling (Diskussion)

### Placing
- Fokus auf Threats/Open Mills/Double-/Fork-Threats und Connectivity.
- Mobility nur moderat gewichten (noch instabil).
- Ziel: Drohungen aufbauen oder verhindern, mit Blick auf kommende Moving-Phase.

### Moving
- Mobility + Blocked stark (Zugzwang-Gefahr).
- Threats/Double-Threats weiterhin zentral.
- Fork-Threats stark, weil sie Blockaden erzwingen.

### Flying
- Mobility weniger relevant (freie Zuege), Blockade weniger stark.
- Threats/Double-/Fork-Threats dominieren.
- Material bleibt kritisch (ein Stein Verlust kann sofort verlieren).

---

## 3) Weight-Tuning (Diskussion / ToDo)

Ziel: Spielstaerke erhoehen, ohne neue Komplexitaet im Modell.

Vorgehen:
1. **Stabile Baselines** pro Phase (Startgewichte definieren).
2. **Kleine Teststellungen** kuratieren (pro Phase 2-3).
3. **Vergleich**: Best-Move-Qualitaet + Why-Panel-Kohaerenz.
4. **Feintuning** in kleinen Schritten, nur eine Metrik pro Iteration.

Wichtige Leitplanken:
- Double-Counting vermeiden (Initiative-Weights vs. Einzelmetriken).
- Fork/Double nur gewichten, wenn Threat-Definitionen konsistent sind.
- Ring-Gewichtung spaeter optional feinjustieren (Middle > Outer/Inner).

---

## 4) Offene Fragen (spaeter klaeren)

- Soll `fork_threats` in Moving strenger sein (nur wenn Zug die Muehle
  schliesst, ohne die beiden Steine der Linie zu bewegen)?
- Ring-Gewichtung dynamisch an Mobility/Connectivity koppeln?
- Sollen Phase-Weights als eigene Defaults in `EvalWeights` hinterlegt werden?
