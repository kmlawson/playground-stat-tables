# Reference details (read when the task needs them)

Moved out of `CLAUDE.md` on 2026-11-07 so that every session does not load them; the rules are unchanged.

## The `llm` pipeline (`../_pipeline/`) — only when the user asks for it

Claude models called through the `llm` CLI, not sub-agents. `run.py jobs.json N` runs a list of
`{"imgs", "prompt_file", "model", "out"}` jobs in parallel (default `claude-haiku-5.5`; skips existing outputs,
retries rate limits).
- `pipeline.sh <Folder|year>` (`PFX=cyb|jyb|gen` picks the prompt set): contact sheets (`sheets.py`) → Sonnet
  survey per sheet (`*_survey.txt`, finds rotated pages and spreads) → `cyb_jobs.py` builds per-page Haiku jobs
  (`*_table.txt`, `*_dir.txt`) → `run.py` → re-run empty outputs → `cyb_assemble.py` writes `tables/` and
  `directory/` (joins continued tables where column headings match).
- `myb_pipeline.sh <Folder> <pdf>` does the same from a PDF (extracts images first) with the Manchuria Year Book
  prompts, including chronologies (`myb_chron.txt` → `chronology/`). The chronology rule applies here too:
  survey pages of kind "chronology" must go to the chronology prompt, not be dropped.
- `jyb_one.sh <edition>` renders a Japan Year Book PDF from Oma and runs the pipeline; `jyb_pub.sh`,
  `jyb_publish.py`, `cyb_publish.py` add the BOOKS entry (with the standard "read once by Haiku, not checked by eye"
  `gaps` text) and publish. `chapfix.py` normalises chapters; `toc_get.py`/`toc_leaves.py`/`tocmap.py` do the contents.

## Codex and agy runs (`../_codex/`, `../_haiku/`)

Used only for the books the user names (`../queue.md` says which, with the model). `_codex/run_codex.py` runs page
jobs through the Codex CLI (gpt-6.1-sol low; gpt-6-astra low for very difficult tables; at most 2–3 processes);
on a usage limit it writes `<jobs>.pending.json` and the remaining pages go to own sub-agents (Haiku, Sonnet for
complex tables), with job lists in `_haiku/` (BRIEF.md + chunk files in the same job format). agy (Gemini) has no
shell: give it crops already rotated upright and say so in the prompt.

## Toolkits (`../_pipeline/kits/`, copied 2026-10-26)

The paths inside still name the book they came from — edit them first.
- `ndl-tokei/`: NDL statistical yearbooks (from 臺灣統計書 1942): BRIEF, MISSION, `crop.sh`, `validate.py`,
  `dl.sh`, and `plan/` (`make_plan`, `prompt`, `swap`, `status`, `join_frags`, `glue_columns` for column-wise joins,
  `compare`, `normalise`, `skeleton`), and `TRANSLATE_TASK.md` for the English layer.
- `english-yearbook/`: agent missions for English yearbooks (from Japan-Manchoukuo 1939): BRIEF, MISSION, FIX,
  TOC_LOCATE, `crop.sh`, `validate.py`, and `plan/` (`make_plan`, `prompt`, `swap`, `status`, `chapters`,
  `toc_fix`, `toc_merge`, `cmp_trial` for Haiku-vs-Sonnet trials, `mkimg.sh`).
- `chart-debug/`: Node helpers that load `charts.js` (`ct.js` per-table statistics, `vw.js slug:id` views from the
  site root, `dossier.js` review batches, `topic_tags_txt2json.py` → `build/topics/*_tags_N.json`).
- Contents pages: `../_toc/` (`TOC_BRIEF.md`, `get_front*.sh`, `mk_sheets.sh`). Accuracy reviews: `../_review/`
  (`REVIEW_TASK.md`, `SUMMARY_2026-11-04.md`: 99.92% of 3,603 figures; sub-agents return reports as text, they
  cannot write .md files).

## Kanji numerals (display only; user, 2026-11-05)

`build/kanji_nums.js`, inlined in every book page, shows positional numbers (`五〇〇瓦` → `500瓦`, `第一三類` →
`第13類`) as Arabic with an Arabic / As printed switch; the data, CSV, Excel and Full Search keep the printed form.
BOOKS flag `"kanji_full": True` also converts single digits and 十百千 before a unit (`五寸五分`); only 百貨店年鑑
has it. `"kanji_full": "cells"` is for listings whose figure columns hold bare numbers (クーポン旅館一覧 1936): a
cell that is only a number converts whatever its length, and 、 between yen and sen is a decimal point (二、五〇 →
2.50). Grades and ranks stay in kanji (`一級`, `九等`, `二番狸毫`), as do names and lists. When in doubt the rule
leaves the kanji. After changing it, read every comma and decimal conversion.

## Directories

- Directory books can set `dir_cards`, `dir_places`, `dir_pinyin` (place cards, pinyin with "alt. romanization").
  A directory entry may carry `"fields": [[label, value], …]` and `"description"`: the card then shows each field on
  its own line under a bold label, then the description (`text` still holds everything, for search). Hotels in Japan
  1935 does this, with all hotels also as one sortable table whose last column is a scan link (a cell holding only
  an archive.org URL shows as "scan ↗").
- **"label: value" text.** `DIR_FIELDS` in `build/build_site.py` names the books whose directory entries run labelled
  items together, and how they are separated (`dot` " · ", `semi` "; ", `prose` sentences). `split_fields` turns
  them into `f` (one line per field, bold label) and `h` (the text before the first label); `t` keeps everything for
  search. In `prose` a label must recur three or more times in the book, so a misprinted colon after an occupation
  is not taken for a field. Bilingual (English/Japanese) entries are left alone. A new directory with this kind of
  text: add it to `DIR_FIELDS`.

## Charts

`CHART_ALL` in `build_site.py` gives every table of the books with those slug prefixes a Table / Chart / Both switch;
elsewhere only tagged tables. A table printing several measures gets one chart per measure (tabs); earlier-year rows
under a list form their own chart. Labels and year order as printed; printed totals are marked on stacked bars.
`topics/<region>-<topic>.html` lists the tagged tables with a coverage grid.

## Full Search

Pagefind indexes `pagefind/` (everything) and `pagefind-titles/` (titles and names only) are written from the
committed `data/*.json`; `build_search.py` sets nice 15 and cores − 3 threads itself. `robots.txt` and `llms.txt` ask
crawlers to skip them and point to the GitHub data instead. Chinese/Japanese characters are indexed spaced, with
folded (`fold.js`) copies of lines that contain variant forms.

## Reader notes (switched off)

Table, directory and chronology pages can carry an opt-in Notes button that loads the vendored `annotate.js` 1.4.0
(MIT; `annotate.js` + `annotate.LICENSE.txt` at the site root; never load it from a CDN). Notes stay in the reader's
localStorage (project `stat-tables`), keyed per view. Loader and workarounds live in `ANNOT_JS` in `build_site.py`;
no feedback endpoint (user, 2026-10-10). **Switched off** (user, 2026-10-10: "a bit too confusing"):
`NOTES_ENABLED = False` removes the button and loader.

## Map links in more detail

- `build/maplinks.json`: one entry per table (`book`, `table`, `units`, `ids` {printed row: map key}, `columns`,
  `total_row`/`total_col`, `across`, and for places printed more than once `blocks` [+ `block_names`] or
  `split_col` [+ `split_first`]). Address entries by book and table, never by position. `maplinks.py` builds the
  payload; `MAPLINK_SPEC.md` is the contract with the map (the map side is `table-link.js` and
  `docs/table-links.md` in `~/shell/interactive-japan-map`).
- `maplinks_add.py --dry book/table …` proposes entries (prefectures by `match_place`; other units by the gazetteer
  in `build_candidates.py`, read from the map's `texts/territories/sub-units/*.csv`, plus spelling aliases there:
  older Chinese province names, Keian for 平安). `build_candidates.py` also writes the candidates block of
  `support/candidates.html`.
- The build prints `maplinks: … places on more than one row` for an entry whose ids name a place twice (only the
  first row is drawn). About a hundred entries do this harmlessly (a city printed twice); when the rows are parts
  of a whole (內/鮮/外/計, one block per school kind) the entry needs `split_col` or `blocks`.
- `topics/with-maps.html` lists every linked table with area and kind filters; the addresses themselves are in
  `topics/maps/<book>.json`, opened through `topics/map.html?b=<book>&t=<id>` (`build_with_maps`).
