# LESSONS.md — what table extraction has taught us, by kind of volume

Short, case-specific lessons (2026-09 to 2026-11). The rules themselves are in `CLAUDE.md`; this file says what goes
wrong and what to do about it. Add a line when a book teaches something new.

## Choosing whether a scan is worth it
- Pilot first: one mission, then count `[?]`/blank cells. 朝鮮年鑑 1941 (NDL, 5068 px per spread, 2–3 kanji digits per
  cell) came out ~68% blank and was abandoned after 12 of 50 missions.
- Sharp 400 dpi bilevel (NLC/Commons 1935 統計提要) and 6,000 px NDL spreads read cleanly; 300 dpi bilevel with broken
  or doubled type (Commons SSID 1947) gives ~1.5% `[?]` after the first reading.
- Downloads: one request at a time, a few seconds apart, descriptive non-identifying User-Agent. Commons: use the API
  (`prop=imageinfo`) for the file URL; `pdfimages -png` keeps bilevel pages lossless.

- DjVu (Commons/CADAL): `ddjvu -format=pbm -page=N` then `magick x.pbm full/pNNNN.png` (~0.6 s a page; writing a
  bilevel PNG straight from TIFF with `-type bilevel` took 5 s a page). Commons `&page=N` is the DjVu page.
- 民國叢書 photo-reprints (CADAL, 第一次中國教育年鑑 1934) can be badly broken type: 4 prints like 1, 3/5/8 and 0/6/9 lose
  strokes; contact-sheet quality ratings miss it (pages rated "good" gave 50% [?] to Sonnet). Sample full-res crops first.

## By kind of volume
- **Vertical Japanese with kanji (stacked-stroke) numerals** (NDL 統計書, 行政年報, 朝鮮年鑑): Opus. A Sonnet trial on a dense
  kanji page (1925) got 15 of 39 count cells right and modernised characters; Opus got 84/84. The 一/二/三 grouping
  rule exists for these tables. Tell agents to keep old forms (數, 縣, 淸).
- **Horizontal Japanese/Chinese with Arabic figures** (統計年鑑, 統計書, 統計提要): Sonnet is reliable (Opus checks
  99.7–100% agreement); Haiku for light single-page tables. Opus only for very dense small type (1935 county tables).
- **Vertical Chinese with compressed place-value numerals** (二〇、六五五, two digits to a cell; 第一次中國教育年鑑): Sonnet
  left ~50% [?] and misread unflagged figures (independent check 94%); Opus with 4× crops and row/column re-adding
  is usable. Broken Arabic type in the same book: Sonnet 98.7%, Haiku poor (wrong page, failed ratios) — use Opus.
- **English yearbooks** (IA, Google scans): Haiku for most pages; bold faces make 3/8 look alike (hence the 3-vs-8 rule).
  Google scans repeat and omit pages — check printed page sequences on the contact sheets. IA leaf = file no. − 1:
  keep `build/leafmaps/<slug>.json` when the viewer counts differently.
- **Bilingual tables** (Taiwan 1905, 統計提要 1947): keep both languages in titles, headings and row labels
  ("江蘇 Kiangsu"); the English layer still needs `t`/`d` per table.
- **Directories / Who's Who** need their own DIRECTORY missions (Sonnet); mixed into table missions they are skipped or
  half-done.
- **Chronologies**: transcribe everywhere except the Japan Year Books; the llm pipeline once skipped them silently.

## Layout traps
- **Sideways pages**: rotate them upright in `full/` and `plan/` before any mission (the 1947 abstract had 98 of 145);
  record rotations in `plan/rot.txt`. Agents told "already rotated" read them without trouble.
- **Landscape ≠ sideways**: most landscape frames are wide tables printed upright. Survey with a ROT column (0/cw/ccw).
- **Wide tables split over two frames** (row labels on the left frame only): one reader for both frames; match rows by
  order and count them. Figures printed half a line below their labels are also matched by order — say so in the notes.
- **Sub-tables** (❶ ❷ …, (甲)(乙)) that each start a frame: surveys mark them as STARTs, so planners cut missions there.
  The owner of the first part must stop at the next sub-table heading; a mission whose first frame begins a sub-table
  writes it as its own file with the same `table_no`, merged at assembly. (表32 in 1935 was edited by two agents at once.)
- **Very long tables** (表230 in 1935, ~290 pages of monthly accounts): one file per printed sub-table (province), each
  month a part — never one giant file. Tables over ~15k cells crash mobile Safari (Radio 1934 table 4): split them.
- **Tables continued elsewhere** ("NNN頁へ續く") must be joined in reading order; column-wise continuations (Nanyō
  統計年鑑) need a column join, not `join_frags.py`.
- **Check the files, not the report**: a mission report said 1935 表68 had places in rows while its neighbour had them
  in columns; the files were in fact consistent. Inspect the JSON before transposing or re-planning anything.
- **Repeated sheets** (one month per page, e.g. 表230): readers split a month differently — one part, or 收入/支出 halves.
  Fix the part scheme in the brief. Fragment missions also write a NEW sub-table (next province) as a fragment:
  regroup all pieces by the heading in each caption, inheriting it on frames without one (`plan/assemble.py`, 1935).
- **Joining fragments**: identical row labels do not mean the same part — a new month or sub-table with the same rows
  stays a new part; append columns only when the fragment's label is empty or names the same sub-table. Run
  `validate.py` after every join (a fragment lacking its row-label column heading broke 表209's widths).

## Missions and agents
- Plan missions from the survey, never fixed leaf counts: group frames into table runs, keep a multi-frame table in one
  mission, cut only very long runs into fragment missions (`tables/frag/<leaf>_0.json`, joined by `join_frags.py`).
- Boundaries still produce duplicates (both neighbours write a piece) and orphans (each leaves it to the other). After
  the missions: check `table_no` coverage against the contents, move duplicates to `tables_dup/`, send one small fix
  mission for orphans.
- Haiku gives up on long multi-frame missions and over-marks clear figures `[?]` when totals do not reconcile; keep it
  to light single-page tables and tell it to write what it reads. Exception: repetitive one-sheet-per-frame accounts
  (~200 figures a frame) went well in 7-frame Haiku missions (1935 表230; spot check 179/180).
- Some readers copy row labels from the previous frame with the same layout instead of re-reading them (1935 表315):
  tell them to read labels on every frame.
- Scale: a 1,312-page abstract (1,035 table pages) planned at ~4–5 frames a mission gave 228 missions, about 10 hours
  of wall time at 5–10 agents, plus a quota pause.
- Opus readers extend the total rule to other digit pairs (1/4, 0/6/9) when type is broken; say "only 一/二/三 and
  3-vs-8" in the prompt itself. Cells settled otherwise were turned back to [?] at assembly (`plan/unsettle.py`, 1934).
- Agents mislabel chapters (e.g. 第七類 for 第十類): normalise every chapter at assembly from the divider frames.
- Agents sometimes write partial readings (`243,8[?]0`), stray characters (`€31號`) or missing decimal points as read —
  normalise at assembly (whole-cell `[?]` plus a note with the partial reading).
- **No `rm` in agents** (user, 2026-11-10): deletes trigger permission prompts. Crops stay in `crops/`; the book's work
  files are cleaned up once when it is finished. Never put `rm` in a chained command.
- Agents may stall for hours after finishing (and a quota pause can stretch a mission to 7 h): if the report and output
  are complete, stop it. Check that fragment files still have `parts` after a final rewrite.
- Give each agent its own script names; one translation agent once ran another session's scratch script.
- Survey agents can each take ~18 contact sheets (144 frames) in 1–3 minutes.

## Checking
- Second readings of Arabic-numeral tables almost always confirm the first (League report 1925: ~3,000 cells, one
  difference); non-reconciling totals are usually source misprints. Keep them as printed with a note.
- When a rough scan leaves many `[?]`, one blind Opus re-read of just those cells (values hidden; `plan/make_blind.py`)
  settles about half (1947: 122 of 266). Worth it for rough scans, not for clean ones.
- Opus review of Haiku/Sonnet samples (2026-11-04): 99.92% of figures right (統計提要 1935 spot check 2026-11-10: 1648/1649); the errors are labels (modernised or
  truncated kanji, a vertical range dash read as 一) and over-cautious `[?]`.

## English layer
- Translation agents tend to script generic descriptions from the titles alone (done in three tool calls). Tell them
  to read each table's column headings and row labels, and sample a few entries per batch before building.

## Contents (toc.json)
- Transcribe the printed contents FIRST, with every listed section, before the missions; place unpaged entries from
  survey/mission headings, never a separate re-read of the book (one such pass cost a week's quota).
- Sonnet guesses smudged page numbers and calls its own misreads "misprints": re-read every uncertain or out-of-sequence
  entry from a tight crop. Contents pages can carry their own page numbers (-1-, -2-): exclude them from the page→leaf
  map or they collide with body pages.

## Publishing
- Branch with `--no-track` and push `refs/heads/<branch>:refs/heads/main` explicitly: a tracking branch once pushed
  straight to `main`.
- Population finder: new places need aliases; check new aliases against the gazetteer (an agent made a duplicate
  "British North Borneo"); a spec fix can make an older `place_moves.json` entry redundant ("matched nothing").
- County-level population tables bring hundreds of unknown places (the gazetteer has no Chinese counties: ~530 from
  1935). Run several alias agents on slices, each writing a proposal file (never `aliases.json` itself); merge them
  and check for duplicate ids and missing parents. A city is not the county of the same name.
- `cp`/`mv` are interactive aliases and unmatched globs abort commands: use `\cp -f`, `\mv -f`, `>|`, `>>|` (noclobber).
- **Regular spread books with a full contents** (朝鮮防疫統計 1939: frame = 8 + page/2 throughout): the contact-sheet
  survey can be skipped — plan missions from toc.json page numbers, confirm the mapping on a few frames (first table,
  colophon) and write a synthetic `plan/survey.json` for toc_leaves.py. Sonnet still normalises '1.376'→'1,376' and
  modernises 齡/查/清 even when told not to: restore from notes and normalise at assembly.
- **A second edition with the same layout** (朝鮮防疫統計 1938 after 1939: same 76 tables, same page numbers): copy the
  first edition's tooling, survey.json and brief; read only the new contents to confirm; launch missions as frames
  download (`plan/ready.py`, `plan/slots.py`); derive the English layer and Similar-tables families by table number and
  shift the years — no translation or matching agents needed. Publication data is in the colophon at the very back.
