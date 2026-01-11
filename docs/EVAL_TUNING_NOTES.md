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

## 2) Phase-Scaling (Leitlinie)

### Placing Phase
Spielrealitaet:
- Steine sind hoch mobil (setzen ueberall).
- Blockaden sind nicht stabil.
- Taktik entsteht ueber Struktur, nicht ueber Bewegung.

Dominante Faktoren:
- Threats (Mill-in-1): hoch
- Double/Fork Threats: sehr hoch
- Open Mills: hoch
- Connectivity: mittel
- Material: konstant
- Mobility: 0 (nahezu bedeutungslos)
- Blocked Opponent: 0 (bedeutungslos)

Setup-Notiz:
- Threat/Open/Double/Fork bleiben primaer.
- Mobility muss auf 0 skaliert werden, sonst entstehen Fake-Signale.
- Blocked Opponent hart deaktivieren.

Typischer Fehler:
- Mobility zaehlt mit, weil "Zuege existieren".

### Moving Phase
Spielrealitaet:
- Bewegung ist eingeschraenkt.
- Blockaden entstehen und wirken nachhaltig.
- Initiative wirkt dauerhaft.

Dominante Faktoren:
- Mobility: sehr hoch
- Blocked Opponent: hoch
- Threats (Mill-in-1): hoch
- Double/Fork Threats: hoch
- Open Mills: mittel
- Material: hoch
- Connectivity: mittel

Setup-Notiz:
- Mobility und Blocked duerfen nicht gleichzeitig mit Initiative aktiv sein
  (Double-Counting vermeiden).
- Fork/Double nur zaehlen, wenn Reachability gegeben ist.

Typischer Fehler:
- Threats zaehlen, obwohl der Zug gar nicht erreichbar ist.

### Flying Phase
Spielrealitaet:
- Mobility ist kuenstlich hoch (Fliegen).
- Blockaden verlieren an Stabilitaet.
- Taktik wird brutal direkt.

Dominante Faktoren:
- Threats (Mill-in-1): sehr hoch
- Double/Fork Threats: sehr hoch
- Material: entscheidend
- Open Mills: niedrig
- Mobility: 0 (fast irrelevant)
- Blocked: 0 (fast irrelevant)
- Connectivity: 0 (irrelevant)

Typischer Fehler:
- Mobility zaehlt noch mit und erzeugt falsche Endspiel-Signale.

---

## 3) Typische Phase-Scaling-Fehler (Checklist)

- Fehler 1: Gewicht * Phase ohne Normalisierung.
  Fix: Feature-Werte phasenstabil normieren, dann skalieren.
- Fehler 2: Initiative + Mobility gleichzeitig aktiv.
  Fix: Initiative ersetzt Mobility/Threat-Cluster, sie ergaenzt sie nicht.
- Fehler 3: Blocked im Placing oder Flying.
  Fix: Blocked nur in Moving-Phase werten.
- Fehler 4: Open Mills gleich Threats.
  Fix: Open = Struktur, Threat = erreichbare Taktik.

---

## 4) Referenz-Implementierung (robust)

Phase-Profil:
```
PHASE_SCALE = {
    "placing": {
        "material": 1.0,
        "mills": 0.8,
        "open_mills": 1.2,
        "threats": 1.5,
        "double_threats": 1.5,
        "fork_threats": 1.5,
        "mobility": 0.0,
        "blocked": 0.0,
        "connectivity": 0.7,
    },
    "moving": {
        "material": 1.0,
        "mills": 1.0,
        "open_mills": 0.8,
        "threats": 1.2,
        "double_threats": 1.2,
        "fork_threats": 1.2,
        "mobility": 1.3,
        "blocked": 1.2,
        "connectivity": 0.6,
    },
    "flying": {
        "material": 1.5,
        "mills": 1.0,
        "open_mills": 0.4,
        "threats": 1.6,
        "double_threats": 1.6,
        "fork_threats": 1.6,
        "mobility": 0.0,
        "blocked": 0.0,
        "connectivity": 0.0,
    },
}
```

Score-Komposition:
```
score = 0.0
for feature, raw_value in features.items():
    base_w = BASE_WEIGHTS[feature]
    phase_w = PHASE_SCALE[state.phase][feature]
    score += raw_value * base_w * phase_w
```

Why-Panel:
- Why-Panel zeigt nur die rohen Feature-Werte.
- Phase-Scaling ist Engine-intern, kein UI-Konzept.

---

## 5) Didaktische Leitplanke

- Phase-Scaling darf nie direkt im UI sichtbar sein.
- Ziel: Nutzer sehen, dass X wichtiger ist als Y, nicht den Faktor.

---

## 6) Weight-Tuning (Diskussion / ToDo)

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

## 7) Offene Fragen (spaeter klaeren)

- Soll `fork_threats` in Moving strenger sein (nur wenn Zug die Muehle
  schliesst, ohne die beiden Steine der Linie zu bewegen)?
- Ring-Gewichtung dynamisch an Mobility/Connectivity koppeln?
- Sollen Phase-Weights als eigene Defaults in `EvalWeights` hinterlegt werden?
