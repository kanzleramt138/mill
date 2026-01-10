# Decision Guide (Ableitungen aus Analyse)

Ziel: Die Metriken im Analyse-Panel sollen in klare Schluesse und
konkrete Zugentscheidungen uebersetzt werden.

---

## 1) Ableitungs-Map: Metrik -> Schluss -> Entscheidung

### Material (negativ)
- Schluss: Rueckstand, reines Abtauschen verschlechtert oft.
- Entscheidung: Taktische Kompensation suchen (Muehle, Double-Threat, Blockade).

### Mills / Open Mills / Threats
- Schluss: Taktische Initiative oder direkte Gefahr.
- Entscheidung: Wenn Threats > 0: Mill schliessen oder gegnerische Threat blocken.

### Blocked Opponent / Blocked Stones
- Schluss: Zugzwang- bzw. Endspielvorteil.
- Entscheidung: Blockaden halten oder erhoehen.

### Mobility (beide Seiten)
- Schluss: Manoevrierspielraum.
- Entscheidung:
  - Eigene Mobility niedrig -> entblocken, Verbindungen schaffen.
  - Gegnerische Mobility niedrig -> blockieren, keine Befreiung zulassen.

### Connectivity
- Schluss: Qualitaet der Felder / Flexibilitaet.
- Entscheidung: Umgruppieren auf Felder mit mehr Nachbarn.

### Initiative (strategic/tactical)
- Schluss: Wer diktiert den Verlauf.
- Entscheidung: Negative Initiative -> aktive Drohungen erzeugen.

---

## 2) Decision Hints (deterministisch, aus Metriken)

Kurze, klare Ableitungen direkt unter dem Why-Panel:
- "Material-Rueckstand: Suche nach Muehle/Blockade als Kompensation."
- "Gegnerische Mobility niedrig: Blockierende Zuege priorisieren."
- "Threats vorhanden: Mill-in-1 pruefen oder blocken."
- "Viele eigene Steine blockiert: Entblocken vor Angriff."

Ziel: 1-3 Hints pro Stellung, keine generischen Texte.

---

## 3) Overlay-Prioritaeten (visuelle Ableitung)

Reihenfolge fuer visuelle Lernwirkung:
1. Threat-Overlay (bereits vorhanden)
2. Blocked-Overlay (Steine ohne legale Zuege markieren)
3. Mobility-Overlay (Farbintensitaet = Mobilitaet pro Stein)
4. Double-Threat-Overlay (Felder mit 2 Muehlen)

Ziel: Entscheidungsrelevante Infos auf dem Brett sichtbar machen,
nicht nur im Textpanel.

---

## 4) Prioritaetsregeln (Konflikte aufloesen)

Wenn mehrere Hinweise gleichzeitig feuern, gilt folgende Reihenfolge:
1. **Akute Taktik**: Eigene Mill-in-1 schliessen oder gegnerische Threat blocken.
2. **Double-Threats**: Doppelte Drohung erzeugen oder verhindern.
3. **Blockade**: Gegner blockieren, eigene Blockaden aufloesen.
4. **Mobility**: Manövrierfaehigkeit sichern/erhoehen.
5. **Connectivity**: langfristige Feldqualitaet verbessern.

Kurz: Erst Gefahr/Chance, dann Struktur, dann Langfrist.

---

## 5) Phasen-spezifische Ableitungen

### Placing
- Wichtig: Open Mills, Threats, Double-Threats, Connectivity.
- Weniger wichtig: Mobility (noch nicht stabil), Blocked nur begrenzt.
- Entscheidung: Drohung erzeugen oder verhindern hat Prioritaet.

### Moving
- Wichtig: Mobility, Blocked, Threats.
- Entscheidung: Wenn Mobility niedrig -> entblocken; sonst Angriff/Threat.

### Flying
- Mobility weniger relevant (freie Zuege), Blockade geringer.
- Wichtig: Threats und Material (Endspiel).
- Entscheidung: direkte Taktik und Materialerhalt.

---

## 6) Trigger-Definitionen (Startwerte)

Diese Schwellwerte sind Startpunkte fuer Hints:
- **Threats vorhanden**: Threats >= 1
- **Double-Threat**: Double-Threats >= 1
- **Niedrige Mobility**: avg_mobility < 1.0
- **Hohe Blockade**: blocked_ratio >= 0.4
- **Material-Rueckstand**: material <= -2.0

Alle Schwellen pro Phase spaeter feinjustieren.

---

## 7) Ableitungs-Templates fuer Hints

Beispiele (deterministisch):
- "Du hast eine direkte Threat: Mill-in-1 pruefen."
- "Gegner hat Threats: Block oder Gegen-Muehle."
- "Viele eigene Steine blockiert: erst entblocken."
- "Material-Rueckstand: suche taktische Kompensation."

Regel: maximal 3 Hints, nach Prioritaet geordnet.

---

## 8) Datenquellen (Mapping Code -> Metrik)

- Threats: `compute_threat_squares` (core/analysis.py)
- Double-Threats: `double_threat_squares`
- Blocked: `blocked_stones`
- Mobility/Profil: `mobility_profile`, `mobility_score`
- Breakdown: `engine/eval.py` (EvalBreakdown)

---

## 9) Roadmap zur Umsetzung

1. **Hints-Engine**: kleine pure Funktion `derive_hints(state) -> list[str]`
2. **Phase-Regeln**: Phase-abh. Schwellen/Prio
3. **UI**: Hints unter Why-Panel anzeigen, max. 3
4. **Overlays**: Blocked/Mobility/Double-Threat als Toggle
5. **Tuning**: Schwellen/Weights nach Tests

---

## 10) Tests / Validierung

- 2-3 feste Teststellungen je Metrik (Threat, Blockade, Flying).
- Unit Tests fuer `derive_hints` (deterministisch).
- Snapshot-Tests fuer Overlay-Sets (z. B. Threat-Targets).

---

## 11) Entscheidungslogik fuer Zuege vorausdenken

Ziel: Die Ableitung soll nicht nur "was ist gut" sagen, sondern auch
"welche Folge entsteht, wenn ich X spiele".

Vorschlag:
- Pro Top-Move die **Top-2 Treiber** (Breakdown-Diff) nennen.
- Dazu eine kurze **Konsequenz** aus der PV:
  - Beispiel: "Du gewinnst Blockade, aber oeffnest eine gegnerische Threat."

Das verknuepft Zahlen mit konkreten Folgen.

---

## 12) Beispiel-Entscheidungen (Textbausteine)

### Wenn Threats vorhanden
- "Du kannst eine Muehle in 1 schliessen: priorisieren."
- "Du kannst blocken: opfere ggf. einen Stein, wenn Material ohnehin negativ ist."

### Wenn Blocked hoch
- "Blockade sichern (keine Entblockung erlauben)."
- "Eigene Blockaden zuerst loesen, bevor Angriff."

### Wenn Mobility niedrig
- "Entblocken + Verbindungen herstellen, sonst droht Zugzwang."

### Wenn Material stark negativ
- "Nur Zuege mit unmittelbarer Kompensation (Muehle/Double-Threat) sind sinnvoll."

---

## 13) Confidence / Signalstaerke

Optional: Jeder Hint bekommt ein **Signal-Level** (low/med/high).
Beispiel-Heuristik:
- Threats >= 2 -> high
- Blocked ratio >= 0.5 -> high
- Mobility avg < 0.7 -> med
- Connectivity nur als low

UI kann spaeter z. B. Icon-Farbe nutzen.

---

## 14) Output-Format fuer Hints (API)

Vorschlag:
```
Hint {
  kind: "threat" | "blockade" | "mobility" | "material" | "initiative",
  level: "low" | "med" | "high",
  text: "..."
}
```

Damit koennen wir spaeter UI/Style getrennt von Logik halten.

---

## 15) Overlay-Design (kurz)

- Threat-Overlay: markiert konkrete Zielfelder.
- Blocked-Overlay: markiert Steine ohne Zuege (Punkte/Umrandung).
- Mobility-Overlay: Farbintensitaet pro Stein (0..n).
- Double-Threat-Overlay: markiert Felder mit 2 Muehlen.

Regel: Overlay niemals State veraendern.

---

## 16) Grenzen / Risiken

- Heuristiken koennen kurzfristig falsche "Intuition" erzeugen
  (z. B. Mobility vs. taktische Muehle).
- Darum Prioritaetsregeln strikt anwenden.
- In Endgames sind Material/Threats oft wichtiger als Connectivity.

---

## 17) Mini-Roadmap fuer die naechste Iteration

1. derive_hints (pure function) + Tests
2. Hint-UI (max 3, nach Prioritaet)
3. Blocked-Overlay (schnellster visueller Mehrwert)
4. Mobility-Overlay (Farbschema definieren)
5. Phase-spezifisches Tuning (Schwellen pro Phase)
