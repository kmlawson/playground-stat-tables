# Table extraction brief — <BOOK TITLE>

<!-- Template. Copy to <BookFolder>/_work/BRIEF.md, replace every <…> placeholder, and delete
     sections that do not apply. Give each sub-agent a batch of about 30 page images and point it here. -->

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
- `./crop.sh pNNNN` → `crops/pNNNN_1.jpg`, `_2`, `_3` (three overlapping horizontal bands). Look at the
  whole page first to locate tables, then read the bands. For dense tables make tighter crops and enlarge:
  `magick full/pNNNN.jpg -crop WxH+X+Y +repage -resize 200% crops/pNNNN_c1.jpg`.
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
  `images` listing every leaf and `printed_pages` every page. If it continues past your batch, finish it from
  the next leaves. If your batch starts in the middle of a table begun earlier, check whether the previous
  batch already has it; if not, write your part with `"continued": true` and say so in your report.

## Report and saving as you go
- Write each table's JSON the moment it is finished. After each leaf, append a line to `reports/<BATCH>.md`:
  `- pNNNN (p. <printed page>): <files written | no tables — why>`. If you are cut off, the next agent must be
  able to resume from the report and the files on disk; if the report exists when you start, resume from it.
- At the end add a summary: table numbers seen per chapter (for gap checks), repeated or missing printed
  pages, excluded maps/charts/directories, every unreadable cell, every total that does not reconcile.
- Do not edit files outside `tables/`, `reports/` and `crops/`. Put helper scripts in your own scratch folder;
  never run scripts you did not write.

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
