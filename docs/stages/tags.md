# Stage: controlled tags (topics, detailed tags, text-tables flag)

When: after the book's first build (`data/<slug>.json` must exist), before the publish commit (user, 2026-10-27).

1. `python3 build/tags/new_book_tags.py prepare <slug> [--prior <earlier-edition slugs, comma-separated>]` — writes
   `build/tags/runs/new-<slug>/batches/bNN.json` (40 tables each); `--prior` gives earlier editions' assignments as hints.
2. One Sonnet agent per batch: "Follow build/tags/NEW_BOOK_TASK.md exactly; your batch bNN → results/bNN.json; JSON only".
3. `python3 build/tags/new_book_tags.py apply <slug>` — validates and saves to `build/tags/published/assignments.json`.
4. Rebuild; commit `build/tags/runs/new-<slug>/` and the assignments with the book.

Rules (in `build/tags/README.md`, `CLASSIFICATION.md`, `VOCABULARY.md`): 0–2 high-level topics, 0–3 detailed tags, the
`text-tables` flag only for rosters/lists — and only where a term genuinely fits; `[]` beats a forced term. Agents
must use existing vocabulary IDs and report gaps in `why`.
