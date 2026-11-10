# Stage: chart topic tags and map links

**Topic tags for charts** (user, 2026-10-22/23): `build/topics/<region>.json` (`{"slug:id": [[topic, subtopic], …]}`;
topics population / education / religion / crime; subtopics in `build_site.SUBTOPICS`). Sonnet agents from title
listings with `build/topics/TOPIC_TASK.md` (regional variants `TOPIC_TASK_CN/JP/TW/MN/SS/FE.md`). Charts draw only
printed figures: `[?]`, blanks, dashes and ditto marks are gaps, never filled; printed totals are marked and parts
that do not add up show ≠. Never italicise CJK text.

**Map links** ("View as Map": tables by prefecture, province, island group, city or country):
`python3 build/maplinks_add.py --dry <slug>/<id> …`, check, then run without `--dry`; after the build check the
`maplinks:` lines for unplaced rows and places on more than one row. Details in `docs/reference.md` ("Map links").
