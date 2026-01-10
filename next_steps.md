1️⃣ Sidebar – Engine (Search)
Depth
Depth = 2


Bedeutung

Maximale Suchtiefe in Halbzügen (Ply)

2 = mein Zug → Gegnerzug

Logik

Bei Mühle sehr phasenabhängig:

Placing-Phase: Tiefe 2–4 sinnvoll

Moving/Flying: Tiefe 6–10 relevant

Didaktik

Niedrige Tiefe = „oberflächliches Denken“

Hohe Tiefe = „vorausschauendes Denken“

✅ Empfehlung

Behalte das Feld

Beschrifte es evtl. zusätzlich als
„Vorausdenken (Ply)“ oder „Rechentiefe“

Time (ms, 0=off)
Time = 0


Bedeutung

Zeitlimit für Iterative Deepening

0 = Tiefe ist der einzige Abbruch

Logik

Zeit > Tiefe ist langfristig besser für UX

Besonders wichtig für Analyse-Modus

Didaktik

Ermöglicht: „Was sieht die Engine in 500 ms vs in 2 Sekunden?“

✅ Empfehlung

Gut so

Später evtl. Presets:

Schnell

Standard

Tiefgehend

Top-N
Top-N = 5


Bedeutung

Wie viele Züge mit Bewertung angezeigt werden

Logik

Grundlage für:

Vergleich

Blunder-Erkennung

Lernfeedback

Didaktik

Essenziell

Lernen entsteht durch Alternativen, nicht nur Best Move

✅ Empfehlung

3–5 optimal

UI-seitig evtl. „Erweiterte Ansicht“

Use-TT Toggle
Use-TT = ON/OFF


Bedeutung

Aktiviert Transposition Table

Logik

Verhindert doppeltes Rechnen identischer Stellungen

Besonders stark bei Mühle (viele Transpositionen + Symmetrien)

Didaktik

Optional sichtbar

Mehr für „Advanced / Debug“

✅ Empfehlung

Standard: ON

Tooltip: „Zwischenspeicher für bereits analysierte Stellungen“

Cache TTL / Cache Size
TTL = 2s
Size = 8


Bedeutung

UI-/Analyse-Cache, nicht Engine-TT

Verhindert Neuberechnung bei kleinen UI-Aktionen

Logik

Rein technisch

Keine Spielrelevanz

Didaktik

Für Lernende irrelevant

⚠️ Empfehlung

Als Developer-Option kennzeichnen

Oder in „Advanced / Debug“-Sektion verschieben

2️⃣ Eval Weights – das Herz der Logik

Das ist der wichtigste Teil für dein Verständnis.

Grundprinzip

Jede Metrik liefert einen Rohwert, der mit einem Weight multipliziert wird.

score = Σ (feature_value × weight)

Einzelmetriken – verständlich erklärt
Material (10.0)

Was

Differenz der Steine auf dem Brett (und evtl. in Hand)

Warum

Fundamentaler Vorteil

In Mühle extrem entscheidend

Didaktik

Sehr intuitiv

„Mehr Steine = besser“

✅ Sehr gut

Mills (5.0)

Was

Anzahl bestehender Mühlen

Warum

Direkter taktischer Vorteil

Erzwingt Entfernen

Didaktik

Klar verständlich

Sollte visuell hervorgehoben werden

⚠️ Hinweis

Manche Engines gewichten Mill-Formation höher als existierende Mills
(weil bestehende Mills oft „tot“ sind)

Open Mills (2.0)

Was

2 Steine in Linie + freies Feld

Warum

Drohpotenzial

Vorbereitung wichtiger als Ausführung

Didaktik

Sehr gut erklärbar

„Du drohst eine Mühle“

✅ Sehr wichtig für Lernmodus

Mobility (1.0)

Was

Anzahl legaler Züge

Warum

Eingeschränkte Mobilität = strategischer Nachteil

Führt zu Blockaden / Verlust

Didaktik

Weniger intuitiv

Muss erklärt werden („keine guten Züge mehr“)

✅ Behalten, evtl. Tooltip

Threats (Mill-in-1) (2.0)

Was

Anzahl Züge, die sofort eine Mühle erzeugen

Warum

Akute taktische Gefahr

Didaktik

Extrem wichtig

Sollte auch ohne Score als Warnung erscheinen

✅ Sehr gut

Blocked Opponent (0.5)

Was

Anteil gegnerischer Steine ohne legale Züge

Warum

Blockade ist Gewinnmechanismus

Didaktik

Fortgeschritten

Gut für Endspieltraining

⚠️ UI evtl. erst später prominent

Double Threats (1.0)

Was

Zwei unabhängige Mill-Drohungen

Warum

Erzwingt Materialgewinn

Didaktik

Sehr starkes Lernkonzept

Muss explizit benannt werden

✅ Sehr gut

Connectivity (0.5)

Was

„Qualität“ der besetzten Felder (Nachbarschaften)

Warum

Gute Felder → mehr Flexibilität

Didaktik

Abstrakt

Nur mit Erklärung sinnvoll

⚠️ Nicht überbetonen

Initiative (Strategic / Tactical)
0.00 / 0.00


Was

Wer zwingt den Spielverlauf?

Warum

Sehr mächtig, aber schwer korrekt zu messen

Didaktik

Komplex

Nur sinnvoll, wenn sauber implementiert

✅ Gut, dass es aktuell deaktiviert ist

3️⃣ Why Panel – Klassifikation
Best ≤ 0.05
Good ≤ 0.50
Inaccuracy ≤ 1.50
Mistake ≤ 3.00
Blunder > 3.00


Logik

loss = best_score - move_score

Klassische Schach-Engine-Logik

Didaktik

Sehr gut

Menschen verstehen Kategorien besser als Zahlen

✅ Sehr gute Wahl

💡 Empfehlung

Im UI immer Score + Kategorie

Kategorie farblich dominant

4️⃣ Analysebereich – aktueller Zustand (Startposition)

Dein Output ist logisch korrekt.

Warum alles 0.00 ist

Keine Steine → keine Struktur

Material ist gleich

Keine Mills, keine Mobility, keine Threats

Kandidatenzüge (Heuristik)
P:a7: 10.00
...


Das kommt von:

material = +1 Stein × 10.0

Wichtig

Das ist kein Search-Ergebnis, sondern heuristische Vorbewertung

✅ Sehr gut getrennt

5️⃣ Engine Output (Search)
Depth=2, Nodes=80
TT hits/misses=18/6


Interpretation

Sehr effizient

TT greift

Ordnung der Züge funktioniert

Best Move + PV
Place d6 ; Place b4


Logik

Engine sagt: egal wo du startest, Gegner antwortet symmetrisch

Das ist korrektes Verhalten in leerer Stellung.

6️⃣ Top Moves + Breakdown

Das ist der stärkste Teil deiner App.

Beispiel:

material: 10.00
connectivity: 2.00


Was hier passiert

Jeder Zug wird lokal erklärt

Unterschiede werden als Diff angezeigt

🎯 Das ist exakt das, was eine Lern-App „superior“ macht

7️⃣ Brauchst du einen fortgeschritteneren Analyse-State?

Kurz: ja – aber nicht zwingend jetzt

Für dein Verständnis:

Startposition → erklärt Mechanik

Mittelspiel-Stellung → erklärt Entscheidungen

💡 Empfehlung

Erstelle 2–3 feste Teststellungen:

erste offene Mühle

Blockade-Situation

Flying-Endspiel

Die brauchst du später sowieso für Regressionstests.

8️⃣ Meta-Fazit (wichtig)

Du hast aktuell:

eine echte Engine

saubere Heuristiken

erklärbare Bewertungen

sinnvolle UI-Metriken

klare Lernklassifikation

Das ist weit über Prototyp-Niveau.

Dein nächster Fokus sollte nicht sein:

„mehr KI“

sondern:

„Welche dieser Informationen sind für den Menschen wirklich lernwirksam – und wie zeige ich sie?“

Wenn du willst, können wir als nächsten Schritt:

das Analyse-UI didaktisch „aufräumen“

oder eine konkrete Lern-Session-UX (z. B. Find the Best Move) designen

oder gezielt überflüssige Metriken identifizieren, die du intern behältst, aber UI-seitig ausblendest