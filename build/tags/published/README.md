# Website tag data

`assignments.json` is the stable source of website labels, keyed by
`book-slug:table-id`. Transcription JSON remains unchanged. Each record contains
0–2 high-level topics, 0–3 detailed tags, independent flags, the classification stage
and the text/statistical assessment status. An empty flag with unknown status is
not a statistical-content decision.

The export combines the saved China and Korea/Taiwan classifications, the
Japan/Manchuria/South Seas metadata first pass and preserved reviewed pilot labels.
Existing Far East high-level selections remain available pending that collection's
controlled classification. `sources.json` identifies the original local runs.
Approved subsequent corrections live in `overrides.json`, so a fresh export does
not discard a later review.

Run `python3 -B build/build_tags.py` from the repository root to rebuild the topic
pages, public per-book sidecars and table badges from committed transcriptions.
It does not change `data/<book>.json`. The main site builder also includes this
step. `--prepare` re-exports the original locally saved classification runs first;
it is only needed when preparing a new canonical export.

Every high-level topic has a global page and collection pages. Detailed tags and
`text-tables` have global pages with collection/book filters. Legacy `*-crime.html`
URLs continue to work alongside `*-crime-and-justice.html`. Book/year grouping is
remembered in the browser and can be shared through query parameters. Coverage
cells select a book/tag intersection; related-tag links open that tag's own page.

The fixed 7,662-table detailed-review cohort is recorded in
`../reviews/deferred-detailed-tags-2026-10-26.json` and is not consumed by high-level
review.
