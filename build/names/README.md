# Places: the draft place-name glossary (`places.html`)

Asked for on 2026-11-28: a page linked from About with a searchable table of every place name in our books. Each
place has:
- its characters in four forms: traditional Chinese, simplified Chinese, old Japanese forms, new Japanese forms;
- pinyin, Wade-Giles, postal and other spellings, Hepburn and McCune–Reischauer;
- Mongolian in romanisation and in script;
- the adopted standard form (Manchukuo, Kwantung Leased Territory);
- latitude and longitude, for points only;
- a link to its World Historical Gazetteer (WHG) record.

Former names are marked sub-entries, e.g. 北平 Beiping under Beijing and 新京 Xinjing under Changchun.

**Draft rule:** a cell holds only forms our books already use. Nothing is converted or filled in to complete a row.
Computed readings (pypinyin, pykakasi) only decide which column and which name an attested form belongs to.

## Files

- `collect.py` writes `glossary.json`. Its sources:
  - the Population finder's claims, i.e. the printed labels matched to the gazetteer;
  - `finders/places/aliases.json`;
  - our translations: a form counts only if the entry's own table prints that place's characters.

  Run it with `nice -n 15 uv run --with pypinyin --with pykakasi python3 build/names/collect.py`, which takes about
  30 seconds. It also writes `suspects.tsv`: Population-finder labels it rejected because a Chinese county was matched
  to a Japanese or Korean town with the same characters (e.g. 清水 "Tsingshui" matched to Shimizu).
- `former.json` is hand-made. It gives a place's present-day name and its former names with dates (e.g. 北平 Beiping,
  1928–1949), and Mongolian forms such as Kalgan. Add places as they come up.
- `shinjitai.json` is generated from OpenCC (jp2t and s2t, character by character). It is used to tell new Japanese
  forms and simplified Chinese apart from old forms. A simplified character also has to be outside Big5.
- `whg.py` writes `whg.json`. It uses WHG's legacy name search, which needs no token but is deprecated in favour of
  the token-based Reconciliation API. It is gentle: one request every 3 s, responses cached in
  `~/.cache/stat-tables-names/whg/`, and it stops on HTTP 429 or 5xx. A match is accepted only if:
  - for towns and cities, the WHG record lies within 25 km of our point;
  - for areas, the title matches, the feature class is administrative and the country code is right.
- `hangul.json` holds Hangul for every Korean place. This is reference data the user asked for, and it is not printed
  in our books, so the page marks it as added and the database stores it with `attested = 0`. Sources: the map's
  `korea.csv` and `stations.csv`, otherwise the `hanja` package's Sino-Korean reading. Every entry was checked by eye;
  three gazetteer errors were corrected (城津, 興南, 沙里院). `today` gives the present-day name (서울, 김책).
- `db.py` writes `data/place-names.sqlite`, the database to query and build on. Every form is preserved. Tables:
  - `places`
  - `names`: present-day, main, former name or other form
  - `forms`: with system and `attested`
  - `attestations`: every label as printed, with book, table and URL
  - `namesakes`
  - `checks`
  - `suspects`
  - views `v_forms` and `v_namesakes`
- `build_names.py` writes `places.html` and `data/places.json`. `build_site.py` runs it after the finder pages.

## Added forms (user, 2026-11-28)

On request, the glossary now goes beyond what the books print. Every added form is marked: dotted on the page,
`attested = 0` and `sources = 'added: …'` in the database.
- **Pinyin** is added for Chinese place names (China, Manchuria, Kwantung, Taiwan) whose reading is unambiguous. A
  name with a character from `POLY` gets none, unless pypinyin's phrase dictionary knows the whole name. `POLY` lists
  characters whose reading varies in place names: 長 (Changchun, but Zhangzi), 朝 (Chaoyang), 樂 (Laoting, Yueqing,
  Leshan), 六 (Lu'an), 蔚, 單, 洞 and others. About 650 names were added and about 70 left out. Compound labels
  (租界, 設治局 …) get none.
- **Hepburn** is added from the gazetteer's own name for Japanese places, and for the map's Korean and Taiwanese
  cities and provinces.
- **McCune–Reischauer and Hangul** for Korean places come from `hangul.json`. Its sources are the map, the station
  list, the gazetteer, and 15 names supplied by hand; all were checked by eye.

The page's "only forms printed in the tables" toggle hides the added forms and also the forms found only in our
English translations, which are shown in italics. The database's `in_tables` flag marks forms printed in a table.

## Wikipedia (2026-11-28)

`wiki.py` reads the lead name infoboxes of English Wikipedia articles into `wiki.json`. The first run took 18 requests,
batched 50 titles at a time, one request every 5 s, with maxlag, cached in `~/.cache/stat-tables-names/wikipedia/`,
and it stops on any error.

An article counts as the right place only if:
- for a town or city, its coordinates lie within 25 km of ours (220 places);
- for a province, it is the map's own link **and** its infobox gives the same characters or Hangul (43 places).

The second check exists because the map links a Taiwanese gun to its whole prefecture, Lungkiang 龍江 to Heilongjiang,
and Sankiang to a general article. Places that cannot be checked this way are not looked up.

`collect.py` (`wiki_forms`) sorts what it reads into columns:
- characters into the four character columns;
- pinyin with tones (minus "Shì"), Wade-Giles (tone numbers removed), postal and other spellings, Hangul,
  McCune–Reischauer, romaji;
- Mongolian into its two columns (Cyrillic and script, and romanised).

The second name blocks of Infobox Chinese go to the row with those characters (新京 under Changchun). A name our books
never print becomes a sub-row "other name (Wikipedia)" (盛京 Shengjing under Shenyang). Romanised alternates go to the
row whose characters they read (Antung and Andong go to 安東). Every such form is marked added, with the article as its
source.

## Same characters, different places

The rule: a printed label goes only to the place in the table's region.
1. `collect.py` checks every label whose characters also name a gazetteer place in another region group (China with
   Manchuria and Kwantung; Korea; Japan with Karafuto; Taiwan; the South Seas). For example, 安東 is Andong in Korea
   and Andong in Manchuria, and 松江 is Matsue and Sungkiang.
2. The table's region comes from the finder spec's "in", else from the book (china-, korea-, taiwan-, manchukuo-,
   South Seas books).
3. A label stays with its place if the regions agree. It moves to the namesake if the table is about the namesake's
   region. It is left out if neither fits.
4. If the table's region is unknown (empire-wide books), the label is kept and logged. The table's other rows may
   confirm the place but never move it.
5. Translation forms that fit two namesakes are kept only when the book's region decides between them.

Results are in `same_name_checks.tsv` and in the database's `checks` table. The world-level duplicates of East Asian
places (w-weihaiwei, w-manchukuo, w-hongkong…) count as China (`GROUP_OVERRIDE`). Grouping keys strip one
administrative suffix (市 府 縣 郡 …) but never 州 or 道 (全州, 北海道), and never down to one character; within one place,
臺北州/臺北 and 萩市/萩 are merged.

## How a form is placed

- **CJK forms:**
  - In China books, a form goes to traditional Chinese, or to simplified if it has a simplified-only character.
  - In Japanese, Korean, Taiwan and South Seas books, it goes to old forms, or to new forms if it has a new-form
    character.
  - Manchukuo tables count as Japanese if they print kana.
- **Romanised forms:**
  - pinyin and Wade-Giles if the form matches the reading of the name's characters;
  - Hepburn if it matches the map's Hepburn form, a Japanese reading, or has ō/ū;
  - McCune–Reischauer if it matches the map's form or has ŏ/ŭ;
  - adopted standard if it is in `romanisation/conversions.json` "keep";
  - otherwise "postal or other".
  - For Taiwan, a form that is both pinyin and Hepburn (Tainan) counts as Hepburn.
- **Rows:**
  - the main row is the present-day name (from `former.json`, else the name whose pinyin matches the gazetteer's,
    else the gazetteer's own);
  - other character names become sub-rows: "former name" if `former.json` lists them, else "other form";
  - postal and Japanese-reading forms go to the row whose name they romanise (Mukden goes to 奉天).

## Review of 2026-11-28

Four Sonnet reviewers checked the data, each on a slice (China and Manchuria; Korea and Taiwan; Japan and the rest;
integrity and links). Their reports are in the session's scratchpad. The fixes are in the code, plus
`corrections.json` (hand merges, drops and moves).
- **Wikipedia parsing:** templates are now resolved (`{{wg-apos}}`, `{{nobold}}`, `{{unbulleted list}}`…) and only
  pure CJK runs are kept. Infobox labels (Abbreviation, Official name) are rejected, and templates nested in the
  settlement box (a mayor's name) are skipped. Traditional and simplified are now told apart with OpenCC, not Big5.
  Articles of the wrong level are rejected (a prefecture's for a city, a city's for a province).
- **Translations:** "Kyoto City" and "Osaka Prefecture" now go only to the unit of that kind, and a bare "Tokyo" that
  could be either is left out. Trailing descriptors are not kept.
- **Labels:**
  - katakana names are kept whole (マニラ市, not 市);
  - lowercase glosses ("new boundaries") and 1–2 letter fragments are dropped;
  - "Mit[o]" becomes Mito;
  - spellings with an acute é (Kobé) and Wade-Giles shapes without hyphens go under "other".
- **Pinyin:** the variable-reading list now overrides pypinyin's phrase dictionary (朝陽 is Chaoyang), with 琿 渦 濬 曾
  added, and 陝西 is Shaanxi. Countries and compound labels get no added pinyin.
- **Same-name check:** labels from Chinese books are now checked for every place outside China (Vinh had 榮縣), and
  for the alias file too.
- **WHG matching:** a town's record must be a populated place, titled with one of our names, within 25 km. Two
  places may not share a record. Xi'an→Xianyang, Yichang→Xiaoxita and Shaanxi→Shanxi are gone.
- **Data:**
  - Duplicate gazetteer ids are merged in the glossary: 14 Tokyo wards, seven Taiwanese cities, Rehe, Chahar,
    Suiyuan, Xinjiang and others.
  - 見谷面 is 현곡면 / Hyŏn'gok-myŏn.
  - Present-day names were added for Benxi, Siping, Yilan, Yantai, Wanzhou, Tengchong, Pu'er, Hebei (直隸) and for
    North Korean towns.
  - The region tags of kwantung-zone and of the Republic's 1945–47 provinces were corrected.

## Converted character forms (2026-11-28)

`converted_forms()` in collect.py fills the character columns with OpenCC (`t2s`, `t2jp`, `jp2t`), converting whole
names so that its phrase tables settle ambiguous characters (乾縣 → 乾县, 後里 → 后里, 臺灣 → 台湾).
- **Every Japanese empire place (tag em)** gets old and new Japanese forms.
- **Every Taiwan, China, Manchuria and Kwantung place** gets traditional and simplified Chinese.

A name without variant characters gets the same characters in the other column. If our books print no characters,
the base is the gazetteer's name (or `corrections.json` "cjk" for the two places with none). Katakana names count as
both old and new forms. Every converted form is marked added, with its source.

## Page features (2026-11-28)

- **Years.** Every form and name row carries the first and last edition year of the books that print it (`fy`, `yrs`
  in glossary.json; `first_year`/`last_year` in the database's forms and names, `year` in attestations). Example:
  Changchun is printed 1914–1932, Hsinking/新京 1934–1942. These are the books' years, not the years the names were
  in use.
- **Evidence.** "printed in N tables" opens every label as printed, grouped by book, linking to each table
  (`book/<slug>/#<table id>`). The list comes from `data/places-evidence.json`, loaded on first use; the page needs
  http(s) for this, not file://. Places on the Population page link there (`figures/population.html#p=<id>`).
- **Permanent links.** `places.html#<place id>` shows one place, with its evidence open. `places.html#in=<id>`
  lists the places within a unit, and each entry links its parent ("in Hénán") and its contents ("110 places in
  it"). Parent headings come from glossary.json "parents".
- **Variant-insensitive search.** A character map built in `build_names.variant_map()` groups variants with
  union-find, over the site's simplify tables (traditional→simplified, old→new Japanese) and OpenCC's lists in
  shinjitai.json. With it 台北 finds 臺北 and 満洲 finds 滿洲. Only the groups of characters our data uses are embedded.

## Not yet

- The ~13,000 labels the gazetteer does not know (mostly counties) are not in the glossary.
- The Mongolian script column is empty: our books do not print it.
