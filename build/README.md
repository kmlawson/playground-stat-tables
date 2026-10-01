# East Asian statistical tables, 1929–1942

Every statistical table printed in English-language official yearbooks on Japan and its empire, LLM-transcribed cell by cell from the page images:

| Book | Page |
|---|---|
| *The Japan Year Book 1905* | [japan-1905/](../book/japan-1905/) |
| *The Japan Year Book 1910* | [japan-1910/](../book/japan-1910/) |
| *The Japan Year Book 1920–21* | [japan-1920-21/](../book/japan-1920-21/) |
| *The Manchoukuo Year Book 1942* | [manchoukuo-1942/](../book/manchoukuo-1942/) |
| *Annual Report on Administration of Chosen 1929–30* (Korea) | [korea-1929-30/](../book/korea-1929-30/) |
| *朝鮮年鑑 1926* (大正十五年版; Korea, in Japanese) | [korea-nenkan-1926/](../book/korea-nenkan-1926/) |
| *朝鮮事情 1935* (Korea, in Japanese) | [korea-1935/](../book/korea-1935/) |
| *朝鮮事情 1940* (Korea, in Japanese) | [korea-1940/](../book/korea-1940/) |
| *朝鮮事情 1942* (Korea, in Japanese) | [korea-1942/](../book/korea-1942/) |
| *朝鮮事情 1943* (Korea, in Japanese) | [korea-1943/](../book/korea-1943/) |
| *朝鮮事情 1944* (Korea, in Japanese) | [korea-1944/](../book/korea-1944/) |
| *The Japan Year Book 1930* | [japan-1930/](../book/japan-1930/) |
| *The Japan Year Book 1935* | [japan-1935/](../book/japan-1935/) |
| *The Japan Year Book 1939–40* | [japan-1939-40/](../book/japan-1939-40/) |
| *The Japan Year Book 1946–48* | [japan-1946-48/](../book/japan-1946-48/) |
| *The Far East Year Book 1941* | [far-east-1941/](../book/far-east-1941/) |
| *The China Year Book 1912* | [china-1912/](../book/china-1912/) |
| *The China Year Book 1921–22* | [china-1922/](../book/china-1922/) |
| *The China Year Book 1929–30* (in progress) | [china-1929-30/](../book/china-1929-30/) |
| *China Handbook 1937–1943* | [china-1937-43/](../book/china-1937-43/) |
| *China Handbook 1950* | [china-1950/](../book/china-1950/) |

> **Warning:** These tables were transcribed by the vision model of Opus 5.5. Before using any of these figures, you must verify specific statistics with the original source which is linked to whenever possible.

## How the figures were transcribed

- Each figure was read from the page image by the vision model of Opus 5.5. No separate OCR engine was used.
- Figures are transcribed as printed, printers' errors included. A figure that could not be read is left **blank** and explained in a transcriber's note; nothing is guessed.
- Wherever a total is printed, the parts were added up and a note records whether they reconcile. Many totals in these books do not, and the notes list each one.

## Data

`data/<book>.json` holds one record per table:

- `title`, `table_no`, `chapter`, `printed_pages`
- `parts`, each with its `columns` and `rows`
- `footnotes`, as printed
- `transcriber_notes`

In the browser, any column can be sorted by clicking its header (click again to reverse, a third time to restore the printed order), and any table can be downloaded as CSV or copied as TSV.

To rebuild: `uv run --with openpyxl build/build_downloads.py` (Excel workbooks and Markdown directories in `downloads/`), then `python3 build/build_site.py`. `build/build_site.py` regenerates the pages from the per-table JSON files. It builds every book, including the Far East Year Book 1941 (read from its own folder), plus the directory, chronology and cross-book search pages.

Adding a book from another session: see [build/example/guidance.md](example/guidance.md) (how to post a branch without clashing and how to run the transcription), [build/example/BRIEF.md](example/BRIEF.md) (template brief for the transcription agents) and [build/example/MISSION.md](example/MISSION.md) (template for short sub-agent missions). [CLAUDE.md](CLAUDE.md) summarises the workflow for Claude sessions.

## Links between editions

Book pages link each chapter, and each recurring table, to the same chapter or table in other editions of the same
series (Japan Year Book; China Year Book; China Handbook — never across series), with a side-by-side Compare view.

- `build/crosslinks/chapters.py`: hand-made map of matching chapters (topics) per series.
- `build/crosslinks/families/*.json`: groups of the same recurring table across editions, one file per topic, made by
  Claude sub-agents from table titles, captions, column headings and row labels (`listings/`, `prompts/`,
  `missions.md`). Families sharing a table are merged at build time.
- Adding a new edition: add it to its series in `chapters.py`, regenerate the listings for its topics and re-run the
  matching for those topics.
