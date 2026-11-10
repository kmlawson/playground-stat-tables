# Stage: Similar tables / Compare (books that belong to a series)

When: after tags, for every book that is an edition of a series — one already on the site, or a second edition that
starts a new series (user, 2026-10-28; 2026-11-10: "whenever there is a series"); skip for one-off books.

1. Add the book to `SERIES` in `build/crosslinks/chapters.py` (series key → slugs in edition order).
2. `python3 build/crosslinks/make_listings.py` — writes the per-series topic listings the agents read.
3. Sonnet agents match the new edition's tables into `build/crosslinks/families/<series>--<topic>.json`:
   - existing series → **update mode**: add the new tables to existing families or open new ones; never reshuffle
     existing families (prompt pattern `build/crosslinks/prompts/NU1.txt` / `KU1.txt`);
   - new series → `prompts/S01.txt` pattern (topic map first: `TOPICMAP_TASK.md`, `topicmap_prep.py`).
4. Record each mission (id, status, topics) in `build/crosslinks/missions.md`; rebuild and check a few Compare panels.
