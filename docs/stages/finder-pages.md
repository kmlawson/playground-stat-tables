# Stage: finder pages (Population etc.) — moved from CLAUDE.md on 2026-11-10

Overview of the feature (purpose, what visitors see, how it is built, limits): `docs/2026.11.07-finder-pages.md`.

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
  Population also has `place_moves.json` (figures a spec put at the wrong unit, moved by table and years) and, in
  `config.json`, `place_notes` (a note on a place's page), `link_groups`, `place_up`, `chart_break`; `sources.json`
  (official and scholarly sources per region, shown above every place page; `SOURCES_TASK.md`) and `DATE_TASK.md`
  (date check: figures go under the year measured, never the edition year).
- **Kwantung vs the Railway Zone** (user, 2026-11-09): up to 1936 the empire-wide tables print 關東州及滿鐵附屬地
  (often headed just 關東州/Kwantung) — that is the place `kwantung-zone`, not `kwantung` (the territory alone) or
  `smr` (the zone alone). From 1937 the zone was Manchukuo's. New specs follow `TASK.md`; check new Kwantung
  figures above the territory's own series and add a move when a spec got it wrong.
- **Nothing is re-read:** a spec per table says which rows/columns hold the figure, for which place, date, group and
  basis; the script copies those cells as transcribed. Each spec carries a fingerprint of its table; if the table
  changes, the spec is left out until re-written.
- **Finder batch for every new book with candidate tables** (user, 2026-11-10: "whenever there are tables that need to
  be added to figures page" — part of publishing the book, not batched): build; `python3 build/finders/status.py
  --batches` (tables with no spec, stale specs, new unmatched names, new suspicious figures; writes
  `work/batches/pending-<date>/`); one Sonnet agent per finder on those batches with its `TASK.md`, specs into
  `specs/pending-<date>/`; one agent on `work/new_names.txt` with `ALIAS_TASK.md`; one on `work/new_outliers.txt` with
  `OUTLIER_TASK.md`; build again; look at a few new places; `status.py --baseline`; commit specs + baselines, bump
  version, push. Table pages get their finder link one build after a table's spec (they read `table_links.json`).
- **A new finder:** copy `population/`, change `config.json`, `TASK.md` and the claim fields in `extract.py`/the
  page; `make_previews.py` splits the candidates into batches for the first agents.
