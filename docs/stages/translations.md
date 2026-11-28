# Stage: English layer (title translations) — required for every Japanese, Chinese and Korean book

When: after assembly, before the first build of the book (user, 2026-11-03: no CJK book is published without it).

- Output: `build/translations/<slug>.json` — `"_chapters"` {printed chapter: English}, and per table file (name without
  `.json`) `{"t": English title, "d": one-sentence description}`. One entry per table file, valid JSON.
- One Sonnet agent per ~150 tables, from the JSON only (no images): brief `../_pipeline/kits/ndl-tokei/TRANSLATE_TASK.md`;
  tell it the book's language and romanisation.
- Romanisation in `t`, `d` and `_chapters` (user, 2026-11-28) — these are our own words, so they follow these rules;
  transcriptions never do (they keep the printed romanisation, see CLAUDE.md):
  - Japanese: Hepburn. Korean: McCune–Reischauer.
  - The rules below apply to place names and personal names alike.
  - China and Manchuria: standard pinyin, no tone marks (Jiangsu, Sichuan, Chongqing; 奉天 Fengtian,
    新京 Xinjing, 大連 Dalian, 哈爾濱 Harbin; 孫科 Sun Ke). Romanise the name as printed; don't swap in a later name.
    No Wade-Giles or postal forms.
  - Exception — 關東州 (user, 2026-11-28): always the full phrase "Kwantung Leased Territory" (also for bare 關東州,
    "Kwantung Territory/Province"); institutions "Kwantung Bureau" 關東局, "Kwantung Government" 關東廳,
    "Kwantung Army" 關東軍. Dalian 大連 and Lüshun 旅順 stay pinyin.
  - Taiwan books 1895–1945: Japanese Hepburn reading with pinyin in parentheses: 臺北 Taihoku (Taibei),
    臺中 Taichū (Taizhong), 新竹 Shinchiku (Xinzhu), 高雄 Takao (Gaoxiong), 澎湖 Hōko (Penghu); 林獻堂 Rin Kendō
    (Lin Xiantang). Leave out the parentheses when the two forms are the same (臺南 Tainan) and for Japanese people's
    names (Hepburn only).
  - Known old forms and their conversions, lessons and tools: `build/romanisation/` (README, `conversions.json`).
    Use it for any mass conversion; add new forms to `conversions.json`.
- Title Case; add the date/period when the title or caption gives one.
- Bilingual books: base `t` on the book's own English, tidied (Title Case, obvious misprints fixed), made more explicit
  when terse ("Area" → "Area of the Provinces and Municipalities").
- `d`: what the table gives (rows × columns, units, period, breakdown) — no figures.
- Check a sample of entries and that every table file has one, then build.
