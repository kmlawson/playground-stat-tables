# Table extraction brief — <BOOK TITLE>

<!-- Template. Copy to <BookFolder>/_work/BRIEF.md, replace every <…> placeholder, and delete
     sections that do not apply. Give each sub-agent a SHORT mission (see example/MISSION.md): 1–3 dense
     pages, 3–5 ordinary table pages, or 10–20 pages of pure prose, sized to finish in under an hour. -->

## Checklist (read first)
1. Read the images yourself — no OCR, Vision framework, `llm`/Gemini or text layer of any kind.
2. Unreadable figure → `""` + a note. Never guess; never infer a digit from a total.
3. Transcribe as printed; never correct the source. Re-add every printed total and note whether it reconciles.
4. Read tables from tight crops (≤ ~2000 px wide, ≤ ~25 rows), each with its column headings in view.
5. Note the number of rows you read for every table/part.
6. Save each table as soon as it is done; keep tool calls small; no sub-agents; helper scripts only in your
   own `crops/<MISSION>/` folder.

Working dir: `<ABSOLUTE PATH TO BookFolder>/_work`

Each file `full/pNNNN.jpg` (about <W>x<H> px; <where the scan comes from>) is ONE printed page.
`pNNNN` is the scan's page index starting at 0 (for an Internet Archive item this is the leaf number
`n` in `archive.org/details/<item>/page/n<leaf>`), not the printed page number. For two-page spreads
say so here and describe the left/right convention; for multi-part scans name files `p{part}-{leaf:04d}`.

Your job: transcribe **every table** (and every long list, see below) printed on the pages in your
batch, exactly as printed, into JSON files. Use the chapter name (e.g. "Geography") as `chapter`, and
put a sub-heading printed above an unnumbered table in `caption_extra`.

## Hard rules
1. **Read the images with your own eyes (the Read tool on image crops). Do NOT use OCR of any kind** —
   no tesseract, no Apple Vision, no `llm`/Gemini or other image-description service, no PDF text layer,
   no OCR text files that came with the scan. Transcribe what you see.
2. A figure you cannot read with confidence = **empty string `""`** in that cell, plus an entry in
   `transcriber_notes` naming the row and column. Never guess a digit: a wrong digit is worse than a blank.
   **Never use a printed total (or any arithmetic) to decide what a damaged digit is.** You may say in the
   note what the total would imply. Never write partial readings such as `"12[?]"` into a cell.
3. Where the table prints a total (row or column), add up the parts yourself (python3) and record in
   `transcriber_notes` whether it reconciles, e.g. `"Total 1,303,437: parts sum to 1,303,337 — does NOT
   reconcile (diff 100)"`. **Never correct the source.** Re-read the cells once more before recording a
   discrepancy.
4. Keep figures as printed strings: commas, decimal points, `...`, `*` footnote marks, parentheses.
   Write a printed dash as `"—"`. Keep misprints as printed and mention them in `transcriber_notes`.

## How to read
- `./crop.sh pNNNN` → `crops/pNNNN_1.jpg`, `_2`, `_3` (three overlapping horizontal bands). Use the whole
  page and the bands to **locate** tables only — do not read a table from a band that has lost its column
  headings (that is how whole columns get shifted by a row).
- Read each table from tight crops of the table itself:
  `magick full/pNNNN.jpg -crop WxH+X+Y +repage crops/pNNNN_c1.jpg` (coordinates in the full image; check its
  size with `magick identify`). Images are shown to the model shrunk to about 2000 px on the long side, so
  keep crops ≤ ~2000 px wide and ≤ ~25 rows. Enlarging (`-resize 200%`) adds no detail; use it only to look
  closely at a very small crop such as a single gutter column. On a low-resolution scan (under ~1000 px
  wide) crop tighter rather than enlarging.
- Tall table: cut it into row chunks and paste the header strip on top of each chunk
  (`magick crops/hdr.jpg crops/chunk2.jpg -append crops/chunk2h.jpg`). Wide table: vertical strips that each
  keep the row-label column.
- Figures printed out of line with their row labels (common near the gutter): count the labels and the
  figure rows, assign in order, and say so in the notes.
- Rotated (sideways) tables: rotate the crop (`-rotate 90`) and read normally.
- **Open every page in your range**, even ones you expect to be prose.
- Crops are disposable: delete your own crops when you finish. Never touch another batch's crops.

## What counts as a table
- Include: numbered or unnumbered statistical tables; lists laid out in columns with figures; administrative
  lists in columns; weights/measures and currency equivalences; comparison tables; any chart that prints its
  figures (transcribe the figures and say so).
- **Lists count too:** long lists of places, people, officials, institutions, ships, newspapers, laws, events
  etc. set out one per line, numbered or bulleted. One row per item, split into the obvious fields (Name /
  Position / Place / Date) where the entries have a regular shape, otherwise a single "Item" column. Title in
  [brackets] if none is printed.
- Exclude: running prose (even when it names many things), maps, organisation charts, graphs without printed
  figures, numbered legal clauses/articles (prose), the contents pages and the index. Note every exclusion in
  your report.
- **Directories are a separate job:** a Who's Who, a directory of firms/institutions/officials, or another long
  run of name-and-paragraph entries is recorded in your report (leaves, printed pages, what it is) and NOT
  transcribed as tables. The same for a chronology of dated events. Columnar lists inside those sections still
  count as tables.
- Give dates context: if a list or table comes from a narrative about an earlier period (e.g. a 1931 statement
  reprinted in a 1939 yearbook) and its title does not show the date, add the date in [brackets] to the title
  and a "[Context, added by the transcriber: …]" sentence at the start of `caption_extra`.

## Output — one JSON file per table
Path: `tables/<pNNNN of first page>_<n>.json`, n = 1, 2, 3… in reading order on that page. Write with
python3 `json.dump(..., ensure_ascii=False, indent=1)`.

```json
{
  "image": "p0029",
  "images": ["p0029"],
  "printed_pages": ["4"],
  "chapter": "Geography",
  "table_no": "2",
  "title": "Area of the Provinces",
  "caption_extra": "(Unit: sq. km.) — headnote printed with the title, verbatim",
  "continued": false,
  "parts": [
    {"label": null, "columns": ["Province", "Sq. km."], "rows": [["Fengtien", "75,812"], ["Kirin", "88,819"]]}
  ],
  "footnotes": ["Note: ... printed under the table, verbatim"],
  "transcriber_notes": ["Total reconciles ...", "Row 'Heiho', col 'Sq. km.': unreadable"]
}
```
- `table_no` as printed ("12", "12-A") or `null`. `title` as printed but in Title Case, or a short
  description in [brackets] if none is printed.
- `parts`: sub-sections "(A) …", "(B) …" → one part each with `label`; a simple table has one part.
- `columns`: flatten multi-level headers with " — " (e.g. `"Imports — Japan"`). Every row has exactly
  `len(columns)` cells; the first column is the row label. A sub-heading row inside a table becomes a row with
  the heading in the first cell and `""` elsewhere.
- Side-by-side layouts (the same columns printed twice across the page) → one continuous list.
- **A table running over several pages is written once**, in the file for its first page, with all rows,
  `images` listing every leaf and `printed_pages` every page. Ownership rule (lets missions run in parallel
  without duplicates): **you own every table whose first line is on one of your pages** — finish it even if
  that means reading pages beyond your range. **You do not own a continuation** at the top of your first
  page: leave it (the earlier mission owns it) and mention it in your report. The exception is a file your
  prompt explicitly tells you to "finish": load it, append what is missing, keep what is there.
- In `transcriber_notes` give the number of rows read (e.g. "Rows: 28 as printed") and the result of every
  total check.

## Report and saving as you go
- Write each table's JSON the moment it is finished. After each leaf, append a line to `reports/<BATCH>.md`:
  `- pNNNN (p. <printed page>): <files written | no tables — why>`. If you are cut off, the next agent must be
  able to resume from the report and the files on disk; if the report exists when you start, resume from it.
- At the end add a summary: table numbers seen per chapter (for gap checks), repeated or missing printed
  pages, excluded maps/charts/directories, every unreadable cell, every total that does not reconcile.
- Do not edit files outside `tables/`, `directory/`, `chronology/`, `reports/` and `crops/`. Put helper
  scripts in your own `crops/<MISSION>/` folder; apart from `./crop.sh` and `validate.py`, never run scripts
  you did not write.

## Before you stop
- [ ] Every page in your mission has a report line (pages, files written or "no tables — why").
- [ ] Every table's notes give the row count read and every total check.
- [ ] Unreadable cells listed in the notes and the report.
- [ ] `python3 validate.py` run and problems in your own files fixed.
- [ ] Your crops deleted.
- [ ] A reply of at most ~8 lines: files written, unreadable cells, totals that do not reconcile.

## Directory entries (only for a directory batch)
One JSON per leaf in `directory/<leaf>.json`:
```json
{"leaf": "p0600", "printed_pages": ["27"], "appendix": "Appendix A: Who's Who",
 "entries": [{"section": null, "name": "ABE, Isoo", "text": "M.P., b. 1865; grad. ... Addr. ...", "page": "27"}],
 "notes": ["Entry 'KATO, ...': year of birth [illegible]"]}
```
Verbatim text, line-break hyphens removed, `[illegible]` for anything unreadable. An entry that runs onto the
next leaf goes, whole, in the file for the leaf where it starts. Optional `rank` or `mark` fields are shown
after the name on the site.

## Chronology (only for a chronology batch)
One JSON per chronology in `chronology/<first leaf>.json`: `{"image", "images", "printed_pages", "chapter",
"title", "events": [{"section", "date", "text", "page"}], "notes"}`. Dates exactly as printed, with the year
added in front when the year is only given as a heading.

## This book
<Book-specific notes: footers to ignore, how chapters are titled, scan quirks (repeated or out-of-order
leaves, fold-outs, missing pages), where the directories and chronologies are, anything the batches should
hand over to each other.>
