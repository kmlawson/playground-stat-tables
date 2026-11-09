# Population page — date check (agent brief)

The site *Old Tables of East Asia* has a **Population** page that gathers population figures from transcribed tables.
A short **spec** per table (format: `build/finders/population/TASK.md`, read its "Spec format" section first) says
which cells hold figures, for which place and **date**. A script copies the figures exactly as transcribed.

Your job: check the **date** each spec gives its figures. The page must show a figure under the year it was **measured**
(census day, end of year, survey date …), not the year the book was **published**. Correct the specs that are wrong.

## Ground rules

- Work only from the batch file and the transcribed JSON: `data/<slug>.json` (a list of tables; find `"id"`), the
  English layer `build/translations/<slug>.json`, the printed contents `data/<slug>-toc.json`. You may look at the
  neighbouring tables of the same book (same page or chapter) when a heading or note there dates the figures.
- **Never open scans or images. Never use OCR** or any tool that reads images. Do not re-read or change any figure.
- Change no file except your own two output files. Do not edit specs in place.

## Input

`build/finders/population/work/datecheck/<AGENT>.txt`. Per table: `### slug:id | book (edition year) | chapter | page`,
`WHY:` the reason it is listed, title/English title, caption, context, footnotes, transcriber notes, each part's
columns and row labels, `SPEC:` the current spec, `CURRENT DATES:` the dates the figures now get.

Reasons a table is listed:
1. **no date in spec** — the page shows the edition year as "date not stated". Look for a date the table *does* state
   (title, caption, column or row heads, footnotes, part labels, a heading or note in a neighbouring table, the chapter).
2. **plain year at or just before the edition year** — often right, but check the year comes from the table and not
   from the book's year. E.g. a 1935 yearbook table headed 昭和八年末 is `1933-12-31`, not 1935.
3. **same figure dated differently elsewhere** — another table prints the same figure with another year. Decide which
   date the table in your batch states. If it states none and the other tables state one explicitly for exactly the
   same figures (same source, same totals), you may use that date with a note `"n": "date as printed in <slug:id>"`.
   If the table in your batch states its own date clearly, it stays, even if it disagrees — the page shows both.

## Rules for dates

- Use the most precise date printed: `"1930-10-01"` (census), `"1933-12-31"` (年末 / end of year), `"1934-06-30"`, or
  `"1933"` when only the year is given. Era years: 昭和 n = 1925+n, 大正 n = 1911+n, 明治 n = 1867+n, 民國 n = 1911+n,
  康德 n = 1933+n, 大同 n = 1931+n.
- Different columns or rows can have different dates: give each column its `d`, or use `rd` / `rows: "dates"` /
  `rows: "cells"` as `TASK.md` describes. Fix row-to-year misalignments in `rows: "dates"` specs.
- **Never guess.** When the table and its neighbours state no date, leave the date empty (the page then says "date not
  stated"); do not substitute "the year before the edition" or a round number. A clue that is only probable is not
  enough.
- Keep everything else in the spec as it is (places, columns, groups, notes) unless it is plainly broken; keep `"fp"`.

## Output

1. `build/finders/population/work/datecheck/<AGENT>.out.json` — a JSON **list**, one object per table you change:
   `{"t": "<slug:id>", "spec": {<the full corrected spec, same format as SPEC, with "t" and "fp">}, "why": "<10–25 words:
   where the date is printed>"}`. Tables you leave alone are not listed. Write the file early and add to it as you go
   (work is never lost); check it parses: `python3 -c "import json,sys;json.load(open(sys.argv[1]))" FILE`.
2. `build/finders/population/work/datecheck/<AGENT>.report.md` — counts (checked, changed, left with no date, left as
   is), and a short list of tables you could not decide, with why.

Reply with only the counts and the undecided list.
