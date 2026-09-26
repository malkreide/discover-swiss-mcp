# PROBE_QUERY — was `searchText` versteht

Datum: 2026-09-26 · Project `dsod-content` · Skript `probes/probe_query_syntax.py` · 26 Calls · ausgeführt vom Maintainer mit eigenem Key; die Werte in `probe_query_out/results.json` sind aus der Konsolenausgabe übertragen (die Sandbox erreicht `api.discover.swiss` nicht).

## Anlass

Audit FID-005: Die Tool-Beschreibung von `search` behauptete eine Abgleichsgranularität («ganze Wörter»), die nie gemessen war. Die P5-Korrektur ersetzte das durch «ungetestet» — ehrlich, aber für das Modell nutzlos. Die Spezifikation sagt nur «search for contained string by the searchable fields», ohne Abfragesprache.

## Messung

Jeder Fall zweimal: `searchFields` weggelassen (alle Felder, Tool-Default `match='all'`) und `searchFields=name`. Wert ist `count`.

| Fall | `searchText` | alle Felder | nur Name |
|---|---|---:|---:|
| Ganzes Wort (Referenz) | `Landesmuseum` | 52 | 7 |
| Kleinschreibung | `landesmuseum` | 52 | 7 |
| Präfix | `Landesmus` | 0 | 0 |
| Wildcard `*` | `Landesmus*` | 0 | 0 |
| Wildcard `?` | `Landesmuse?m` | 0 | 0 |
| Fuzzy `~` | `Landesmusem~` | 0 | 0 |
| Zwei Wörter | `Landesmuseum Zürich` | 13 | 1 |
| In Anführungszeichen | `"Landesmuseum Zürich"` | 13 | 1 |
| `AND` | `Landesmuseum AND Zürich` | 0 | 0 |
| `OR` | `Landesmuseum OR Kunsthaus` | 0 | 0 |
| Minus | `Landesmuseum -Shop` | 4 | 1 |
| Wortteil eines Kompositums | `museum` | 451 | 128 |
| Umlaut gefaltet | `Zurich` | 615 | 176 |

Kein Fall lieferte einen Fehler (HTTP 400).

## Lesart

1. **Gross-/Kleinschreibung spielt keine Rolle** (52 = 52).
2. **Nur ganze Wörter.** Das Präfix `Landesmus` findet nichts.
3. **`*`, `?` und `~` sind keine Operatoren.** Jede Variante liefert 0 statt der 52 des ganzen Worts — still, ohne Fehler.
4. **Mehrere Wörter müssen alle vorkommen** (13 < 52).
5. **Anführungszeichen ändern nichts** (13 = 13). Ob sie eine Phrase erzwingen würden, lässt sich nicht trennen, weil schon die Wortfolge ohne Anführungszeichen 13 liefert; sicher ist nur: Sie verengen nicht zusätzlich.
6. **`AND` und `OR` sind keine Operatoren.** Beide liefern 0; `OR` erweitert nicht, sondern verlangt offenbar das Wort «OR» selbst.
7. **`-` schliesst nicht aus.** `Landesmuseum -Shop` liefert 4 statt ≤ 52 mit Ausschluss — es verengt wie ein zusätzliches Pflichtwort.
8. **Nicht entschieden:** Ob ein Wortteil eines Kompositums trifft (`museum` in «Landesmuseum»), und ob `Zurich` auch «Zürich» findet. `museum` 451 und `Zurich` 615 zeigen nur, dass es Treffer gibt, nicht welche. Dafür braucht es einen Vergleich über Identifikatoren, nicht über Zählwerte.

## Konsequenz

- Die `search`-Beschreibung und die Feldbeschreibung von `query` nennen die gemessenen Regeln (Punkte 1–7) und benennen Punkt 8 als offen.
- Liefert eine Anfrage mit `*`, `?`, `~`, `AND`, `OR`, `-Wort` oder Anführungszeichen nichts, beginnt der `hint` mit dem Hinweis auf die nicht verstandene Syntax (`tools.query_syntax_note`). Ein Bindestrich im Wort («Rhein-Falls») und Namen wie «Andorra» lösen ihn nicht aus.
- Der Default `match='all'` bleibt: Er findet 52 statt 7 Objekte und die Beschreibung sagt, dass die Zahl auch Erwähnungen enthält.
