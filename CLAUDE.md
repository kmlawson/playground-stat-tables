# CLAUDE.md — Old Tables of East Asia (stat-tables site)

Static site of statistical tables, directories and chronologies transcribed from yearbooks and handbooks on Japan,
Korea, Taiwan, Manchuria, China and the South Seas Mandate, in English, Japanese, Chinese or both. This file is the
authoritative process (rewritten 2026-11-10; previous versions in `docs/oldclaudemds/`). When a rule changes, change it
here and in the templates, not in memory notes.

Other files to read when the task needs them:
- **`LESSONS.md`** — what goes wrong with each kind of volume and layout (scan quality, kanji vs Arabic figures,
  sideways pages, split tables, sub-tables, giant tables, agent behaviour, checking, publishing traps). Read it before
  planning a new book.
- **`docs/ndl.md`** — rules for every NDL request: page-image downloads (`../_pipeline/ndl_dl.sh`) and catalogue
  searches (one request at a time, ≥ 5 s apart, back-off, non-identifying User-Agent). Read it before touching NDL.
- `docs/reference.md` — llm/Codex/agy pipelines, toolkits, kanji numerals, directories, charts, Search, map links.
- `docs/stages/` — one file per later stage (translations, tags, similar tables, topics and maps, finder pages):
  read the one for the stage you are at.
- `../queue.md` — the book log (what is done, where, which model, special instructions per book).

## Where things are

- **Live site:** https://froginawell.net/reference/old-tables/ (the user updates that copy; a push does not).
  **GitHub Pages** (https://kmlawson.github.io/playground-stat-tables/) deploys from `main` on every push (the draft).
- **Sources are outside the repo:** each book's transcriptions are JSON in `../<Name_Year>/_work/` (`tables/`,
  `directory/`, `chronology/`, `toc.json`, `STATUS.md`). The build reads them through `STAT_TABLES_ROOT`.
- **Built output (committed, never edited by hand):** `index.html`, `about.html`, `search.html`, `book/<slug>/`,
  `data/<slug>.json` (+ `-toc.json`), `downloads/`, `topics/`, `figures/`, `support/`. Change `build/` and rebuild.
- **Hand-written site scripts at the root:** `charts.js`, `tags.js`, `tags.css`, `fold.js`, `annotate.js`.
- **`build/`:** `build_site.py` (the `BOOKS` list, loaders, English layer, topic pages, templates); `build_downloads.py`;
  `build_search.py`; `build_tags.py`; `bump_version.py` + `VERSION.json`; `about_text.py` (the author's own text:
  change only when asked); `added_dates.json`; `leafmaps/`; `translations/<slug>.json`; `tags/`; `topics/`;
  `crosslinks/`; `finders/`; `example/` (templates `BRIEF.md`, `MISSION.md`).
- **Next to the repo:** `../_pipeline/` (`toc_leaves.py`, `kits/`), `../_codex/`, `../_haiku/`, `../_review/`, `../_toc/`.
- **Git:** this checkout is a worktree whose git directory is on `/Volumes/Oma` — git fails if Oma is not mounted.

## Hard rules (every book, every sub-agent prompt)

- **No OCR, ever.** Every figure is read from the page image by a vision model: no tesseract, Apple Vision, PDF text
  layers, OCR files, or pixel/stroke-counting scripts. Cropping, zooming and contrast are fine. Say this in every prompt.
- **Never guess.** Transcribe as printed, misprints included; re-add every printed total and note whether it
  reconciles; never correct the source. A wrong digit is worse than a blank.
- **Two kinds of empty cell.** Empty in the original = `""`; unreadable = `"[?]"` (the whole cell, never `"12[?]"`)
  plus a note naming row and column. New books get `"blank_marking": true`.
- **A printed total never decides a digit**, with two exceptions: the 一/二/三 stroke grouping (kanji numerals) and
  3-vs-8 (Western figures) — only when exactly one reading reconciles a printed sum, sub-total, balance or %-to-100,
  every other cell in that sum is certain, never chained, and the cell is listed in `transcriber_notes`.
- **No deleting by agents** (user, 2026-11-10): mission agents never run `rm`; crops stay in `crops/` until the book is
  finished. The orchestrator never chains `rm` into other commands.
- **Privacy.** Nothing identifying the user in commits, request headers (User-Agent/From), file metadata or pages.

## Models and agents

- **Claude sub-agents** by default; Codex/agy/the `llm` CLI only for books the user names for them (`../queue.md`).
- **Haiku**: light tables, at most one dense page, no spreads; tell it to keep figures exactly as printed and not to
  mark clearly read figures `[?]`. **Sonnet**: the default — multi-page tables, split/spread tables, directories,
  chronologies, contents, surveys, translations, tags. **Opus**: kanji (stacked-stroke) numerals, very dense small type,
  blind re-reads of doubtful cells (only where the rule under "Checking is light" allows one).
- **At most 10 agents at a time** (the user may set a lower limit for a book). Pass the model on every Agent call and
  set `"model"` in the BOOKS entry to the models that did the reading.
- **Checking is light** (user, 2026-10-28 / 11-03): after the missions only mechanical assembly and publishing. No
  random checks, no Opus spot-checks, no second transcriptions of Arabic-numeral tables. A non-reconciling total stays
  as printed with a note. A blind re-read of single cells (the reader sees table/row/column, never the values) only for
  a table with **more than 4 `[?]` cells AND read by a model other than Opus** (user, 2026-11-12); tables read by Opus
  are never blind re-read, whatever their `[?]` count.

## Workflow for a book

1. **Scan.** Book folder `<Name_Year>/` next to this repo, work in `<Name_Year>/_work/`. Page images in
   `full/pNNNN.{jpg,png}` (`pNNNN` = PDF page / scan leaf, 1-based; `build/leafmaps/<slug>.json` if the online viewer
   counts differently); 1600–1800 px copies in `plan/`. Check `df -h` first; download gently. Pilot one mission on a
   doubtful scan before committing to the book (see LESSONS.md).
2. **Contact sheets and survey.** `contactsheet` skill: 8 frames per sheet (4×2) in `sheets/`. Sonnet survey agents
   (~16–18 sheets each, brief `plan/SHEET_SURVEY.md`) write one line per frame:
   `pNNNN | p. | START/CONT | kind | tables starting | ENDS/RUNS-ON | density | ROT | note (Q:good/fair/poor …)`.
   **Rotate every sideways page upright in `full/` and `plan/` before any mission** and tell agents it has been done.
3. **Printed contents first.** An agent reads the contents pages by eye into `_work/toc.json`
   (`{"entries": [{"level", "title", "page", "src"}]}`, every chapter and listed section); re-read uncertain page
   numbers from tight crops. Unpaged entries get a `found_leaf` from survey/mission headings — never from a dedicated
   re-read of the book. `python3 ../_pipeline/toc_leaves.py <book>/_work` maps pages to leaves via `plan/survey.json`.
4. **Brief and missions.** Copy `build/example/BRIEF.md` (rules, JSON format, a "This book" section: language,
   numerals, chapter naming, page numbering, layout quirks, units) and `MISSION.md`. `plan/make_plan.py` builds
   `missions.json` from the survey: frames grouped into table runs, a multi-frame table kept in one mission, very long
   runs cut into fragment missions (`tables/frag/`); model per mission from density and layout. `plan/prompt.py`,
   `plan/next.py` and a `launch.sh` drive them; `validate.py` checks files. Directories and chronologies get their own
   missions. Each mission writes `reports/<MID>.md` (one line per frame, every heading seen). Run on a rolling basis;
   reply to the user per mission only "N done, M left".
5. **Assembly** (mechanical): `join_frags.py`; merge sub-table files of the same `table_no`; duplicates to
   `tables_dup/`; check `table_no` coverage against the contents and send a small fix mission for orphans; normalise
   chapters from the divider frames (by a table's first printed page), titles and odd cells; `validate.py`. Log
   follow-ups in `FIXES.md`. Huge single-part books get bracketed virtual chapters in printed order.
6. **Errata slips** (正誤表) on front frames: transcribe into `_work/errata.json` and attach each correction as a note.
7. **English layer** (title translations) — required for every Japanese, Chinese and Korean book, before the first
   build: `docs/stages/translations.md`.
8. **BOOKS entry, build, downloads** (below), then the post-build stages, each with its own instructions:
   - **Tags** (every book): `docs/stages/tags.md`.
   - **Similar tables / Compare** (every book in a series — including a second edition, which starts a new series;
     user, 2026-11-10): `docs/stages/similar-tables.md`.
   - **Chart topic tags and map links** (when tables fit): `docs/stages/topics-and-maps.md`.
9. **Finder pages** (Population etc.): for every book with tables that belong on a finder page, as part of publishing
   (user, 2026-11-10: not batched) — `python3 build/finders/status.py --batches` after the first build, specs, rebuild:
   `docs/stages/finder-pages.md`.
10. **Publish** (below), record the state in `_work/STATUS.md` and `../queue.md`, push each volume as soon as it is
    complete.
11. **Clean up — always, right after the book is pushed and the deploy has succeeded** (user, 2026-11-10; part of
    publishing, not optional, not left to the user): `bash ../_pipeline/cleanup_book.sh <Name_Year> "<title> <edition>
    <year> (<source id>)" [<Oma subfolder>]`. It backs the downloaded frames (`full/`, or `full_orig/` if pages were
    rotated) up to `/Volumes/Oma/Book Scans/` as a lossless img2pdf PDF and checks the page count; then deletes `full/`,
    `full_orig/`, `rot/`, `crops/`, `sheets/` and the `plan/` image copies with `find -delete` (no `rm` prompts). It stops
    without deleting if Oma is not mounted or the page count differs. Never deletes `tables/`, `directory/`,
    `chronology/`, `toc.json`, `reports/` or plan scripts. **Then, by hand, delete only your own session's finished
    sub-agent transcripts** (`find ~/.claude/projects/<project>/<your session id>/subagents -type f -delete`, literal
    path, once none of your agents is running) — never another session's (user, 2026-11-10). Record "scan on Oma,
    images deleted" in `STATUS.md` and `../queue.md`.

## BOOKS entry

`slug`, `dir`, `title` (simple title + edition year, e.g. "朝鮮年鑑 1940"; notes such as "(incomplete scan)" go in
`note`), optional `subtitle` (romanisation/edition, English title), `publisher`, `blurb` (English overview), `source`,
`gaps` (what is and isn't transcribed, how it was read and checked, `[?]` count), `scan` (`…/page/n{leaf}/…` for IA,
`https://dl.ndl.go.jp/pid/<pid>/1/{leaf}` for NDL, Commons `…index.php?title=File:<name>&page={leaf}`; `None` if not
online), `item`, `model`, `blank_marking: True`; optional `group`. Home-page sections come from the slug prefix
(`japan-`, `china-`, `korea-`, `taiwan-`, `manch…`) or `group`. Name books by edition year. Slugs: 朝鮮年鑑 =
`korea-nenkan-YYYY`, 朝鮮事情 = `korea-YYYY`, 中華民國統計提要 = `china-tongji-YYYY`.

## Building and publishing (this session runs the repo — user, 2026-10-06)

- `git status` and the recent log first; if another session is working in this checkout, use your own worktree.
- Branch from `origin/main` with `--no-track`.
- `python3 build/bump_version.py` before building for anything more than a minor fix; give the new number in the reply.
- Build (~4 min, `nice`): `STAT_TABLES_ROOT=/Users/kml/shell/projects/yearbooks/japanyearbooks python3
  build/build_site.py`; for a new book then `uv run --with openpyxl build/build_downloads.py` and build again.
- Commit only what the change made (plus pages a shared-code change touched); revert other books' rebuilt downloads.
  Commit trailer as given by the session; never the user's identity.
- `git merge-base --is-ancestor origin/main HEAD`, then `git push origin refs/heads/<branch>:refs/heads/main` (never a
  bare `git push`); watch the Pages deploy with `gh run watch`.
- Full Search (Pagefind, not in git): `uv run --with "pagefind[extended]" build/build_search.py` once after a batch of
  books, then pack `../search-index-upload.tar.gz` for the user.
- Heavy local jobs: `nice -n 15`, thread limits = cores − 3, one at a time.
- Shell: `cp`/`mv` are interactive aliases (`\cp -f`, `\mv -f`), `noclobber` is on (`>|`, `>>|`), unmatched globs abort.
