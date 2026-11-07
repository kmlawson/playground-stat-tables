# Finder pages

Pages that gather one kind of figure from every table on the site, place by place and year by year
(`figures/<name>.html`, hub `figures/index.html`). The process is in the repository's CLAUDE.md ("Finder pages"); an overview is in `docs/2026.11.07-finder-pages.md`.

- `finderlib.py` — shared: figures and dates out of transcribed cells, place matching, tables, specs, fingerprints
- `places/` — the gazetteer (`places.json`, rebuilt by `make_gazetteer.py` from the Japanese Empire map) and hand
  matches (`aliases.json`, brief `ALIAS_TASK.md`)
- `registry.py` — what the rest of the build reads (Topics buttons, topic/tag banners, table links, Search)
- `build_all.py` — builds every finder and the hub (end of `build_site.py`)
- `status.py` — the backlog since the last batch (`--batches`, `--baseline`)
- `population/` — the first finder: `config.json`, `TASK.md`, `specs/`, `spec_fixes.json`, `OUTLIER_TASK.md`,
  `extract.py`, `build_population.py`, `check.py`, `make_previews.py`, `page.html`, `baseline/`
