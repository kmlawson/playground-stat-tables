# Adding a book from another session

Several Claude sessions add books to this site at the same time, each on its own branch. The main session
merges the branches into `main` and publishes. This guide explains how to prepare a book and post a branch
so that merges go cleanly. `BRIEF.md` in this folder is the template brief for the sub-agents that do the
transcription.

## 1. Where things live

- **This repo** holds the build scripts (`build/build_site.py`, `build/build_downloads.py`) and the generated site:
  `index.html`, `search.html`, one folder per book (`book/<slug>/index.html`, `directory.html`, `chronology.html`),
  `data/<slug>*.json` and `downloads/<slug>-*`.
- **Transcriptions live outside the repo**, in a book folder next to it:
  `<BookFolder>/_work/tables/*.json`, `…/directory/*.json` and `…/chronology/*.json`. `build/build_site.py` reads
  them and regenerates everything. Scans, crops and page images are never committed (`.gitignore`).
- Each book is one entry in the `BOOKS` list at the top of `build/build_site.py`.

## 2. The BOOKS entry

```python
{"slug": "china-1929-30",                  # URL folder and data file prefix; lowercase, unique
 "dir": "China_Year_Book_1929-30",          # book folder, relative to the folder holding this repo
 # or "root": "/abs/path/to/BookFolder"     # if the book folder lives somewhere else
 "title": "The China Year Book 1929-30",
 "publisher": "Editor; place: publisher, year",
 "blurb": "One sentence (shown only in the About box).",
 "source": "LLM-transcribed from ...",
 "in_progress": True,                       # remove when every batch is done
 "dir_in_progress": True,                   # optional: directory still being transcribed
 "gaps": "Missing pages, skipped sections ...",   # About box; add when the book is complete
 "scan": "https://archive.org/details/<item>/page/n{leaf}/mode/1up",  # per-table scan links
 "item": "https://archive.org/details/<item>",                        # "original scan" link on the card
 # "scan": None, "hide_images": True        # no online scan: tables show no scan link
}
```
- For multi-part Internet Archive items, name leaves `p{part}-{leaf:04d}` and put `{part}` and `{leaf}` in
  `scan`.
- If the scan is not online, set `"scan": None, "hide_images": True` and leave out `item`.
- Book order on the home page is the order of `BOOKS`: the Japan Year Books first (by year), then Korea,
  Manchoukuo, the Far East book, then the China books. Put your entry where it belongs in that order.
- Say "LLM-transcribed", never "hand-transcribed".

## 3. Posting a branch without clashing

The clashes so far came from three things:
- sessions committing regenerated files for **other** books;
- one session's build resolving book folders against the wrong root, which overwrote another book's data;
- edits to shared template code in `build/build_site.py`.

Follow these steps.

1. **Start from the current `main`.** Run `git fetch origin && git switch -c <your-branch> origin/main`, or if
   your branch already exists, `git rebase origin/main`. Rebase again just before every push.
2. **One branch per book or series** (e.g. `early-japan-year-books`, `far-east-1941`). Never push to `main`.
3. **Set the root when you build from a worktree or clone that isn't next to the book folders.**
   `build/build_site.py` finds relative `dir` paths from `STAT_TABLES_ROOT`, falling back to the folder that holds
   the repo. If your checkout lives elsewhere, run
   `STAT_TABLES_ROOT=/path/to/folder-holding-the-book-folders python3 build/build_site.py`.
   Otherwise other books may resolve to the wrong folder and be rebuilt empty, or from the wrong data.
4. **Build**: `uv run --with openpyxl build/build_downloads.py`, then `python3 build/build_site.py`.
5. **Commit only your own files.**
   - Commit: your `BOOKS` entry (one block in `build/build_site.py`), your README row, `book/<slug>/`, `data/<slug>*.json`
     and `downloads/<slug>-*`.
   - Revert everything else the build touched, such as other books' data or pages, `index.html` and
     `search.html`: `git checkout -- <path>`. Check `git status` and `git diff --stat` before committing; the
     only changes should be in your book's files.
   - The main session rebuilds `index.html`, `search.html` and every other page from all the book folders when
     it merges, so you don't need to commit them.
6. **Don't change shared code in the same commit as book data.** If you need a change to the templates or the
   build logic, such as a new field or a bug fix:
   - put it in its own small commit with a message that explains why;
   - keep it backwards-compatible, with new keys optional and defaults unchanged;
   - never reformat or reorder code you didn't need to touch.
7. **Commit identity and privacy.**
   - Author commits with the account's GitHub noreply address; never a personal email.
   - Add the usual Co-Authored-By trailer.
   - Nothing that identifies the user goes into commits, file metadata, request headers or pages. Use a
     descriptive, non-identifying User-Agent (e.g. `table-extraction/1.0 (offline archive research)`) when
     downloading scans.
8. **Push your branch** (`git push -u origin <your-branch>`). For a large push, use
   `git -c http.postBuffer=524288000 push`. Then tell the main session, or the user, which commit is ready.

The main session merges your branch. Where generated files conflict, it takes `main`'s side and rebuilds
everything from the book folders, which regenerates your book from your `_work` files. Your transcriptions
in the book folder are therefore the source of truth, not the generated HTML.

## 4. Running the transcription

- Copy `build/example/BRIEF.md` to `<BookFolder>/_work/BRIEF.md` and `build/example/MISSION.md` to
  `<BookFolder>/_work/MISSION.md`; fill in the placeholders and the "This book" section.
- **Use short missions, not big batches.** Batches of 12–30 spreads ran for 5–9 hours per agent, were hard
  to monitor, and lost work when an agent died from an API timeout. Size each mission to finish in under an
  hour:
  - dense statistical pages (trade returns by commodity and country, big multi-part tables): **1–3 pages or
    spreads** per mission;
  - ordinary table pages: **3–5** (up to 8 when that keeps whole tables inside one mission);
  - pure prose (laws, history, treaties, Who's Who pages to be skipped): **10–20**.
  Make a contact sheet (`magick montage`, labelled thumbnails, ~40 leaves per sheet) of the whole book first,
  and draw the mission boundaries where tables start and end, so that few tables cross a boundary.
- **Very long single tables** (a 30-page customs tariff, a trade return running 20 pages): split them into
  missions of ~5 pages that each write **one file per printed page** (`"continued": true`), with the columns
  and conventions fixed up front in a small `_work/<TABLE>_CONVENTIONS.md` (set by the first mission). Then
  they can run in parallel and the pieces are merged or shown in page order afterwards.
- Keep the plan in `_work/batches.md`: one row per mission, with its pages, any file it must "finish", and a
  status. Run missions on a rolling basis — start the next one as each finishes — staying under the
  concurrent-agent limit the user has set (ask if you don't know it).
- Tables that cross mission boundaries: the mission that owns the **first** page of a table writes all of it,
  reading ahead (see BRIEF.md). So missions can run in parallel without duplicates. When a mission is killed
  mid-table, the next mission's prompt names the partial file and tells it to **finish** it. When a finished
  mission reports that it read ahead into a neighbour's pages, **message the running neighbour** so it skips
  that continuation.
- The prompt itself is a few lines (template at the end of MISSION.md): the pages, any file to finish, an
  example file whose structure to copy, the no-OCR rule, the report file.
- **Watch progress by files, not by elapsed time**: `ls -t tables | head` and the mission's report. A
  mission with no new file for ~30 minutes is stuck: stop it and relaunch a smaller one from what is on disk.
- When a mission finishes, read its reply: it may report a table nobody owns (e.g. a table whose first page
  was in a mission that died). Queue a one-table mission for it.
- Do Who's Who and directory sections as separate missions (`directory/<leaf>.json`), and chronologies the
  same way.
- **Check pass.** When a book is done, run short check missions over (a) tables whose totals do not
  reconcile, (b) tables with columns in the gutter, and (c) a random ~10% sample: re-read against the image
  and fix misreads. In the Far East Year Book 1941 such re-reads found shifted columns and misread digits
  that the first pass had missed.
- **Audit "judgement calls" in replies.** Agents sometimes fill a half-printed digit from its shape, a
  similar glyph elsewhere, row order or a total, and say so. Under the no-guess rule those cells must be
  blank with the partial reading in the note — blank them, or send the mission back to do it.
- Publish interim progress with `"in_progress": True`. When every mission is done, remove it and add `gaps`.

## 5. Parallel sessions: git practice and measured results (2026-09-26)

### What works
- Each session has its own clone or worktree and its own branch; nobody checks out another session's
  branch in the shared `stat-tables-site` folder.
- Each book's transcriptions live in their own `<BookFolder>/_work` — the source of truth — so no two
  sessions edit the same data.
- Merge (or rebase onto) `origin/main` before every push; push small increments often; commit only your
  own book's files (§3).

### The weak spot: generated files and the shared `BOOKS` list
Every session rebuilds and commits the same generated files (`index.html`, `search.html`, `data/*.json`,
`downloads/*`), and every session edits the `BOOKS` list in `build/build_site.py`. They conflict on almost every
merge; resolving by rebuilding from the book folders works only if whoever merges remembers to.
- `git merge` **refuses to start while you have uncommitted edits**, and the message is easy to miss.
  Commit or stash first, then confirm: `git merge-base --is-ancestor origin/main HEAD`.
- Before committing a resolved merge, `grep -rlE '^(<<<<<<<|>>>>>>>) ' --exclude-dir=.git .` must print
  nothing.

### Recommended changes (for the maintainer; they affect every session)
1. **Don't commit generated output on branches.** Branches carry only source data and code; pages,
   `data/*.json` and `downloads/*` are rebuilt once on `main` after merging — ideally by a GitHub Action on
   push to `main` that runs both build scripts and publishes to Pages. (The Action needs the `_work` JSON
   in the repo, e.g. `books/<slug>/tables/…`, since it cannot see local folders.)
2. **One small config file per book** (`books/<slug>.json` with an `order` key) instead of one shared
   `BOOKS` list, so sessions never edit the same lines of `build/build_site.py`.
3. **Merge small and often.** Long-lived branches make the generated-file conflicts worse.

### Why short missions: what three sessions measured
- **Far East Year Book 1941:** 1-spread missions took 13–70 min; 12-spread batches took 5–9 hours.
- **Japan Year Book 1905** (same scan, same brief): 30-leaf batches took 48–89 min (1.6–2.5 min/leaf,
  ~6–7k tokens/leaf); on harder scans (1910 low resolution, 1920-21 dense tables) they ran 2–7 hours, slowed
  as their context grew, and several died and had to be resumed. 2–7-leaf missions took a median ~8 min
  (1.9 min/leaf, ~18k tokens/leaf) and none failed.
- **China Year Books 1912 and 1929-30** (8–10 agents): 19 thirty-leaf batches took a median 77 min (up to
  213), ~2.6 min/leaf and 12.7 tables per agent-hour; 22 content-aligned batches of 3–20 leaves took a median
  9 min (up to 44), ~1.3 min/leaf and 23.7 tables per agent-hour, with no failures.
- Why: a small agent's context stays small (~90k vs ~190k tokens), so every step is faster and it never
  hits compaction; a failure costs minutes; free slots let dense and light sections interleave; boundaries
  drawn around whole tables need less cross-checking. Costs: ~2–3× the tokens per page (every agent re-reads
  the brief), more seams to coordinate, and more orchestration for the main session. Quality — tables per
  page, blanks, reconciliation notes — was the same.
