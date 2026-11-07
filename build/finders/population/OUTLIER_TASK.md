# Population page — suspicious figures (agent brief)

The Population page takes figures out of the transcribed tables by the specs in `build/population/work/specs/*/b*.json`
(format: `build/population/POP_TASK.md`). `build/population/work/outliers_ranked.txt` lists tables with figures far
from the other figures for the same place, count and group (under 1/4 or over 4× the median within 15 years), worst
first. Most big gaps are spec mistakes; some are real (a fast-growing group, a city proper vs. a wider area, a
misprint in the book).

For each table in the list, from the top, open its spec and the table in `data/<slug>.json` and decide:

- **Spec mistake** — wrong column, a ratio/percentage/density/index column read as people, households read as people,
  a group read as `all` (e.g. Japanese residents only), figures printed in thousands without `mult`, a mis-dated column,
  a total row named as the wrong place, a part-of-city row named as the city. → write a corrected spec for the whole
  table (same format; it replaces the old one), or `{"t": "...", "skip": "reason"}` if the table cannot be read right.
- **Real or printed that way** (the book prints it; the place or definition genuinely differs) → leave it. A misprint in
  the book stays as printed: never change a figure, never fill a date the table does not give, never decide a year
  from a matching total.

Write `build/population/spec_fixes.json`: a JSON list of corrected specs (one per table you fix). Write it as you go
and check it parses. Work only from the specs and `data/<slug>.json`; never open scans or images; never use OCR.
Do not edit any other file (scratch only in `build/population/work/outlier_scratch/`). You can re-run
`python3 build/population/check.py` (it rewrites `work/outliers.txt`, unranked) to see whether a fix worked.

Go through at least the first 150 tables of the ranked list. When done, reply with only: tables looked at, specs
fixed, tables skipped, and the kinds of mistakes found (one line each).
