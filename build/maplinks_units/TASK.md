# Map links: columns printed in thousands (agent brief)

"View as Map" sends a table's figures to the Japanese Empire map exactly as printed. Where a column is printed in
thousands (or millions, or 萬), the map then shows e.g. "Japan Proper · 72,223" for a population of 72 million, which
confuses readers. The fix: for each such column, a multiplier, so the map receives the full number (72,223,000).

`build/maplinks_units/candidates.txt` lists 206 map-linked tables whose title, caption, notes or headings mention a
unit of thousands/millions. For each table: `### book:table | units=…`, `TABLE:` title | caption | part label | notes,
then every column the map receives: `col K: heading | en= | kind= unit= | e.g. [first values]`.

For each table decide, column by column, the multiplier that turns the printed figure into the full figure in its
base unit:
- `1000` when that column's figures are in thousands: its heading says so (千圓, 千人, 千貫, 千石, 千本, (1,000 yen),
  "Unit: 1,000", "in thousands"), or the table-level unit (title/caption: (單位千圓), (Unit: 1,000), "1,000 piculs")
  covers it. A table-level unit covers only the columns it names: "(單位數量千瓩, 價額千圓)" covers quantity and value
  columns, not counts of factories or workers; "(單位千圓)" covers money columns, not a count of companies or persons.
  When a generic table-level unit ("Unit: 1,000") is stated, it covers every figure column except obvious exceptions
  (ratios, percentages, densities, per-head figures, counts that are plainly whole numbers of units like factories).
- `1000000` for millions (百萬圓, million yen), `10000` for 萬.
- Nothing (leave it out) for: ratios "per 1,000" (人口千ニ付, ‰), percentages, densities, indexes, per-capita values,
  averages, and any column you are not sure about. **Only when sure** — a wrong multiplier is worse than none.
- Yields per unit area printed in 千貫 etc. are in thousands of that unit too: give 1000.
- Use the sample values as a check (a population in thousands is 1,000–80,000; in persons it is far larger), never as
  the only reason.

Write `build/maplinks_units/mult.json`:
```json
{"japan-1942-43:p0066_1": {"cols": {"3": 1000, "4": 1000, "5": 1000}, "why": "estimated population columns say Unit: 1,000"},
 "japan-tokei-1935:p0073_1": {"cols": {"15": 1000, "16": 1000, "17": 1000}, "why": "yields of 甘藷, 馬鈴薯, 大根 in 千貫 per are"}}
```
Keys of "cols" are the `col K` numbers. Include a table only if at least one column gets a multiplier; for tables
where nothing applies, list them in `build/maplinks_units/none.txt` (one `book:table — reason` per line).
Write the file as you go and check it parses. Work only from candidates.txt and, if needed, `data/<slug>.json`;
never open scans; no OCR; no git; edit no other file.

When done reply with only: tables with multipliers, columns given multipliers, tables with none, and anything
you could not decide.
