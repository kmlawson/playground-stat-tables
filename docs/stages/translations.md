# Stage: English layer (title translations) — required for every Japanese, Chinese and Korean book

When: after assembly, before the first build of the book (user, 2026-11-03: no CJK book is published without it).

- Output: `build/translations/<slug>.json` — `"_chapters"` {printed chapter: English}, and per table file (name without
  `.json`) `{"t": English title, "d": one-sentence description}`. One entry per table file, valid JSON.
- One Sonnet agent per ~150 tables, from the JSON only (no images): brief `../_pipeline/kits/ndl-tokei/TRANSLATE_TASK.md`;
  tell it the book's language and romanisation.
- Romanisation: Hepburn for Japanese, McCune–Reischauer for Korean, the period's Wade-Giles/postal forms for Chinese
  (Kiangsu, Szechwan, Chungking — never pinyin). Title Case; add the date/period when the title or caption gives one.
- Bilingual books: base `t` on the book's own English, tidied (Title Case, obvious misprints fixed), made more explicit
  when terse ("Area" → "Area of the Provinces and Municipalities").
- `d`: what the table gives (rows × columns, units, period, breakdown) — no figures.
- Check a sample of entries and that every table file has one, then build.
