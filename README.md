# East Asian statistical tables, 1929–1942

Every statistical table printed in English-language official yearbooks on Japan and its empire, LLM-transcribed cell by cell from the page images:

| Book | Page |
|---|---|
| *The Manchoukuo Year Book 1942* | [manchoukuo-1942/](manchoukuo-1942/) |
| *Annual Report on Administration of Chosen 1929–30* (Korea) | [korea-1929-30/](korea-1929-30/) |
| *The Japan Year Book 1930* | [japan-1930/](japan-1930/) |
| *The Japan Year Book 1939–40* (in progress) | [japan-1939-40/](japan-1939-40/) |
| *The Far East Year Book 1941* (in progress; branch `far-east-1941`) | [far-east-1941/](far-east-1941/) |

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

`build_site.py` regenerates the pages from the per-table JSON files. `build_extra.py` builds the books added on the `far-east-1941` branch (tables, plus directory and chronology pages) without touching the others.
