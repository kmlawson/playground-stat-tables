# CLAUDE.md — East Asian statistical tables site

Static site of statistical tables transcribed from English-language yearbooks. The transcriptions (JSON)
live **outside** this repo in each book's `_work/` folder; `build_site.py` regenerates everything here from
them. Several Claude sessions add books at once, each on its own branch — read `example/guidance.md` before
building or pushing anything.

## Transcription workflow (how every book is done)

- **No OCR, ever.** Every figure is read by the model from image crops. No tesseract, Apple Vision, `llm`/
  Gemini, PDF text layers or OCR files — not for transcription and not "just to help". Put this in every
  sub-agent prompt; an agent given a scan and no constraint reaches for a tool.
- **Blank, never guess.** An unreadable figure is `""` plus a transcriber note. Never infer a digit from a
  printed total. Transcribe as printed, misprints included; re-add every printed total and note whether it
  reconciles.
- **Short missions, not long batches.** Each sub-agent gets one short mission sized to finish in under an
  hour: 1 dense page/spread (trade returns, big multi-part tables), 2–3 ordinary table pages, 4–6 prose
  pages. Long batches (12–30 spreads) ran 5–9 hours per agent, were hard to monitor and lost work to API
  timeouts. Templates: `example/BRIEF.md` (rules, formats) and `example/MISSION.md` (scope + prompt).
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

- Build: `uv run --with openpyxl build_downloads.py`, then `python3 build_site.py`. From a worktree that isn't
  next to the book folders, set `STAT_TABLES_ROOT` (see `example/guidance.md` §3) or other books rebuild from
  the wrong folder.
- Commit only your own book's files; revert everything else the build touched. Shared code changes go in
  their own backwards-compatible commit.
- Never push to `main`; push your branch and let the main session merge.
- Privacy: GitHub noreply commit identity; never put the user's name, email or other identifying details in
  commits, request headers (User-Agent/From), file metadata or pages.
