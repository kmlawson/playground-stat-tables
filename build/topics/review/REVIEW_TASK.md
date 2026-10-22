# Review chart views of Korea tables (English Annual Reports)

The site shows each transcribed table with an optional chart drawn automatically by `charts.js` (rules below). Your batch
file lists tables: title, chapter, columns, rows (as printed, truncated at 40 rows) and what the chart currently does
(CHART kind, X/CATEGORIES, SERIES with * = shown by default, MODE, NOT DRAWN). Find tables whose chart could be clearer or
more logical, and say how.

## Current automatic rules
- Line chart when rows (or columns) are years; series = the other axis. If years repeat with other labels, one line per label.
  Rows without a year (e.g. "Total", "Increase") are not drawn on line charts and are listed as "not drawn".
- Otherwise horizontal bars: categories = rows (total rows hidden by default, button to show), series = numeric columns.
  Default: if a total column and ≥2 part columns that add up to it exist → stacked parts with the printed total marked;
  else ≤3 columns all shown, else only the total (or first) column. Users can toggle series, sort, switch stacked/side by side,
  and split lines into separate small charts (automatic when series differ >50× in size).
- Columns that are year labels are treated as labels. Text cells, dashes, blanks, [?] are gaps.

## Principles (the site owner's, not negotiable)
These tables are historical constructions. Never propose smoothing, interpolating, filling gaps, computing per-capita
rates, merging tables or "correcting" figures. Keep printed labels and printed categories. Improvements are about
*how the printed figures are displayed*: chart type, which rows/columns form the axis, which series are shown by default,
splitting a table into two charts, excluding a mixed-in block from a chart (e.g. comparison rows for earlier years under a
province list), units that must not share an axis, percentages vs counts, etc.

Example of a problem: "Population of Provinces, End of 1936" lists 13 provinces, a Total row, then rows for 1930, 1925,
1920, 1910. The bar chart mixes the earlier-year rows with the provinces, and the 1936 total (a "total" row) is hidden while
the earlier years' totals are shown — illogical. Better: provinces as bars (stacked by nationality); the Total row plus the
1930/1925/1920/1910 rows as a separate small line/bar chart of totals over time.

## What to report
Only tables where a change would clearly help (skip ones that are fine — most are). For each, also say whether the fix is a
*general rule* (would apply to many tables — describe the detectable pattern precisely) or a *one-off* for this table.

Write `/Users/kml/shell/projects/yearbooks/japanyearbooks/stat-tables-site/build/topics/review/suggestions_<N>.json`:
`[{"key": "<slug:id>", "part": 0, "problem": "...", "suggestion": "...", "scope": "rule"|"one-off", "rule": "<pattern, if rule>"}]`
It must parse. Then reply in ≤8 lines: number of suggestions, and the 3–5 most common general patterns you saw.
Work from the batch file only. No sub-agents. Never write in /tmp. Never run scripts you did not write.
