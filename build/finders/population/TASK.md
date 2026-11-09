# Population page — table specs (agent brief)

The site *Old Tables of East Asia* is getting a **Population** page: a visitor picks a place (a country, colony,
prefecture, province, city, district …) and sees every population figure our transcribed tables give for it, year by
year, with links to the tables. Contradictory figures from different tables are shown side by side.

Your job: for each candidate table in your batch files, write a short **spec** saying how to read population figures
out of it. A script then pulls the actual numbers from the transcribed JSON using your spec. You never copy figures.

## Ground rules

- Work only from the batch previews and, when a preview is not enough, the full table in
  `data/<slug>.json` (a JSON list of tables; find the one with `"id"`). Never open scans or images, never use OCR.
- Do not change any file except your own output files.
- Be quick. Most tables take one line. Skip anything that is not a count of people or households for a place.

## Input and output

Your batch files: `build/population/work/batches/<AGENT>/bNN.txt`. Each table starts with
`### <slug>:<id> | book | ch: chapter | p.printed page`, then `T:` title, `EN:` English title (for CJK books),
then for each part: `part N (R rows) cols: [0]… | [1]…`, the first two rows and the last row in full (`rN: a | b | …`),
and the other rows' labels only (column 0). Open `data/<slug>.json` if you need the rest of a row.

For each `bNN.txt` write `build/population/work/specs/<AGENT>/bNN.json`: a JSON **list** with exactly one object per
table in the batch, in order. Write each file as soon as its batch is done (so work is never lost). If an output file
already exists and is complete, skip that batch. Check each file parses (`python3 -c "import json,sys;json.load(open(sys.argv[1]))" FILE`).

## What counts

Counts of **people** (total, male, female) and **households** (戶數/戸數) for a **place at a date**, including
population of one group in a place (Japanese residents in Korea, Koreans in Japan, foreigners in Shanghai, Chinese in
Taiwan, islanders in the South Seas …). Also estimates (e.g. Customs estimates of China's provinces).

Not wanted (`skip`): births, deaths, marriages, rates, densities, percentages, increases, age groups other than the
total, occupations, pupils, members of an institution, workers, emigrants/passengers moving in a year, area-only
tables, prose. A table of age groups or occupations whose **total** row/column gives the whole population of a place
IS wanted, for that total only.

## Spec format

Skip: `{"t": "<slug>:<id>", "skip": "births only"}` (reason: 2–5 words).

Use: `{"t": "<slug>:<id>", "x": [ {extractor}, … ]}` — one extractor per part/layout you read. Keys (omit defaults):

| key | meaning |
|---|---|
| `part` | part index (default 0) |
| `rows` | what the row labels are: `"places"` (default), `"dates"`, or `"cells"` (see below) |
| `lc` | label column index (default 0) |
| `cols` | list of value columns: `{"c": col, "m": metric, "g": group, "d": date, "p": place, "b": basis, "n": note}` — only `c` is required |
| `m` | default metric: `"total"` (default), `"male"`, `"female"`, `"households"` |
| `g` | default group (default `"all"`; see below) |
| `d` | default date of the figures (for `rows: places`): `"1930"`, `"1930-10-01"`, `"1935-12-31"`. Take it from title, caption, column head, footnote or the book (an edition year book of 1935 usually gives end-1933 or 1934 figures: say what the table says; if the table gives no date at all, use `"~<edition year>"`, e.g. `"~1935"`) |
| `p` | the place (for `rows: dates` when the whole table is one place, e.g. `"Korea"`) |
| `pt` | kind of place in the label column: `prefecture`, `province`, `city`, `district`, `ward`, `town`, `country`, `colony`, `island`, `region`, `other` |
| `in` | where those places are: `Japan`, `Korea`, `Taiwan`, `Karafuto`, `Kwantung`, `South Seas`, `Manchuria`, `China`, `World`, or a city/province name (for wards, districts, towns) |
| `b` | basis: `census`, `registered` (本籍), `resident` (現住 / present), `estimate`, `survey`, `police` (police counts), `other` |
| `mult` | 1000 when figures are printed in thousands (千人), 10000 for 萬, etc. |
| `rp` | `{"row": "place"}`: name a row's place yourself (English), **especially total rows** (`{"0": "Japan proper"}`), or `"-"` to drop a row (sub-totals of mixed groups, headers, notes, rows that are not places) |
| `rd` | `{"row": "date"}` for `rows: dates` when a label is not a plain year (see below) |
| `only` | list of row indices to read (default: all) |
| `n` | short English note shown with every figure from this extractor (e.g. `"civilians only"`, `"Customs estimate"`) |

**Columns.** In `rows: places` tables list every column that holds a wanted count: e.g. a prefecture table with
`[1]男 [2]女 [3]計 [4]戶數` → `"cols":[{"c":3},{"c":1,"m":"male"},{"c":2,"m":"female"},{"c":4,"m":"households"}]`.
If columns are different years, give each its `d`. If columns are different groups (内地人 / 朝鮮人 / 外國人 / 計) give
each its `g`. If columns are different sources (census vs estimate), give each its `b` and/or `n`.

**rows: dates.** Row labels are years/dates. Plain years and era years are read automatically: `1930`, `1930年`,
`1930 (Oct. 1)`, `昭和5年`, `昭和五年末`, `大正九年`, `明治四十年`, `民國十年`, `M.40`, `T.9`, `S.5`, and ditto marks
(`,,` `〃` `同`) repeating the row above. Otherwise give `rd`. Put the place in `p` (or per column `p` when each column
is a different place, e.g. `[1]東京 [2]大阪`).

**rows: cells** for anything irregular: `{"rows":"cells","cells":[{"r":row,"c":col,"p":"place","d":"date","m":…,"g":…}]}`.

**Places.** Use the label as printed (the script matches 京畿道, Keiki-dō, Kyŏnggi, 東京府, Tokyo-fu, Shengking, 奉天,
Saipan … against a gazetteer). Only use `rp` for totals, for rows whose label is not the place's name, or for
labels that would be ambiguous. Standard names for whole units (use these in `p`/`rp`): `Japanese Empire`,
`Japan proper` (内地), `Korea`, `Taiwan`, `Karafuto`, `Kwantung Leased Territory`, `South Manchuria Railway Zone`,
`South Seas Mandate`, `Manchuria` (or `Manchukuo` from 1932), `China`, `China proper`, `Mongolia`, `Tibet`,
`Hong Kong`, `Macao`; countries by English name (`United States`, `British India` …); cities by English name.

**Kwantung and the Railway Zone.** Up to 1936 most empire-wide tables (censuses, 帝國統計年鑑, 都市年鑑, Japan Year
Book "Population of the Empire") print the leased territory and the S.M.R. zone as one unit — 關東州及滿鐵附屬地, but
often headed just 關東州 or "Kwantung". Name such a row or column `Kwantung Leased Territory and South Manchuria
Railway Zone`, also when it is printed as plain Kwantung but a heading, footnote or the figure itself shows the zone is
in (the combined census figures: 919,568 or 939,952 in 1920, 1,054,074 in 1925, 1,328,011 in 1930, 1,656,726 in
1935). `Kwantung Leased Territory` is the territory alone. From 1937 the zone belonged to Manchukuo, so a 1937 or
later row under 關東州 is the territory alone.

**Groups** (`g`): `all`, `japanese` (内地人), `korean` (朝鮮人), `chinese` (支那人/中華民國人/華僑), `taiwanese`
(本島人, Han Taiwanese), `aborigine` (蕃人/高砂族/生蕃), `islander` (South Seas 島民), `ainu`, `manchu`, `mongol`,
`foreign` (外國人, all foreigners together), or one nationality in lower-case English (`british`, `american`,
`russian`, `german`, `french`, `filipino` …). "Japanese subjects" incl. Koreans and Taiwanese → `all` with a note.

## Examples (the last two ids are illustrative)

```json
[
 {"t":"china-1913:p0020_1","x":[{"m":"households","pt":"region","in":"China","d":"1910","rp":{"4":"-"},"b":"other","n":"families returned (Minchengpu)"}]},
 {"t":"china-1913:p0020_3","x":[{"rows":"dates","p":"China","b":"estimate","cols":[{"c":1}]},{"rows":"dates","lc":2,"p":"China","b":"estimate","cols":[{"c":3}],"rd":{"2":"1710"}}]},
 {"t":"china-1913:p0021_1","x":[{"pt":"province","in":"China","rp":{"21":"-","23":"-","26":"China"},"cols":[{"c":2,"d":"1910","b":"census","n":"Minchengpu census"},{"c":5,"d":"1885","b":"census"},{"c":6,"d":"1910","b":"estimate","n":"Customs estimate"}]}]},
 {"t":"japan-1935:p0075_1","skip":"rates only"},
 {"t":"korea-tokanfu-1939:p0031_1","x":[{"pt":"province","in":"Korea","d":"1938-12-31","b":"resident","rp":{"0":"Korea"},"cols":[{"c":1,"m":"households"},{"c":4},{"c":2,"m":"male"},{"c":3,"m":"female"}]}]},
 {"t":"korea-1938:p0020_1","x":[{"rows":"dates","p":"Korea","cols":[{"c":1,"g":"japanese"},{"c":2,"g":"korean"},{"c":3,"g":"foreign"},{"c":4}]}]}
]
```

When done, reply with only: batches written, tables used, tables skipped, and anything you could not decide.
