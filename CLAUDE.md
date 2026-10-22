# CLAUDE.md — East Asian statistical tables site

Static site of statistical tables (and directories) transcribed from yearbooks and handbooks on Japan, Korea,
Taiwan, Manchuria and China — in English, Japanese or both. The transcriptions (JSON) live **outside** this repo
in each book's `_work/` folder next to it; `build/build_site.py` regenerates everything here from them.
This file is the authoritative process overview (updated 2026-10-07). `build/example/` holds the templates
(`BRIEF.md`, `MISSION.md`) and git/merge details (`guidance.md`).

## Hard rules (every book, every sub-agent prompt)

- **No OCR, ever.** Every figure is read by the model from image crops with its own eyes. No tesseract, Apple
  Vision, `llm`/Gemini, PDF text layers, OCR files, or pixel/darkness/stroke-counting scripts. Cropping,
  zooming and contrast for the agent's own eyes are fine. Say this in every sub-agent prompt.
- **Never guess.** Transcribe as printed, misprints included; re-add every printed total and note whether it
  reconciles. A wrong digit is worse than a blank.
- **Two kinds of empty cell.** Empty *in the original* = `""`; could not read = `"[?]"` (whole cell) plus a
  transcriber note naming row and column. Never `"12[?]"`; `[?]` inside longer text marks an unreadable
  character. New books get `"blank_marking": true` (red hatching for `[?]`).
- **A printed total never decides a digit — two narrow exceptions (user decisions):**
  - *一/二/三 grouping* (Japanese kanji numerals): when the only doubt is how a stack of 一/二/三 strokes groups
    (三 vs 二一 vs 一二; 二 vs 一一), write the candidates down, and if exactly one makes a printed row or column
    total reconcile, use it.
  - *3 vs 8* (Western figures): when a digit is ambiguous only between 3 and 8 and exactly one reading makes a
    printed total reconcile, use it.
  - In both cases every other cell in that sum must be read with confidence; never chain; only printed sums,
    sub-totals, balances or %-to-100 count (not averages, ratios, prose or other tables); and every such cell is
    listed in the table's `transcriber_notes` with candidates and total. Otherwise the cell is `"[?]"`.
- **Opus for reading.** Model tests: on a dense vertical-numeral table (統監府統計年報 第一〇六表) Opus 5.5 scored
  91–100% per reading, Sonnet 5.5 98.3% (slower, more tokens), Haiku 4.5 0% (gave up). On 朝鮮年鑑 1925 Opus also
  clearly beat Sonnet. Use Opus agents, at most 10 at a time (the user's limit).
- **Privacy.** Nothing identifying the user in commits, request headers (User-Agent/From), file metadata or
  pages. Descriptive, non-identifying User-Agent for downloads.

## Workflow for a book

1. **Get the scan.** `ia download` (Internet Archive) or the user's PDF (often NDL, on the Oma drive). Book folder
   `<Name_Year>/` next to this repo; work in `<Name_Year>/_work/`. Extract page images to `full/pNNNN.jpg`
   (`pdfimages -j` for the original JPEGs; render at 300 dpi only for non-JPEG pages; JP2 zips via `magick`).
   `pNNNN` = PDF page / scan leaf, 1-based (keep a `build/leafmaps/<slug>.json` if the online viewer counts
   differently). Make 1600–1800 px copies in `plan/`.
2. **Contact sheets.** 8 images per sheet, 4×2, each labelled with its file name (`magick montage … -label pNNNN`)
   in `sheets/`. Survey agents (Opus, ~8–16 sheets each, `plan/SHEET_SURVEY.md`) list only the images with tables,
   lists, charts with figures or directories, one line each: `pNNNN | pp. | START/CONT | kind | titles | ENDS/RUNS-ON`,
   plus skipped runs (contents, index, ads, prose) and missing/duplicated pages. Only those pages are read later.
   **Transcribe the printed contents (step 9) before the survey**, and give each survey agent the contents entries
   for its stretch of pages: it also writes `headings_<x>.json` (`{"<toc index>": "pNNNN"}`) for every listed
   section heading it can see on the sheets — no extra pass over the pages.
3. **Brief.** Copy and adapt `BRIEF.md` (rules, JSON format, the book's "This book" section: language, numerals,
   chapter naming, page numbering, spreads/RTL, units) and `MISSION.md`; `prompt.py` + `next.sh` +
   `missions.json` drive the missions; `validate.py` checks files.
4. **Missions.** Built from the survey lines: ~3–6 images per mission (3 spreads for dense vertical Japanese
   tables, 4–6 single pages for English tables), never splitting before a `CONT` page; a mission whose last table
   runs on is told to read into the next image, the next mission is told to skip that continuation. Directory or
   Who's Who pages get separate DIRECTORY missions (`directory/<leaf>.json`); columnar lists are tables.
   Run on a rolling basis, ≤10 Opus agents; each mission: report in `reports/<MID>.md`, crops and helper scripts
   only in `crops/<MID>/`, never anything in `/tmp`. Mission ids/status in `missions.json`; `./next.sh <done-MID>`
   marks one done and prepares the next prompt. Reply to the user per mission only "N done, M left".
5. **Follow-ups (FIXES.md).** Log from mission reports: tables nobody owns, duplicates, orphan fragments whose
   first page is missing, and every cell an agent *changed after a total check flagged it*. No 10% random check
   pass (the user judged its yield too low).
6. **Blind verification.** (a) Cells changed after a total check, and total mismatches that look like one-digit
   misreads, are re-read by an agent that sees only table/row/column (`BLIND_TASK.md`, `blind/`), never the
   values; agreeing readings stand. (b) The hardest tables (tiny/compressed type, many `[?]` or large mismatches)
   get a full independent second transcription; every disagreeing cell goes to a third reader shown both
   candidates: agreement with one → use it; three different readings or unsure → `"[?]"`. Keep the first
   version (`blind/*.first.json`) and note every change in the table. (c) Books with many `[?]` (faint print):
   a re-read pass over the `[?]` cells only (`REREAD_TASK.md`).
7. **Normalise** chapter names (one per printed chapter, numbered as printed), titles, duplicate files.
8. **English layer for non-English books** (Korea/Japanese books): `build/translations/<slug>.json` with
   `"_chapters"` (English chapter names) and per table `{"t": English title, "d": one-sentence description}`,
   written by Opus agents from the JSON only (`TRANSLATE_TASK.md`, McCune–Reischauer / Hepburn).
9. **Printed contents** (before deleting the page images; user, 2026-10-13): an agent reads the book's contents pages
   by eye into `_work/toc.json` (`{"entries": [{"level", "title", "page", "src"}]}`, every chapter and every listed
   section) — done **first, before the survey** (step 2). Entries printed without a page number get a `found_leaf`
   from what earlier passes already saw, never from a dedicated re-read of the book (user, 2026-10-14: a separate
   locate pass over every page of 1939 cost a week's quota): (a) the survey agents' `headings_*.json`; (b) mission
   reports, which list every section heading seen on their pages (`MISSION.md`); (c) a local fuzzy match of entry
   titles against the transcribed table titles; (d) only what is still unplaced goes to ONE small agent working
   from 4-page sheets (2×2, `sheets4/`), limited to the leaves between the neighbouring placed entries. Anything
   not found links to its chapter — that is acceptable; do not spend a pass to place every subsection.
   `python3 ../_pipeline/toc_leaves.py <book>/_work` maps printed pages to scan leaves via `plan/survey.json`. build_site shows it as a collapsible "Contents of the printed book" on the book's contents
   page, each entry linked to its scan page, and keeps a copy in `data/<slug>-toc.json` for when `_work` is gone.
   Every book with a printed contents also gets a **"Show tables"** checkbox there (user, 2026-10-22): ticked, each
   entry lists links to this site's tables under it (numbered tables by their number, others under the entry that
   starts nearest before them in the scan). build_site does this automatically from `toc.json` — so give every new
   book a contents transcription with leaves. Table links are a different shade from the scan links; **never italicise
   Asian (CJK) text** anywhere on the site (user, 2026-10-22).
10. **Charts and topic pages** (user, 2026-10-22; Korea and Taiwan): `build/topics/<region>.json` tags tables
   (`{"slug:id": [[topic, subtopic], …]}`, topics population / education / religion / crime, fixed subtopic lists in
   `build_site.SUBTOPICS`; brief in `build/topics/TOPIC_TASK.md`, Sonnet agents working from title listings only).
   Every Korea and Taiwan table gets a Table / Chart / Both switch (`charts.js`, our own code, no library; `CHART_ALL` in
   build_site), elsewhere only tagged tables; `topics/<region>-<topic>.html` lists the tagged ones with a coverage grid.
   A table printing several measures gets one chart per measure (tabs); earlier-year rows under a list form their own chart. Charts draw only printed figures: [?], blanks, dashes and ditto marks are gaps, never
   filled; labels and year order as printed; printed totals are marked on stacked bars and parts that do not add up show ≠.
11. **Publish** (below). Note queued books in `../queue.md`; record per-book state in `_work/STATUS.md`.

## Site and BOOKS entry

- One entry per book in `BOOKS` (`build/build_site.py`): `slug`, `dir`, `title` (simple title + year; edition
  year, e.g. "朝鮮年鑑 1940"; never "(incomplete scan)" in the title: put it in `note`, shown under the publisher on the card), optional `subtitle`
  (romanisation/edition), `publisher`, `blurb` (English overview), `source`, `gaps` (what is and isn't
  transcribed, missing pages, how checks were done), `scan` (`…/page/n{leaf}/…` for IA, `https://dl.ndl.go.jp/pid/<pid>/1/{leaf}`
  for NDL; `None` if not online), `item`, `blank_marking: True`; optional `group` to force a home-page section.
- Home-page sections: Japan, China, Korea, Taiwan, Manchuria, Other — chosen from the slug prefix
  (`japan-`, `china-`, `korea-`, `taiwan-`, `manch…`) or `group`; Korea, Taiwan, Manchuria and China sort by
  edition year. Slugs: 朝鮮年鑑 = `korea-nenkan-YYYY`, 朝鮮事情 = `korea-YYYY`, statistical annual = `korea-tokanfu-YYYY`.
- Directory books can set `dir_cards`, `dir_places`, `dir_pinyin` (place cards, pinyin with "alt. romanization").
- Table pages show printed notes and transcriber's notes in collapsible sections under each table.
- **Notes** (reader annotations): table, directory and chronology pages have an opt-in Notes button that loads the
  vendored `annotate.js` 1.4.0 (MIT; `annotate.js` + `annotate.LICENSE.txt` at the site root; never load it from a CDN).
  Notes stay in the reader's localStorage (project `stat-tables`), keyed per view (one table, chapter or directory
  section). Loader and workarounds live in `ANNOT_JS` in `build_site.py`; no feedback endpoint (user, 2026-10-10).
  **Switched off for now** (user, 2026-10-10: "a bit too confusing"): `NOTES_ENABLED = False` removes the button and loader.

## Building and publishing (this session runs the repo — user, 2026-10-06)

- Build: `STAT_TABLES_ROOT=/Users/kml/shell/projects/yearbooks/japanyearbooks python3 build/build_site.py`, then
  `uv run --with openpyxl build/build_downloads.py`, then build_site again (so the page links the new download).
- Branch from `origin/main` with `--no-track`; commit only the new book's files plus `build_site.py`, `index.html`,
  `search.html` and any book pages a shared-code change touched; revert other rebuilt files (often
  `book/japan-1935/directory.html`, `book/korea-nenkan-1926/directory.html`, other books' downloads).
- Check `git merge-base --is-ancestor origin/main HEAD`, then push explicitly:
  `git push origin refs/heads/<branch>:refs/heads/main`; watch the Pages deploy (`gh run watch`).
- Commit trailer as given by the session; never the user's identity.
- Full Search runs on Pagefind indexes (`pagefind/` = everything, `pagefind-titles/` = titles and names only),
  written from the committed `data/*.json` by `uv run --with "pagefind[extended]" build/build_search.py`. Rebuild them
  after build_site whenever tables, directories or chronologies change. The folders are **not in git** (`.gitignore`):
  the user uploads them to the server that hosts the site (user, 2026-10-12), so the GitHub Pages copy has no
  search index. `robots.txt` and `llms.txt` ask crawlers to skip them and point to the GitHub data instead. Chinese/Japanese
  characters are indexed spaced, with folded (fold.js) copies of lines that contain variant forms.
- **Heavy local jobs must leave the machine usable** (user, 2026-10-12): the index build runs at `nice 15` with
  `RAYON_NUM_THREADS` = cores − 3 (set inside build_search.py); for other CPU-heavy work (ImageMagick montages and
  crops, rendering, pdfimages over whole books) use `nice -n 15` and `MAGICK_THREAD_LIMIT` = cores − 3, and never
  run more than one heavy local job at a time.
