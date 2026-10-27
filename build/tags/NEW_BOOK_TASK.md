# Tagging task — one batch of a newly published book

Site directory: `/Users/kml/shell/projects/yearbooks/japanyearbooks/stat-tables-site`

You classify existing transcriptions; you do not transcribe or correct anything. No OCR, no images.

Read first:
1. `build/tags/README.md` — the classification rules (subject vs measure, boundaries, text tables).
2. `build/tags/CLASSIFICATION.md` — later decisions that take precedence.
3. `build/tags/VOCABULARY.md` — the 32 high-level topics and the detailed tags with definitions.
   `build/tags/vocabulary.json` has the inclusion/exclusion notes when a boundary is unclear.

Input: your batch file `build/tags/runs/new-<slug>/batches/bNN.json`. Each record gives one complete table: original
title, English title/description (`en`), chapter, caption, every part's label, columns and row labels, footnotes.
`prior`, when present, is the saved assignment of a table with the same title in an earlier edition of the same
series. It is a hint, not an answer: many earlier records come from a title-only first pass. Check it against this
table's columns and rows; keep it when it fits, improve it when the content supports more or different terms.

Output: `build/tags/runs/new-<slug>/results/bNN.json` — a JSON list with one object per input record, same order:

```json
[{"key": "nanyo-tokei-1933:p0022_1", "topics": ["geography"], "tags": ["land-area"], "flags": [], "why": "area by island group"}]
```

- `topics`: 1–2 high-level topic IDs (principal subject first); `[]` only if no topic can be decided.
- `tags`: 0–3 detailed tag IDs, most useful first. **Only where a vocabulary term genuinely fits the subject of the
  table** — leave `[]` rather than forcing a term. Do not tag incidental rows, units or places.
- `flags`: `["text-tables"]` only for textual tables (rosters, lists of offices, reference lists); otherwise `[]`.
- Use only IDs that exist in the vocabulary. Never invent IDs. If a useful term is missing, say so in `why`.
- `why`: a few words of evidence.

Write the file with python3 `json.dump(..., ensure_ascii=False, indent=1)`. Check that it has exactly one object per
input record with matching keys. Reply in at most 4 lines: records written, how many with tags, any vocabulary gaps.
