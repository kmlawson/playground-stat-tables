# CLAUDE.md — East Asian statistical tables site

Static site of statistical tables transcribed from English-language yearbooks. The transcriptions (JSON)
live **outside** this repo in each book's `_work/` folder; `build/build_site.py` regenerates everything here from
them. Several Claude sessions add books at once, each on its own branch — read `build/example/guidance.md` before
building or pushing anything.

## Transcription workflow (how every book is done)

- **No OCR, ever.** Every figure is read by the model from image crops. No tesseract, Apple Vision, `llm`/
  Gemini, PDF text layers or OCR files — not for transcription and not "just to help". Put this in every
  sub-agent prompt; an agent given a scan and no constraint reaches for a tool.
- **Blank, never guess.** An unreadable figure is never guessed. Transcribe as printed, misprints included;
  re-add every printed total and note whether it reconciles.
- **Two kinds of empty cell (rule of 2026-10-01).** A cell that is empty *in the original* is `""`. A cell we
  could not read is `"[?]"` (the whole cell), plus a transcriber note naming it. Never write partial readings
  such as `"12[?]"`; `[?]` inside longer text marks an unreadable character. The site shows the two
  differently (`[?]` = red hatched "?", `""` = plain empty) for books whose BOOKS entry has
  `"blank_marking": true`; older books, where `""` still means both, keep the grey hatching for every empty cell.
- **Totals may settle 一/二/三 (rule of 2026-10-01).** A printed total never decides a digit — with one
  exception: when the only doubt is how a stack of 一/二/三 strokes groups (三 vs 二一 vs 一二, 二 vs 一一), and
  exactly one of the candidate readings makes the printed row or column total reconcile, use that reading and
  say so in the note ("一/二/三 grouping settled by the printed total"). Read the strokes first and write the
  candidates down before doing the arithmetic; if no candidate reconciles, or more than one does, the cell
  stays `"[?]"`.
- **Short missions, not long batches.** Each sub-agent gets one short mission sized to finish in under an
  hour: 1–3 dense pages/spreads (trade returns, big multi-part tables), 3–5 ordinary table pages (up to 8 if
  that keeps whole tables together), 10–20 pages of pure prose. Draw the boundaries from a contact sheet of
  the whole book so tables rarely cross them; split very long single tables into one-file-per-page missions
  with shared conventions (see `build/example/guidance.md` §4). Long batches (12–30 spreads) ran 5–9 hours per agent, were hard to monitor and lost work to API
  timeouts. Templates: `build/example/BRIEF.md` (rules, formats) and `build/example/MISSION.md` (scope + prompt).
- **Ownership of multi-page tables:** a table is written once, by the mission that owns its first page,
  reading ahead as far as needed; a continuation at the top of a mission's first page is left alone. A killed
  mission's partial file is handed to the next mission with an explicit "finish tables/<file>" instruction.
- **Read from tight crops with headings in view:** crops ≤ ~2000 px wide and ≤ ~25 rows (images are shrunk
  to ~2000 px); paste the header strip onto each chunk of a tall table; don't upscale except to inspect a
  single tiny region.
- **Monitor by files, not elapsed time** (`ls -t tables | head`, the mission's `reports/M_<leaf>.md`). No new
  file for ~30 minutes → stop the mission and relaunch smaller from what is on disk.
- **Check pass at the end:** short re-read missions for tables whose totals don't reconcile, tables with
  gutter columns, and a ~10% random sample.
- Stay under the concurrent sub-agent limit the user sets; launch missions on a rolling basis.

## Building and publishing

- Build: `uv run --with openpyxl build/build_downloads.py`, then `python3 build/build_site.py`. From a worktree that isn't
  next to the book folders, set `STAT_TABLES_ROOT` (see `build/example/guidance.md` §3) or other books rebuild from
  the wrong folder.
- Commit only your own book's files; revert everything else the build touched. Shared code changes go in
  their own backwards-compatible commit.
- Never push to `main`; push your branch and let the main session merge.
- Privacy: GitHub noreply commit identity; never put the user's name, email or other identifying details in
  commits, request headers (User-Agent/From), file metadata or pages.
- Before merging `origin/main`, commit or stash; confirm the merge ran (`git merge-base --is-ancestor
  origin/main HEAD`) and that no conflict markers remain. Generated pages conflict on almost every merge:
  resolve by rebuilding, never by hand (see `build/example/guidance.md` §5).
- Audit agents' "judgement calls": a digit read from its shape, a similar glyph, context, row order or a
  total is blanked, with the partial reading in the note (except under the 一/二/三 rule above).
