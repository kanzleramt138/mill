# Engine Evaluation Features

## 1) Sidebar: Engine (Search)

### Depth
- Default: 2
- Bedeutung: Maximale Suchtiefe in Halbzuegen (Ply). 2 = mein Zug -> Gegnerzug.
- Logik: In Muehle stark phasenabhaengig:
  - Placing: Tiefe 2-4 sinnvoll
  - Moving/Flying: Tiefe 6-10 relevant
- Didaktik: Niedrige Tiefe = oberflaechliches Denken, hohe Tiefe = vorausschauendes Denken.
- Empfehlung: Feld beibehalten, optional Label "Vorausdenken (Ply)" oder "Rechentiefe".

### Time (ms, 0=off)
- Default: 0
- Bedeutung: Zeitlimit fuer Iterative Deepening. 0 = Tiefe ist der einzige Abbruch.
- Logik: Zeit > Tiefe ist langfristig besser fuer UX, besonders im Analyse-Modus.
- Didaktik: Vergleich "Was sieht die Engine in 500 ms vs. 2 s?"
- Empfehlung: Presets spaeter erwagen (Schnell / Standard / Tiefgehend).

### Top-N
- Default: 5
- Bedeutung: Wie viele Zuege mit Bewertung angezeigt werden.
- Logik: Grundlage fuer Vergleich, Blunder-Erkennung, Lernfeedback.
- Didaktik: Lernen entsteht durch Alternativen, nicht nur Best Move.
- Empfehlung: 3-5 optimal, optional "Erweiterte Ansicht".

### Use-TT Toggle
- Default: ON
- Bedeutung: Aktiviert Transposition Table.
- Logik: Verhindert doppeltes Rechnen identischer Stellungen. In Muehle besonders stark.
- Didaktik: Eher Advanced/Debug.
- Empfehlung: Standard ON, Tooltip: "Zwischenspeicher fuer bereits analysierte Stellungen".

### Cache TTL / Cache Size
- Default: TTL 2s, Size 8
- Bedeutung: UI-/Analyse-Cache, nicht Engine-TT.
- Logik: Reine Performance, keine Spielrelevanz.
- Didaktik: Fuer Lernende irrelevant.
- Empfehlung: Als Developer-Option kennzeichnen oder in "Advanced/Debug" verschieben.

## 2) Eval Weights - Das Herz der Logik

### Grundprinzip
- Jede Metrik liefert einen Rohwert und wird mit einem Gewicht multipliziert.
- Formel: score = sum(feature_value * weight)

### Material (10.0)
- Was: Differenz der Steine auf dem Brett (und ggf. in Hand).
- Warum: Fundamentaler Vorteil, in Muehle extrem entscheidend.
- Didaktik: Intuitiv ("Mehr Steine = besser").
- Empfehlung: Sehr gut so.

### Mills (5.0)
- Was: Anzahl bestehender Muehlen.
- Warum: Direkter taktischer Vorteil, erzwingt Remove.
- Didaktik: Klar verstaendlich, visuell hervorheben.
- Hinweis: Einige Engines gewichten Mill-Formation hoeher als bestehende Mills.

### Open Mills (2.0)
- Was: 2 Steine in Linie + freies Feld.
- Warum: Drohpotenzial, Vorbereitung wichtiger als Ausfuehrung.
- Didaktik: Sehr gut erklaerbar ("Du drohst eine Muehle").
- Empfehlung: Wichtig fuer Lernmodus.

### Mobility (1.0)
- Was: Anzahl legaler Zuege.
- Warum: Eingeschraenkte Mobilitaet = strategischer Nachteil.
- Didaktik: Weniger intuitiv, erklaeren ("keine guten Zuege mehr").
- Empfehlung: Behalten, evtl. Tooltip.

### Threats (Mill-in-1) (2.0)
- Was: Zuege, die sofort eine Muehle erzeugen.
- Warum: Akute taktische Gefahr.
- Didaktik: Extrem wichtig, auch als Warnung ohne Score.
- Empfehlung: Sehr gut.

### Blocked Opponent (0.5)
- Was: Anteil gegnerischer Steine ohne legale Zuege.
- Warum: Blockade ist Gewinnmechanismus.
- Didaktik: Fortgeschritten, gut fuer Endspieltraining.
- Empfehlung: UI spaeter prominent machen.

### Double Threats (1.0)
- Was: Zwei unabhaengige Mill-Drohungen.
- Warum: Erzwingt Materialgewinn.
- Didaktik: Starkes Lernkonzept, explizit benennen.
- Empfehlung: Sehr gut.

### Connectivity (0.5)
- Was: Qualitaet der besetzten Felder (Nachbarschaften).
- Warum: Gute Felder -> mehr Flexibilitaet.
- Didaktik: Abstrakt, nur mit Erklaerung sinnvoll.
- Empfehlung: Nicht ueberbetonen.

### Initiative (Strategic / Tactical) (0.00 / 0.00)
- Was: Wer zwingt den Spielverlauf?
- Warum: Sehr maechtig, aber schwer korrekt zu messen.
- Didaktik: Komplex, nur sinnvoll wenn sauber implementiert.
- Empfehlung: Gut, dass es aktuell deaktiviert ist.

## 2b) Status-Matrix (Ist-Stand)

| Metrik | Implementiert | UI Weight | Tests | Phase-Scaling | Notes |
| --- | --- | --- | --- | --- | --- |
| Material | ja | ja | nicht explizit | nein | Basis-Metrik |
| Mills | ja | ja | nicht explizit | nein | evtl. Gewicht vs. Open Mills pruefen |
| Open Mills | ja | ja | nicht explizit | nein | wichtig fuer Lernmodus |
| Mobility | ja | ja | nicht explizit | nein | Overlay-Kandidat |
| Threats (Mill-in-1) | ja | ja | nicht explizit | nein | Hints bereits vorhanden |
| Blocked Opponent | ja | ja | nicht explizit | nein | Overlay-Kandidat |
| Double Threats | ja | ja | teilweise (Tier-2 Tests) | nein | Hints bereits vorhanden |
| Connectivity | ja | ja | teilweise (Tier-2 Tests) | nein | Tuning offen |
| Initiative (Strategic) | ja (weights=0) | ja | teilweise (Overlap-Test) | nein | Tuning offen |
| Initiative (Tactical) | ja (weights=0) | ja | teilweise (Overlap-Test) | nein | Tuning offen |

### Ableitung (naechste Schritte)
- Explizite Tests fuer Tier-1 Metriken ergaenzen (Material/Mills/Open Mills/Mobility/Threats/Blocked).
- Eval-Tuning + Phasen-Skalierung definieren (v. a. Initiative, ggf. Mobility).
- UI-Feinschliff: tooltips/Legenden pro Metrik (Why-Panel + Weights).
- Optional: Board-Overlay fuer Mobility/Blocked.

## 3) Why Panel - Klassifikation

### Schwellenwerte
- Best <= 0.05
- Good <= 0.50
- Inaccuracy <= 1.50
- Mistake <= 3.00
- Blunder > 3.00

### Logik
- loss = best_score - move_score
- Klassische Schach-Engine-Logik.

### Didaktik
- Kategorien sind fuer Menschen besser als reine Zahlen.
- Empfehlung: Im UI immer Score + Kategorie, Kategorie farblich dominant.

## 4) Analysebereich - aktueller Zustand (Startposition)

### Warum alles 0.00 ist
- Keine Steine -> keine Struktur.
- Material ist gleich.
- Keine Mills, keine Mobility, keine Threats.

### Kandidatenzuege (Heuristik)
- P:a7: 10.00
- ...

### Wichtig
- Das ist kein Search-Ergebnis, sondern heuristische Vorbewertung.
- Empfehlung: Klare Trennung beibehalten.

## 5) Engine Output (Search)

### Beispiel
- Depth=2, Nodes=80
- TT hits/misses=18/6

### Interpretation
- Effizient, TT greift, Move-Ordering funktioniert.

### Best Move + PV
- Place d6 ; Place b4

### Logik
- In leerer Stellung antwortet der Gegner symmetrisch.
- Das ist korrektes Verhalten.

## 6) Top Moves + Breakdown

### Beispiel
- material: 10.00
- connectivity: 2.00

### Bedeutung
- Jeder Zug wird lokal erklaert.
- Unterschiede werden als Diff angezeigt.
- Das ist der Kern einer Lern-App.

## 7) Fortgeschrittener Analyse-State?

### Kurz: Ja, aber nicht zwingend jetzt

### Empfohlene feste Teststellungen
- Erste offene Muehle
- Blockade-Situation
- Flying-Endspiel

Diese Stellungen brauchst du spaeter ohnehin fuer Regressionstests.

## 8) Meta-Fazit

Du hast aktuell:
- eine echte Engine
- saubere Heuristiken
- erklaerbare Bewertungen
- sinnvolle UI-Metriken
- klare Lernklassifikation

Naechster Fokus sollte nicht "mehr KI" sein, sondern:
- Welche Informationen sind fuer Menschen wirklich lernwirksam, und wie zeigt man sie?

Moegliche naechste Schritte:
- Analyse-UI didaktisch aufraeumen
- konkrete Lern-Session-UX ("Find the Best Move") designen
- ueberfluessige Metriken identifizieren und UI-seitig ausblenden
