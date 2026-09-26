# Adding a book from another session

Several Claude sessions add books to this site at the same time, each on its own branch. The main session
merges the branches into `main` and publishes. This guide explains how to prepare a book and post a branch
so that merges go cleanly. `BRIEF.md` in this folder is the template brief for the sub-agents that do the
transcription.

## 1. Where things live

- **This repo** holds the build scripts (`build_site.py`, `build_downloads.py`) and the generated site:
  `index.html`, `search.html`, one folder per book (`<slug>/index.html`, `directory.html`, `chronology.html`),
  `data/<slug>*.json` and `downloads/<slug>-*`.
- **Transcriptions live outside the repo**, in a book folder next to it:
  `<BookFolder>/_work/tables/*.json`, `…/directory/*.json` and `…/chronology/*.json`. `build_site.py` reads
  them and regenerates everything. Scans, crops and page images are never committed (`.gitignore`).
- Each book is one entry in the `BOOKS` list at the top of `build_site.py`.

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
- edits to shared template code in `build_site.py`.

Follow these steps.

1. **Start from the current `main`.** Run `git fetch origin && git switch -c <your-branch> origin/main`, or if
   your branch already exists, `git rebase origin/main`. Rebase again just before every push.
2. **One branch per book or series** (e.g. `early-japan-year-books`, `far-east-1941`). Never push to `main`.
3. **Set the root when you build from a worktree or clone that isn't next to the book folders.**
   `build_site.py` finds relative `dir` paths from `STAT_TABLES_ROOT`, falling back to the folder that holds
   the repo. If your checkout lives elsewhere, run
   `STAT_TABLES_ROOT=/path/to/folder-holding-the-book-folders python3 build_site.py`.
   Otherwise other books may resolve to the wrong folder and be rebuilt empty, or from the wrong data.
4. **Build**: `uv run --with openpyxl build_downloads.py`, then `python3 build_site.py`.
5. **Commit only your own files.**
   - Commit: your `BOOKS` entry (one block in `build_site.py`), your README row, `<slug>/`, `data/<slug>*.json`
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

- Copy `example/BRIEF.md` to `<BookFolder>/_work/BRIEF.md` and fill in the placeholders and the "This book"
  section.
- Plan **short batches of 3–5 leaves** in `_work/batches.md`, with a status column (see §5 for why), cut
  where a chapter or a prose page begins so that tables rarely cross a batch boundary; prose-heavy runs can
  take 6–8 leaves. Look at a contact sheet of the leaves (`grids.sh`) to choose the cuts.
- Launch one sub-agent per batch. Stay under the concurrent-agent limit the user has set; ask if you don't
  know it.
- Tell every agent, in its prompt: read by eye with no OCR; blank plus a note for anything unreadable; check
  totals and never correct the source; save each table immediately; one report line per leaf; resume from the
  report if one exists.
- When a batch finishes, read its report:
  - A table that runs into the next batch's range is written once, by the batch where it starts. Tell the
    neighbouring agent so it doesn't duplicate it.
  - Record repeated or missing pages for the book's `gaps` note.
- Do Who's Who and directory sections as separate directory batches (`directory/<leaf>.json`), and
  chronologies as a chronology batch.
- Publish interim progress with `"in_progress": True`. When every batch is done, remove it and add `gaps`.

## 5. Lessons from running several sessions in parallel (2026-09-26)

Written by the session that did the early Japan Year Books (1905, 1910, 1920-21) on `early-japan-year-books`.

### What has worked
- **Separate working copies.** Each session works in its own clone or worktree on its own branch; nobody
  checks out another session's branch in the shared `stat-tables-site` folder.
- **Separate data folders.** Every book's transcriptions live in their own `<BookFolder>/_work`, so no two
  sessions ever edit the same source data. These folders are the source of truth.
- **Merge (or rebase) `main` before every push**, and push small increments often.
- **Commit only your own book's files**, reverting everything else the build touched (§3 step 5).

### The weak spot: generated files in git
Every session rebuilds and commits the same generated files (`index.html`, `search.html`, `data/*.json`,
`downloads/*`), and `build_site.py`'s `BOOKS` list is edited by everyone. These conflict on almost every
merge. The fix so far — take either side and rebuild from the book folders — works, but only if whoever
merges remembers to rebuild. A merge can also silently not happen: `git merge` refuses to start while you
have uncommitted edits (e.g. to `build_site.py`), so **commit or stash before merging, and check that the
merge actually ran** (`git log -1 origin/main` should be an ancestor of `HEAD`).

### Recommended changes (for the maintainer to decide; they affect every session)
1. **Stop committing generated output on branches.** Branches carry only source data and code
   (`build_site.py`, per-book config). Pages, `data/*.json` and `downloads/*` are rebuilt once, on `main`
   after merging — ideally by a GitHub Action on push to `main` that runs the two build scripts and
   publishes to Pages. (The per-book `_work` JSON would then need to live in the repo, e.g. under
   `books/<slug>/`, since the Action cannot see local folders.)
2. **One small config file per book** instead of one shared `BOOKS` list, e.g. `books/japan-1905.json`,
   loaded and ordered by `build_site.py` (an `order` key). Sessions then never edit the same lines.
3. **Merge small and often.** Long-lived branches make the generated-file conflicts worse.

### Sub-agent batch size: short batches finish far sooner
Measured on the 1905 volume (same scan, same brief):
- 30-leaf batches: 48–89 min each for 30–36 leaves (1.6–2.5 min/leaf), ~6–7k tokens/leaf. On harder scans
  (1910 low resolution, 1920-21 dense tables) 30-leaf batches ran 2–7 hours each, slowed as their context
  grew, and several died (API timeouts, stalls, quota cut-offs) and had to be resumed.
- 2–7-leaf batches: median ~8 min each (range 2–27), ~1.9 min/leaf, ~18k tokens/leaf; none failed.
- So: similar speed per leaf and the same quality (tables per leaf, blanks, reconciliation notes), but
  **work lands in minutes, a failure costs minutes rather than hours**, at roughly 2–3× the tokens per leaf
  (each agent re-reads the brief). 6–8 leaves is a reasonable middle ground if tokens matter more.
- Put the standing rules in one shared file (e.g. `_work/CHUNK_RULES.md`) and keep each launch prompt to a
  few lines naming the leaves and the chapter.
- More batch edges mean more tables crossing a boundary. The rule "the batch where a table starts writes it,
  reading on into the next leaves" works, but when a neighbour reports such a table, **message the running
  neighbour** so it skips the continuation. Long continuous lists (e.g. a 40-page tariff) are better written
  one file per leaf (`continued: true`) so no batch has to follow them far.

### Transcription consistency
- Coordinators should spot-check "judgement calls" in reports. Agents sometimes read a half-printed digit
  from its shape, context or row order; under the no-guess rule such cells should be blank with a note.
