# NDL (National Diet Library) — downloads and catalogue searches

Rules for every request to NDL services (dl.ndl.go.jp, ndlsearch.ndl.go.jp), from scripts and from ad-hoc commands
alike (user, 2026-11-11). They apply equally to sub-agents: say so in a brief that lets an agent touch NDL.

## Everywhere
- **One request at a time.** Never run requests in parallel, never start a second download or search loop while
  one is running, and never fetch two volumes at once.
- **Pause between requests:** at least 5 s for page images and for catalogue queries alike.
- **Back off on failure:** wait 30 s, then 120 s, before retrying; stop and report after the third failure or on any
  HTTP 429/503 rather than retrying in a loop.
- **User-Agent:** a descriptive, non-identifying string such as `stat-tables-site/1.0 (offline statistics
  transcription)`. Never the user's name, email or any contact address, in the User-Agent, a `From:` header or a
  query parameter, even though some APIs invite one.
- Every `curl` gets `--max-time` (60–120 s), so a stalled request cannot hang a loop.

## Page images (digital collections)
- Use `../_pipeline/ndl_dl.sh <Folder>:<pid> [<Folder2>:<pid2> …]`. It fetches the IIIF manifest
  (`https://dl.ndl.go.jp/api/iiif/<pid>/manifest.json`), then each frame at `…/full/full/0/default.jpg` one after
  another, 5 s apart, with the 30/120 s retries. Several volumes go in ONE call, so they run one after the other.
- Run it with `run_in_background`, never with `&`; log to `<Folder>.dl.log`. About 8 s a frame (a 200-frame volume
  takes ~30 min).
- Check `df -h` first (a volume is ~0.5–1 GB of JPEGs).

## Catalogue searches (NDL Search OpenSearch API)
- Endpoint: `https://ndlsearch.ndl.go.jp/api/opensearch?title=…&publisher=…&cnt=…&idx=…` (RSS/XML).
- **Plan the queries first and keep them few:** one broad query with a large `cnt` (up to 500) beats many small
  ones. Page with `idx` only as far as `openSearch:totalResults` requires.
- **Sequential with pauses:** each query in turn with `sleep 5` between them; never a burst of back-to-back
  queries. (On 2026-11-11, 16 queries went out back to back, then a run with 2 s gaps; that was too fast.)
- **Save each response** to a scratch file and parse it locally; re-read the file rather than re-querying.
- Old and new character forms are separate queries (建築學會 / 建築学会); budget for both.
- Quirks: adding `until`/`from` together with `mediatype` or `dpid` returned 0 results; filter dates locally instead.
  A digitised item carries a `dl.ndl.go.jp/pid/<pid>` link in its record; `dcndl:volume` gives the edition
  (e.g. 昭和14年版), and `dc:date` can be the printing date rather than the edition year.
