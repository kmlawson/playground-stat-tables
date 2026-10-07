# East Asian statistical tables, 1905–1950

Statistical tables (and some directories) printed in yearbooks and handbooks on Japan, Korea, Taiwan, Manchuria and China, in English and in Japanese, LLM-transcribed cell by cell from the page images:

| Book | Page |
|---|---|
| *The Japan Year Book 1905* | [japan-1905/](../book/japan-1905/) |
| *The Japan Year Book 1910* | [japan-1910/](../book/japan-1910/) |
| *The Japan Year Book 1920–21* | [japan-1920-21/](../book/japan-1920-21/) |
| *Report on Progress in Manchuria 1929* (1907–1928) | [manchuria-1929/](../book/manchuria-1929/) |
| *Second Report on Progress in Manchuria 1931* (to 1930) | [manchuria-1931/](../book/manchuria-1931/) |
| *Fifth Report on Progress in Manchuria 1936* (to 1936) | [manchuria-1936/](../book/manchuria-1936/) |
| *Sixth Report on Progress in Manchuria 1939* (to 1939) | [manchuria-1939/](../book/manchuria-1939/) |
| *Manchukuo Directory 1938-9* (English–Japanese business directory) | [manchukuo-directory-1938/](../book/manchukuo-directory-1938/) |
| *Japan-Manchoukuo Year Book 1940* (incomplete scan) | [japan-manchoukuo-1940/](../book/japan-manchoukuo-1940/) |
| *The Manchoukuo Year Book 1942* | [manchoukuo-1942/](../book/manchoukuo-1942/) |
| *Annual Report on Administration of Chosen 1929–30* (Korea) | [korea-1929-30/](../book/korea-1929-30/) |
| *第一次統監府統計年報 1908* (Residency-General statistical annual; Korea, in Japanese) | [korea-tokanfu-1908/](../book/korea-tokanfu-1908/) |
| *朝鮮年鑑 1926* (大正十五年版; Korea, in Japanese) | [korea-nenkan-1926/](../book/korea-nenkan-1926/) |
| *朝鮮年鑑 1940* (昭和十五年度版; Korea, in Japanese) | [korea-nenkan-1940/](../book/korea-nenkan-1940/) |
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
| *The China Year Book 1929–30* | [china-1929-30/](../book/china-1929-30/) |
| *The China Year Book 1938* | [china-1938/](../book/china-1938/) |
| *China Handbook 1937–1943* | [china-1937-43/](../book/china-1937-43/) |
| *China Handbook 1950* | [china-1950/](../book/china-1950/) |
| *China, a Commercial and Industrial Handbook 1926* | [china-handbook-1926/](../book/china-handbook-1926/) |
| *The Progress of Taiwan 1905* (Japanese and English) | [taiwan-1905/](../book/taiwan-1905/) |
| *The Statistical Summary of Taiwan 1912* | [taiwan-1912/](../book/taiwan-1912/) |

> **Warning:** These tables were transcribed by the vision model of Opus 5.5. Before using any of these figures, you must verify specific statistics with the original source which is linked to whenever possible.

## How the figures were transcribed

- Each figure was read from the page image by the vision model of Opus 5.5. No separate OCR engine was used. The hardest tables were read twice independently, with a third reading for every disagreement.
- Figures are transcribed as printed, printers' errors included. Nothing is guessed: in recent books a figure that could not be read is marked **[?]** (red hatching) and explained in a transcriber's note, and a plain empty cell is empty in the original; in older books an unreadable figure is simply left blank.
- Japanese-language books keep the old character forms and give kanji numerals as Arabic figures; they also have English table titles, descriptions and chapter names (LLM translations).
- Wherever a total is printed, the parts were added up and a note records whether they reconcile. Many totals in these books do not, and the notes list each one.

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
