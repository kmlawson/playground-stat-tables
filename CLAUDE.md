# CLAUDE.md — Old Tables of East Asia (stat-tables site)

Static site of statistical tables, directories and chronologies transcribed from yearbooks and handbooks on Japan,
Korea, Taiwan, Manchuria, China and the South Seas Mandate — in English, Japanese or both (177 books, 2026-11-07).
This file is the authoritative process overview (updated 2026-11-07). Rarely-needed details are in
`docs/reference.md`; the book log is `../queue.md`. When a rule changes, change it here (and in the templates), not in
memory notes.

## Where things are

- **Live site:** https://froginawell.net/reference/old-tables/ (the user updates that copy; a push does not).
  **GitHub Pages** (https://kmlawson.github.io/playground-stat-tables/) deploys from `main` on every push and is the
  draft. The Pagefind index is not in git and exists only on the live server.
- **Sources are outside the repo:** each book's transcriptions are JSON in `../<Name_Year>/_work/` (`tables/`,
  `directory/`, `chronology/`, `toc.json`, `STATUS.md`). The build reads them through `STAT_TABLES_ROOT`.
- **Built (committed) output:** `index.html`, `about.html`, `search.html`; `book/<slug>/` (one self-contained page
  per book, plus `directory.html`, `chronology.html`); `data/<slug>.json` (+ `-toc.json`); `downloads/` (Excel,
  Markdown); `topics/` (topic pages, tag pages, `with-maps.html` with `maps/` and `map.html`); `support/`
  (map-link candidates). Never edit these by hand: change `build/` and rebuild.
- **Site scripts at the root** (hand-written, served as is): `charts.js`, `tags.js`, `tags.css`, `fold.js`,
  `annotate.js`. `inspect/` is a local, git-ignored inspection tool.
- **`build/`:**
  - `build_site.py` — everything: `BOOKS` (one entry per book, the first ~1,550 lines), loaders, crosslinks, English layer,
    map links, topic pages, with-maps, landing page and the page templates (`TEMPLATE`, `DIRTEMPLATE`, `SEARCH`).
  - `build_downloads.py` (Excel/Markdown), `build_search.py` (Pagefind), `build_tags.py` (tag pages),
    `bump_version.py` + `VERSION.json`, `about_text.py` (the author's own text: change only when asked),
    `added_dates.json` (when each book first went in), `leafmaps/` (scan-leaf corrections).
  - `maplinks.py`, `maplinks.json`, `maplinks_add.py`, `build_candidates.py`, `MAPLINK_SPEC.md` — "View as Map".
  - `translations/<slug>.json` (English layer), `topics/` (topic tags + `TOPIC_TASK*.md`), `tags/` (controlled
    vocabulary, `new_book_tags.py`, `published/assignments.json`), `crosslinks/` (series, families, prompts),
    `example/` (templates `BRIEF.md`, `MISSION.md`; `guidance.md` for parallel sessions and branches).
- **Next to the repo:** `../_pipeline/` (llm pipeline, `toc_leaves.py`, `kits/`), `../_codex/`, `../_haiku/`,
  `../_review/`, `../_toc/`. The `fareast/` and `chinahandbook1950/` folders beside `japanyearbooks/` hold other
  worktrees of this same repo on their own branches.
- **Git:** this checkout is a worktree whose git directory is on `/Volumes/Oma` (`.git` file): git fails if Oma is
  not mounted.

## Hard rules (every book, every sub-agent prompt)

- **No OCR, ever.** Every figure is read from the page image by a vision model: no tesseract, Apple Vision, PDF text
  layers, OCR files, or pixel/darkness/stroke-counting scripts. Cropping, zooming and contrast for the model's own
  eyes are fine. Claude sub-agents by default; Codex (gpt-6.1-sol/astra) or agy (Gemini) only for the books the user
  names for them (`../queue.md` records which); the `llm` CLI only when the user asks for it (user, 2026-10-28), and
  a permission given for one batch ends with that batch. Say this in every sub-agent prompt.
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
- **Models (user, 2026-10-07/08/13/27).** Sonnet by default — missions, contact-sheet surveys, directories,
  chronologies, second transcriptions and third readers. Haiku for easy missions: at most one dense page and no
  sideways pages or spreads (Japan-Manchoukuo 1939 trial: 99.4% figure agreement with Sonnet; tell Haiku to keep
  figures exactly as printed, commas and dots included). Opus only for the hard ones: 3+ dense pages, sideways
  pages, spreads, dense Japanese 目次. **Japanese tables: kanji (old-style) numerals → Opus; Arabic numerals →
  Sonnet.** Pass the model on every Agent call and set `"model"` in the BOOKS entry to the model that did the
  reading. At most 10 agents at a time (the user's limit). No more Opus spot-checks (Sonnet agreed 99.7–100%; an
  Opus review of Haiku/Sonnet samples on 2026-11-04 found 99.92%, with Haiku over-marking clear figures `[?]`).
- **Privacy.** Nothing identifying the user in commits, request headers (User-Agent/From), file metadata or
  pages. Descriptive, non-identifying User-Agent for downloads.

## How a book is read

- **Agent missions** (Claude Code sub-agents; the workflow below) are the default. Toolkits:
  `../_pipeline/kits/ndl-tokei/` (NDL statistical yearbooks) and `../_pipeline/kits/english-yearbook/`.
- **Codex / agy / the `llm` pipeline** only when the user names them for a book (`docs/reference.md`).

Before committing to a book, check the scan resolution and the `[?]`/blank rate of a small pilot: 朝鮮年鑑 1941 was
abandoned after 12 of 50 missions with about 68% of cells blank (5068 px per spread). Check `df -h` before any job
that writes gigabytes.

## Workflow for a book

1. **Get the scan.** `ia download` (Internet Archive) or the user's PDF (often NDL, on the Oma drive). Book folder
   `<Name_Year>/` next to this repo; work in `<Name_Year>/_work/`. Extract page images to `full/pNNNN.jpg`
   (`pdfimages -j` for the original JPEGs; render at 300 dpi only for non-JPEG pages; JP2 zips via `magick`).
   `pNNNN` = PDF page / scan leaf, 1-based (keep a `build/leafmaps/<slug>.json` if the online viewer counts
   differently). Make 1600–1800 px copies in `plan/`.
2. **Printed contents first** (user, 2026-10-13/14; 2026-11-01: more important than tags or similar tables). An
   agent reads the book's contents pages by eye into `_work/toc.json` (`{"entries": [{"level", "title", "page",
   "src"}]}`, every chapter and every listed section), whatever pipeline will read the tables. A chapter-only list
   is not enough when the book prints a fuller contents. Entries printed without a page number get a `found_leaf`
   from what other passes already saw, never from a dedicated re-read of the book (a locate pass over every page of
   1939 cost a week's quota): (a) the survey agents' `headings_*.json`; (b) mission reports, which list every
   section heading seen on their pages (`MISSION.md`); (c) a local fuzzy match of entry titles against the
   transcribed table titles; (d) only what is still unplaced goes to ONE small agent working from 4-page sheets
   (2×2, `sheets4/`), limited to the leaves between the neighbouring placed entries. Anything not found links to its
   chapter. Sonnet on contents pages guesses smudged page numbers and calls its own misreads "misprints": send every
   item it marks uncertain or out of sequence back for a tight-crop re-read (`../_toc/`, `TOC_BRIEF.md`).
   `python3 ../_pipeline/toc_leaves.py <book>/_work` maps printed pages to leaves via `plan/survey.json`. The build
   shows it as a collapsible "Contents of the printed book", each entry linked to its scan page, with an
   **"Include table links [T]"** checkbox on by default, and keeps a copy in `data/<slug>-toc.json`.
3. **Contact sheets and survey.** Make sheets with the `contactsheet` skill (user, 2026-11-05): 8 images per sheet,
   4×2, each labelled with its leaf name (`pNNNN`) in `sheets/`. Survey agents (Sonnet, ~8–16 sheets each,
   `plan/SHEET_SURVEY.md`) list only the images with tables, lists, charts with figures or directories, one line
   each: `pNNNN | pp. | START/CONT | kind | titles | ENDS/RUNS-ON`, plus skipped runs (contents, index, ads, prose)
   and missing/duplicated pages. Only those pages are read later. Give each survey agent the contents entries for
   its stretch: it also writes `headings_<x>.json` (`{"<toc index>": "pNNNN"}`) for every listed heading it sees.
   Note every page printed sideways and make its crops already rotated upright before the missions (user,
   2026-10-30); say in the prompt that the crop has been rotated.
4. **Brief.** Copy and adapt `BRIEF.md` (rules, JSON format, the book's "This book" section: language, numerals,
   chapter naming, page numbering, spreads/RTL, units) and `MISSION.md`; `prompt.py` + `next.sh` +
   `missions.json` drive the missions; `validate.py` checks files.
5. **Missions.** Built from the survey lines: ~3–6 images per mission (3 spreads for dense vertical Japanese
   tables, 4–6 single pages for English tables), never splitting before a `CONT` page; a mission whose last table
   runs on is told to read into the next image, the next mission is told to skip that continuation. Directory or
   Who's Who pages get separate DIRECTORY missions (`directory/<leaf>.json`); columnar lists are tables.
   **Chronologies** (dated-event lists) are transcribed in every book except the Japan Year Books
   (`chronology/<leaf>.json`: events with full dates, year/month carried over, ditto marks resolved); a chronology
   printed as a table inside a chapter belongs with the tables (user, 2026-10-12). Run on a rolling basis, ≤10
   agents; each mission: report in `reports/<MID>.md`, crops and helper scripts only in `crops/<MID>/`, never
   anything in `/tmp`. `./next.sh <done-MID>` marks one done and prepares the next prompt. Reply to the user per
   mission only "N done, M left".
6. **Follow-ups (FIXES.md).** Log from mission reports: tables nobody owns, duplicates, orphan fragments whose
   first page is missing, and every cell an agent *changed after a total check flagged it*.
7. **Checking — light** (user, 2026-10-28 and 2026-11-03: "avoid excessive checking after extraction"). After
   missions, only mechanical assembly (joins, duplicates, orphan fragments, `validate.py`) and publish; no re-read
   passes unless a mission clearly failed (gave up, empty output, wrong layout). No 10% random check, no Opus
   spot-checks, no elaborate rounds after a book is finished. A non-reconciling total is normally a misprint in the
   source and stays as printed with a note; it is NOT by itself a reason to re-read. When a second reading is due:
   - Blind re-read of single cells only (an agent that sees table/row/column, never the values; `BLIND_TASK.md`,
     `blind/`): cells settled by the 3-vs-8 / 一/二/三 rule, and cells a reader marked doubtful.
   - A full independent second transcription of a table only when ALL hold: kanji (stacked-stroke) numerals; 3 or
     more total mismatches in that table; and the gaps have the shape of stroke-grouping misreads (a power of ten
     or 2×), not arbitrary amounts. Never for Arabic-numeral tables.
   - Where readings differ, one blind third reading of just those cells decides (two of three); three different
     readings or unsure → `"[?]"`. Keep the first version (`blind/*.first.json`) and note every change.
8. **Normalise** chapter names (one per printed chapter, numbered as printed), titles, duplicate files. **Assign
   chapters by the table's first printed page, never by its scan frame** (user, 2026-11-05): on a two-page spread a
   chapter can begin on the right page. Where a table sits on the very page a chapter starts, decide by its subject
   and table number. Huge single-part books get bracketed site chapters in printed order.
9. **Errata slip** (正誤表): look at every front frame (covers, endpapers, title leaf) for a pasted slip. Transcribe
   it with the contents into `_work/errata.json` and attach each correction as a transcriber note to its table; the
   figures stay as printed.
10. **English layer for every Japanese, Chinese and Korean book — REQUIRED before publishing** (user, 2026-11-03):
    `build/translations/<slug>.json` with `"_chapters"` (English chapter names) and per table `{"t": English
    title, "d": one-sentence description}`, written by Sonnet agents from the JSON only
    (`../_pipeline/kits/ndl-tokei/TRANSLATE_TASK.md`; Hepburn for Japanese, McCune–Reischauer for Korean,
    pinyin/Wade-Giles as the book's period usage for Chinese). Check one entry per table file before building.
11. **Controlled tags** (user, 2026-10-27): each table gets 0–2 high-level topics, 0–3 detailed tags and a
    `text-tables` flag from `build/tags/vocabulary.json` (`VOCABULARY.md`; rules `README.md` + `CLASSIFICATION.md`)
    — **only where a term genuinely fits**. After `data/<slug>.json` is built:
    `python3 build/tags/new_book_tags.py prepare <slug> --prior <earlier editions>` writes batches; Sonnet agents
    follow `build/tags/NEW_BOOK_TASK.md` and write `results/bNN.json`; `new_book_tags.py apply <slug>` validates and
    saves to `build/tags/published/assignments.json`. Commit `build/tags/runs/new-<slug>/` with the book.
12. **Similar tables / Compare** (user, 2026-10-28): when a book belongs to a series, add it to `SERIES` in
    `build/crosslinks/chapters.py`, run `make_listings.py`, and have Sonnet agents match its tables into
    `build/crosslinks/families/<series>--<topic>.json` (update-mode prompts like `prompts/NU1.txt`/`KU1.txt`: add
    new-edition tables to existing families, never reshuffle; new series: `prompts/S01.txt`). Record the mission in
    `missions.md`.
13. **Topic tags for charts** (user, 2026-10-22/23): `build/topics/<region>.json` (`{"slug:id": [[topic,
    subtopic], …]}`; topics population / education / religion / crime, subtopics in `build_site.SUBTOPICS`; brief
    `build/topics/TOPIC_TASK.md`, Sonnet agents from title listings). Every table has a Table / Chart / Both switch
    (`charts.js`, our own code); charts draw only printed figures: `[?]`, blanks, dashes and ditto marks are gaps,
    never filled; printed totals are marked and parts that do not add up show ≠. **Never italicise CJK text.**
14. **Map links** (tables by prefecture, province, island group, city or country): `python3 build/maplinks_add.py
    --dry <slug>/<id> …`, then without `--dry`; check the build's `maplinks:` lines for unplaced rows and places on
    more than one row (`docs/reference.md`).
15. **Publish** (below). Record per-book state in `_work/STATUS.md` (method, models, counts, what is missing,
    publish commit) and mark the book in `../queue.md`. Push each volume as soon as it is complete (user,
    2026-10-31).
16. **Clean up after publishing.** Copy downloaded originals (not plan copies, crops or sheets) to
    `/Volumes/Oma/Book Scans/<series>/<year>/` and verify counts/sizes, then delete the book's `full/`, `plan/`
    images, `sheets/` and crops; never delete `tables/`, `directory/`, `chronology/` or `toc.json`. Delete finished
    sub-agent transcripts (~100 MB per mission) by literal path, never by a broad glob (`crops/M_p1-021*` once also
    matched `M_p1-0215`).
17. **Finder pages:** nothing per book. Every ~5–10 new books (or monthly) run the finder batch (below): `status.py
    --batches` → spec agents → aliases → outliers → build → `status.py --baseline`.

## Finder pages (`figures/`, user 2026-11-07)

`figures/population.html` (the first; hub `figures/index.html`, linked from the Topics index and from the population
topic/tag pages, not from the home page): every population figure (people, male, female, households; by group) for
every place, year by year. The same figure from several tables is shown once with a link to each; differing figures
side by side, never averaged; "≈ same, rounded" for a rounded print that agrees. Each figure links to its table with
the cell marked (`book/<slug>/#<id>~<part>.<row>.<col>`); table pages link back ("Population across all books"), Search
shows a card for a matching place, and the Japanese Empire map's place card links in (`fillFiguresLink` in its map.js).
- **Code:** `build/finders/` — `finderlib.py` (numbers, dates, place matching, spec loading, fingerprints),
  `places/` (`places.json` frozen from the map's gazetteer by `make_gazetteer.py`; `aliases.json` hand matches,
  `ALIAS_TASK.md`), `registry.py` (what the rest of the site reads), `build_all.py` (run at the end of
  `build_site.py`: every finder + the hub), `status.py` (backlog). Per finder `<name>/`: `config.json` (candidate tags
  and words, banner), `TASK.md` (spec brief), `specs/<batch>/bNN.json`, `spec_fixes.json` (`OUTLIER_TASK.md`),
  `extract.py`, `build_<name>.py`, `check.py`, `make_previews.py`, `page.html`, `baseline/`, `table_links.json`.
- **Nothing is re-read:** a spec per table says which rows/columns hold the figure, for which place, date, group and
  basis; the script copies those cells as transcribed. Each spec carries a fingerprint of its table; if the table
  changes, the spec is left out until re-written.
- **Finder batch, every ~5–10 new books or monthly** (not per book): build; `python3 build/finders/status.py
  --batches` (tables with no spec, stale specs, new unmatched names, new suspicious figures; writes
  `work/batches/pending-<date>/`); one Sonnet agent per finder on those batches with its `TASK.md`, specs into
  `specs/pending-<date>/`; one agent on `work/new_names.txt` with `ALIAS_TASK.md`; one on `work/new_outliers.txt` with
  `OUTLIER_TASK.md`; build again; look at a few new places; `status.py --baseline`; commit specs + baselines, bump
  version, push. Table pages get their finder link one build after a table's spec (they read `table_links.json`).
- **A new finder:** copy `population/`, change `config.json`, `TASK.md` and the claim fields in `extract.py`/the
  page; `make_previews.py` splits the candidates into batches for the first agents.

## BOOKS entry

- `slug`, `dir`, `title` (simple title + edition year, e.g. "朝鮮年鑑 1940"; never "(incomplete scan)" in the
  title: put it in `note`), optional `subtitle` (romanisation/edition), `publisher`, `blurb` (English overview),
  `source`, `gaps` (what is and isn't transcribed, missing pages, how checks were done), `scan`
  (`…/page/n{leaf}/…` for IA, `https://dl.ndl.go.jp/pid/<pid>/1/{leaf}` for NDL; `None` if not online), `item`,
  `model`, `blank_marking: True`; optional `group` to force a home-page section. Directory options are in
  `docs/reference.md`.
- Home-page sections: Japan, China, Korea, Taiwan, Manchuria, Other — from the slug prefix (`japan-`, `china-`,
  `korea-`, `taiwan-`, `manch…`) or `group`; every section except Other sorts by edition year. Slugs: 朝鮮年鑑 =
  `korea-nenkan-YYYY`, 朝鮮事情 = `korea-YYYY`, statistical annual = `korea-tokanfu-YYYY`.

## Building and publishing (this session runs the repo — user, 2026-10-06)

- **Check first:** `git status` and the recent log. Another session may be working in this checkout; if one is,
  work in your own worktree (`git worktree add --no-track -b <branch> <path> origin/main`) and do not build here.
- Build (about 4 minutes): `STAT_TABLES_ROOT=/Users/kml/shell/projects/yearbooks/japanyearbooks python3
  build/build_site.py`; for a new book then `uv run --with openpyxl build/build_downloads.py` and build_site again
  (so the page links the new download).
- **Version** (user, 2026-11-05): 1.<update> in `build/VERSION.json`, shown in the home footer and book About
  panels. Run `python3 build/bump_version.py` before building whenever a commit is more than a very minor fix, and
  give the new number in the reply. A bump touches every book page (one line each).
- Branch from `origin/main` with `--no-track`. Commit only what the change made, plus the pages a shared-code change
  touched; revert unrelated rebuilt files
  (often `book/japan-1935/directory.html`, `book/korea-nenkan-1926/directory.html`, other books' downloads).
- Check `git merge-base --is-ancestor origin/main HEAD`, then push explicitly:
  `git push origin refs/heads/<branch>:refs/heads/main`; watch the Pages deploy (`gh run watch`). Never a bare
  `git push`: with `push.default=upstream` a tracking branch once went straight to `main`.
- `cp` and `mv` are aliased to interactive mode: use `\cp -f`, `\mv -f`. Commit trailer as given by the session;
  never the user's identity.
- **Full Search** (Pagefind; `pagefind/`, `pagefind-titles/`, not in git): `uv run --with "pagefind[extended]"
  build/build_search.py` from the committed `data/*.json`, once after a series or batch of books (not per volume),
  then pack `../search-index-upload.tar.gz` for the user to upload.
- **Heavy local jobs leave the machine usable** (user, 2026-10-12): `nice -n 15`, `MAGICK_THREAD_LIMIT` /
  `RAYON_NUM_THREADS` = cores − 3, never more than one heavy job at a time.
