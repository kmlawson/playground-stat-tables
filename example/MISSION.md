# Mission template — short, bounded transcription jobs

<!-- Copy to <BookFolder>/_work/MISSION.md. The orchestrating session gives each sub-agent a prompt of a
     few lines naming its mission (see "Prompt" below) and points it at BRIEF.md + this file. -->

You have ONE small mission: the page(s) named in your prompt, nothing else. Target: finish in under an
hour. Read `BRIEF.md` (rules and JSON formats) first; this file only narrows your scope.

## Scope
1. **You own** every table / chronology / directory list whose first line is printed on one of your pages.
   Write each one completely, reading ahead into later pages as far as needed.
2. **You do not own** a continuation at the top of your first page (a table begun earlier). Leave it and
   say so in your report. Exception: a file your prompt tells you to "finish" — load it, append the
   missing rows/parts, keep everything already there, update `images` and `printed_pages`.
3. If a file for one of your pages already exists and you were not told to finish it, check it against
   the image and only add what is missing; say so in its notes.

## Output
- JSON files exactly as in `BRIEF.md`.
- Your own report: `reports/M_<first leaf>.md` — one line per page (printed page, files written or
  "no tables — why"), unreadable cells, totals that do not reconcile.
- Helper scripts only in `crops/M_<first leaf>/`; delete your crops at the end.

## Before you stop
- [ ] Every page has a report line.
- [ ] Every table: rows counted and total checks in `transcriber_notes`.
- [ ] `python3 validate.py` run; your own problems fixed.
- [ ] Reply in ≤ 8 lines: files, unreadable cells, non-reconciling totals.

## Prompt (what the orchestrator sends)
```
<Book> extraction — ONE short mission: <leaf(s)> (<printed pages>, <chapter>).
Read _work/BRIEF.md and _work/MISSION.md in <abs path>/_work and follow them.
[FINISH tables/<file>.json (<table>): it stops at <row/item>; append the rest from <page>.]
Write every table that starts on <leaf(s)>; read ahead into <next leaf> only to finish the last one.
Match the structure of <existing example file> if the section has a house style.
Read the images with your own eyes — NO OCR/Vision/llm. Unreadable = "" + note.
No sub-agents. Aim for < 45 min. Report: reports/M_<leaf>.md.
```
