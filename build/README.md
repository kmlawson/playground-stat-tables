# Old Tables of East Asia

Statistical tables, directories and chronologies printed in yearbooks and handbooks on Japan, Korea, Taiwan, Manchuria,
China and the South Seas Mandate, in English and in East Asian languages, transcribed cell by cell from the page images
by large language models. The books are listed on the [home page](../index.html); how they were read, and how accurate
the readings are, is on the [about page](../about.html). Before using any figure, check it against the original scan
linked under each table.

## Data

`data/<book>.json` holds one record per table:

- `title`, `table_no`, `chapter`, `printed_pages`
- `parts`, each with its `columns` and `rows`
- `footnotes`, as printed
- `transcriber_notes`

In the browser, any column can be sorted by clicking its header (click again to reverse, a third time to restore the printed order), and any table can be downloaded as CSV or copied as TSV.

To rebuild: `python3 build/build_site.py`, then `uv run --with openpyxl build/build_downloads.py` (Excel workbooks and Markdown directories in `downloads/`), then `build_site.py` again so the pages link the new downloads. `build/build_site.py` regenerates the pages from the per-table JSON files. It builds every book, including the Far East Year Book 1941 (read from its own folder), plus the directory, chronology and cross-book search pages.

Adding a book: see [CLAUDE.md](../CLAUDE.md) (the process overview), and [build/example/guidance.md](example/guidance.md) (how to post a branch without clashing and how to run the transcription), [build/example/BRIEF.md](example/BRIEF.md) (template brief for the transcription agents) and [build/example/MISSION.md](example/MISSION.md) (template for short sub-agent missions). 

## Links between editions

Book pages link each chapter, and each recurring table, to the same chapter or table in other editions of the same
series (Japan Year Book; China Year Book; China Handbook; 朝鮮事情 — never across series), with a side-by-side Compare view.

- `build/crosslinks/chapters.py`: hand-made map of matching chapters (topics) per series.
- `build/crosslinks/families/*.json`: groups of the same recurring table across editions, one file per topic, made by
  Claude sub-agents from table titles, captions, column headings and row labels (`listings/`, `prompts/`,
  `missions.md`). Families sharing a table are merged at build time.
- Adding a new edition: add it to its series in `chapters.py`, regenerate the listings for its topics and re-run the
  matching for those topics.

## Full Search index (Pagefind)

`search.html` searches a [Pagefind](https://pagefind.app/) index that is **not kept in this repository** (about
188,000 small files). Build it yourself after building the site, from the repository root:

```sh
python3 build/build_site.py                                  # pages and data/ (needs STAT_TABLES_ROOT for source folders)
uv run --with "pagefind[extended]" build/build_search.py     # writes pagefind/ and pagefind-titles/ (about 8 minutes)
```

On a machine someone is using, run `bash build/search_gently.sh` instead: the same build at macOS background priority
(efficiency cores, throttled disk, 2 threads), written into `_search.noindex/` so Spotlight does not index the files,
with `pagefind/` and `pagefind-titles/` as symlinks to it, a watchdog that pauses the job while free memory is under
25%, and `../search-index-upload.tar.gz` packed at the end. It takes about an hour.

`build_search.py` reads only the committed `data/*.json`, so it works on any checkout. It writes two indexes next to
`search.html`: `pagefind/` (everything) and `pagefind-titles/` (table titles, entry names and chronology headings,
for the "Titles and names only" option). Upload both folders with the site. Without them the search page says the
index is not installed; the rest of the site works as before. Serve the site over HTTP (for example
`python3 -m http.server`), not from `file://`.
