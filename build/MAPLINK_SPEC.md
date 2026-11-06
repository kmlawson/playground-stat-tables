# Map links from *Old Year Book Tables of East Asia* — payload spec, version 1

Some tables on the statistics site "Old Tables" (https://froginawell.net/reference/old-tables/, draft copy at https://kmlawson.github.io/playground-stat-tables/) have a **"Show on map"**
link. It opens the Japanese Empire map (https://froginawell.net/reference/japanese-empire/). The address carries one
table's figures by prefecture, so that the map can colour the prefectures.

This file tells the map application how to read that address. Version 1 covers **prefecture-level data for Japan
proper, plus a few colonial units**. Later versions may add cities, Korean provinces and so on. Their payloads will
carry a higher `v` and a different `units` value.

## 1. The URL

```
https://froginawell.net/reference/japanese-empire/?where=125.41,21.53,147.92,48.77&layers=2w#t=<payload>
```

- **`where` and `layers`** are the map's own query parameters, used exactly as the map already uses them. They
  give the bounding box (west, south, east, north in degrees) and the layer string. The site sends the standard
  Japan view.
- **`#t=<payload>`** is the table data in the URL fragment. The fragment is never sent to a server, so length
  limits on servers and CDNs don't apply. Payloads are typically 1–3 KB.
- **Encoding:** `payload` = base64url( raw-DEFLATE( UTF-8 JSON ) ).
  - base64url uses the `-` and `_` alphabet, with the trailing `=` padding removed.
  - raw DEFLATE has no zlib or gzip header, which is the `"deflate-raw"` format of the browser's
    `DecompressionStream`.
- **If there is no `#t=`**, the map behaves exactly as it does today.

### Two hosts: live (Frog in a Well) and draft (GitHub Pages)

Both sites exist twice:

| | live (froginawell.net) | draft (GitHub Pages) |
|---|---|---|
| tables site ("Old Tables") | https://froginawell.net/reference/old-tables/ | https://kmlawson.github.io/playground-stat-tables/ |
| map | https://froginawell.net/reference/japanese-empire/ | https://kmlawson.github.io/japanese-empire-student-map/ |

- **Tables site → map.** The *View as Map* button links to the map on the same host as the page it is on.
  - On `*.github.io` it opens the GitHub Pages map; everywhere else it opens the live froginawell map.
  - For testing, the tables page accepts `?map=gh` or `?map=live` in its address to force either one.
  - Only the base address changes. `where`, `layers` and `#t=` are identical.
- **Map → tables site.** The payload carries the table location both ways:
  - `src.path` is a relative path, e.g. `book/japan-keishicho-1935/#p0110_1`;
  - `src.url` is the full live URL.
- **What the map should do.** Build its "source table" link by joining `src.path` to the tables site **on its own
  host**:
  - the map on froginawell.net links to `https://froginawell.net/reference/old-tables/` + `src.path`;
  - the map on `kmlawson.github.io` links to `https://kmlawson.github.io/playground-stat-tables/` + `src.path`;
  - on any other host (e.g. a local preview), use `src.url`.

```js
function sourceTableUrl(p) {
  const base = /github\.io$/.test(location.hostname)
    ? "https://kmlawson.github.io/playground-stat-tables/"
    : /froginawell\.net$/.test(location.hostname)
      ? "https://froginawell.net/reference/old-tables/"
      : null;
  return base && p.src.path ? base + p.src.path : p.src.url;
}
```

### Decoding in the browser (no library needed)

```js
async function readTablePayload() {
  const m = location.hash.match(/(?:^#|&)t=([A-Za-z0-9_-]+)/);
  if (!m) return null;
  let b64 = m[1].replace(/-/g, "+").replace(/_/g, "/");
  b64 += "=".repeat((4 - b64.length % 4) % 4);
  const bytes = Uint8Array.from(atob(b64), c => c.charCodeAt(0));
  const stream = new Blob([bytes]).stream().pipeThrough(new DecompressionStream("deflate-raw"));
  const json = await new Response(stream).text();
  const p = JSON.parse(json);
  if (p.v !== 1) console.warn("Table payload version", p.v, "— reading as v1");
  return p;
}
```

`DecompressionStream("deflate-raw")` is available in current Chrome, Edge, Firefox (113+) and Safari (16.4+).

## 2. The payload (JSON)

```jsonc
{
  "v": 1,                                   // payload version; always check it
  "src": {                                  // where the data came from: link back to it
    "url": "https://froginawell.net/reference/old-tables/book/japan-keishicho-1935/#p0110_1",  // full live URL
    "path": "book/japan-keishicho-1935/#p0110_1",  // relative: join to the tables site on the map's own host (section 1)
    "book": "japan-keishicho-1935",         // site's id for the volume
    "table": "p0110_1"                      // site's id for the table within the volume
  },
  "title": { "ja": "藝妓本籍道府縣別",          // table title as printed (old character forms kept)
             "en": "Geisha by Prefecture of Registered Domicile, End of December 1935" },  // optional, LLM translation
  "volume": { "title": "警視廳統計書 1935",    // volume (book) title as listed on the site
              "year": "1935",                // the volume's edition year, as a string (can be a range: "1924–5")
              "en": "Keishichō tōkeisho (…)" },  // optional subtitle / romanisation
  "date": "1935-12-31",                     // date the figures refer to, if known: "1935", "1935-12" or "1935-12-31"; null if unknown
  "period": "1930",                         // suggested map period: "1930" or "1942" (nearest to the figures' date); may be null
  "part": null,                             // label of the table part the columns come from, if the table has several parts
  "units": "prefecture",                    // geography of the rows; v1 always "prefecture"
  "cols": [                                 // every data column sent, in order
    { "name": "人員",                        // column heading as printed; " — " separates levels of a multi-level heading
      "en": "Geisha (persons)",             // optional English heading
      "unit": "人",                          // optional unit as printed or explained
      "kind": "count",                      // optional: count | amount | rate | index | other  (see 3)
      "pc": true,                           // optional: per-capita view is meaningful for this column
      "color": "seq" }                      // optional hint: seq (sequential) | div (diverging)
  ],
  "def": 0,                                 // index into cols of the column to show first
  "rows": [                                 // one entry per row matched to a place
    { "id": "01", "label": "北海道", "row": 1, "v": [443] },
    { "id": "13", "label": "東京",   "row": 2, "v": [6349] }
    // …
  ],
  "total": {                                // the printed total row, if the table has one, else null
    "label": "總計", "row": 0, "v": [10661],
    "mismatch": { "0": 10659 }              // optional: for column 0 the mapped rows add up to 10659, not the printed 10661
  },
  "notes": [ "Geisha licensed in the Tokyo Metropolitan Police district, by prefecture of registered domicile …" ]
}
```

### Field rules

- **`rows[].id`** is a place id from section 4. Each `id` appears at most once.
  - A table may cover only some prefectures. Prefectures with no row have no data, which is different from zero.
- **`rows[].label`** is the row label exactly as printed, e.g. 東京, 東京府, 廣島縣, 樺太. Show it in tooltips if you
  want the historical form. It also lets a reader check the match.
- **`rows[].row`** is the row's position in the original table: 0-based, counting all rows of that part.
  Informational only.
- **`rows[].v`** has one value per entry of `cols`, in the same order. Each value is either:
  - a **number**, the printed figure with thousands separators removed. Decimals stay decimals, and percentages
    stay as printed (e.g. 12.5 means 12.5 %);
  - **`"?"`**: printed but unreadable in the scan. Show as "no data (unreadable)", never as 0;
  - **`""`**: blank in the original. Show as "no data";
  - **`"-"`**: a printed dash or "…". In these tables a dash usually means zero or nil, but not always. Show it as
    "— (nil)", distinct from both 0 and no data;
  - **any other string**: printed text that is not a clean figure, such as a misprint like `"17 03"` or a note
    like `"1)"`. Show the text, and treat the value as no data for colouring.
- **`total`** is null when the table prints no total. When `mismatch` is present, the mapped prefectures don't add
  up to the printed total for that column, usually because a row such as 外國 or 不詳 is not a place. Treat the
  printed total as authoritative for the legend or for shares.
- **Rates** (`kind: "rate"`): the total row is a national rate, not a sum. The site does not compute `mismatch`
  for them.
- **Missing optional fields** (`en`, `unit`, `kind`, `pc`, `color`) mean unknown. A missing `pc` means do not offer
  per capita.
- **`notes`** are short English notes worth showing with the legend, such as coverage or exclusions. There are
  usually 0–2.
- **Unknown fields** must be ignored, so that later additions don't break older map code.

## 3. Column kinds and the per-capita option

| kind | meaning | per capita? |
|---|---|---|
| `count` | persons, households, cases, items | yes, if `pc` is true |
| `amount` | money, quantities (yen, koku, tons) | yes, if `pc` is true |
| `rate` | already a ratio: per 1,000, per cent, average | **never**, whatever `pc` says |
| `index` | index numbers, rankings | never |
| `other` | anything else | never |

When `pc` is true, the map may offer an optional per-capita view, e.g. per 1,000 or per 10,000 inhabitants. It
should:

- divide by the population of the same place from the map's nearest census to `date` (1930 or 1940 for Japan
  proper);
- **say which census year it used** in the legend;
- leave out places for which it has no population figure, such as colonies without a matching dataset.

## 4. Place ids (stable across all tables)

The ids are the **JIS X 0401 prefecture codes as two-digit strings**. They fit the pre-1945 prefectures one to one:
東京府 (to 1943) and 東京都 (from 1943) are both `"13"`, and 北海道廳 is `"01"`.

| id | prefecture | id | prefecture | id | prefecture | id | prefecture |
|---|---|---|---|---|---|---|---|
| 01 | 北海道 Hokkaidō | 13 | 東京 Tōkyō | 25 | 滋賀 Shiga | 37 | 香川 Kagawa |
| 02 | 青森 Aomori | 14 | 神奈川 Kanagawa | 26 | 京都 Kyōto | 38 | 愛媛 Ehime |
| 03 | 岩手 Iwate | 15 | 新潟 Niigata | 27 | 大阪 Ōsaka | 39 | 高知 Kōchi |
| 04 | 宮城 Miyagi | 16 | 富山 Toyama | 28 | 兵庫 Hyōgo | 40 | 福岡 Fukuoka |
| 05 | 秋田 Akita | 17 | 石川 Ishikawa | 29 | 奈良 Nara | 41 | 佐賀 Saga |
| 06 | 山形 Yamagata | 18 | 福井 Fukui | 30 | 和歌山 Wakayama | 42 | 長崎 Nagasaki |
| 07 | 福島 Fukushima | 19 | 山梨 Yamanashi | 31 | 鳥取 Tottori | 43 | 熊本 Kumamoto |
| 08 | 茨城 Ibaraki | 20 | 長野 Nagano | 32 | 島根 Shimane | 44 | 大分 Ōita |
| 09 | 栃木 Tochigi | 21 | 岐阜 Gifu | 33 | 岡山 Okayama | 45 | 宮崎 Miyazaki |
| 10 | 群馬 Gunma | 22 | 静岡 Shizuoka | 34 | 広島 Hiroshima | 46 | 鹿児島 Kagoshima |
| 11 | 埼玉 Saitama | 23 | 愛知 Aichi | 35 | 山口 Yamaguchi | 47 | 沖縄 Okinawa |
| 12 | 千葉 Chiba | 24 | 三重 Mie | 36 | 徳島 Tokushima | | |

**Colonies and other units.** These appear in some Japanese tables as single rows:

| id | unit |
|---|---|
| `karafuto` | 樺太 Karafuto (whole territory) |
| `taiwan` | 臺灣 Taiwan (whole colony) |
| `chosen` | 朝鮮 Korea (whole colony) |
| `kwantung` | 關東州 Kwantung Leased Territory |
| `nanyo` | 南洋群島 South Seas Islands (Nan'yō) |

- **Whole territories:** colour the whole territory if the map has a matching outline, or show the value in a side
  list otherwise.
- **Future sub-units:** finer units such as Korean provinces or Taiwanese prefectures will get ids of the form
  `chosen-NN` and `taiwan-NN` in a later version. The `units` field will tell you which kind of row a payload
  holds.

The site matches printed row labels to these ids in Japanese and English, including old character forms (廣島, 靜岡, 鹿兒島, 沖繩), office names (北海道廳, 樺太廳), pre-war romanisations (Tokio, Kioto, Hiogo, Miye, Gumma, Shidzuoka, Yehime …), separate suffixes (Tōkyō Fu, Kanagawa Ken, Hokkaidō Chō) and footnote marks; city rows and sub-units (兵庫縣／神戸市, 郡部) are never matched to a prefecture. The site keeps the master list in `build/places/japan_prefectures.json`: each id with its modern form, English
name and old printed variants. The map does not need it; the ids above are the contract.

## 4a. Tables of the empire's parts (additions, still `v: 1`)

Agreed with the map (its `docs/table-links.md`, 2026-11-06); all fields optional and ignored by older code.

- **`units: "territory"`**: the rows are parts of the empire, ids `naichi` (内地), `chosen`, `taiwan`, `karafuto`,
  `kwantung` (關東州, also 關東州及鐵道附屬地 with the printed label kept), `nanyo`. Never mixed with prefecture ids.
- **Rows are always places.** A table printed with the places across the top is turned; columns that are neither
  place nor measure (期間, 年數, 區分) are not sent, and what they say goes into the heading ("(5 years)").
- **The whole is `total`**, never a row (帝國, 總數, 合計), with **`total.en`** ("Empire", "Total") and `mismatch`
  against the places sent. A printed 總數 that is a measure (all vehicles) is an ordinary column.
- **Every part in one payload**: `name` "part — column", `en` with the same levels; short labels written out.
- **`cols[].series`**: the same string on columns that are one measure at several dates (one scale);
  **`cols[].date`** orders them. 5- and 10-year rates are separate series.
- Footnote marks are taken off figures (`* 163.1` → 163.1) and explained in `notes`; `def` opens on a rate where
  the places differ a hundredfold in size.
- Site side: entries in `maplinks.json` with `"units": "territory"` list each column by hand (`part`, `line` = the
  printed row when `"across": true`, else the printed column); `build_territory` in `maplinks.py` builds them.

## 4b. Tables of cities (addition, still `v: 1`)

- **`units: "city"`**: each row is a city, and `rows[].id` is the map's own city id (`data/cities-1930.csv`,
  `data/cities-1942.csv`, named in `texts/city-names.csv` and `texts/sites/sites.csv`). The site matches printed
  labels against that gazetteer when the entry is written and stores the ids in `maplinks.json`.
- **`unplaced`** (new, optional): the printed labels of rows with figures that match no city on the map (呉市,
  堺市 …), so the map can say how much of the table it is not showing. Totals are in `total`, not here.
- A table printed with the cities across the top is turned as for territories: each printed row is a column.
- `kind`/`pc` as before: `pc: true` means a per-head view makes sense (the map has `pop_c1920/1930/1940` for its
  cities). Weather tables are `kind: "other"`.
- Site side: `city_entry` in `maplinks_add.py`, `build_city` in `maplinks.py`.

## 4c. Provinces, prefectures and groups outside Japan proper (addition, still `v: 1`)

The same shape as cities (4b), with `units` naming the set and `rows[].id` the `key` column of the map's
`texts/territories/sub-units/<file>.csv`:

| `units` | file | e.g. |
|---|---|---|
| `china-province` | `china.csv` | `Hebei` (printed Chihli or Hopei), `Liaoning` (Fengtien) |
| `korea-province` | `korea.csv` | 京畿道 |
| `manchukuo-province` | `manchukuo.csv` | |
| `taiwan-prefecture` | `taiwan.csv` (州・廳) | |
| `taiwan-district` | `taiwan.csv` (市・郡) | |
| `nanyo-group` | `mandate-groups.csv` | |

Older names are matched to the province the map draws (Chihli → Hebei, Fengtien → Liaoning); `label` keeps the
printed name. Rows the set does not cover (Shanghai, Peiping and other municipalities, "Manchuria", "Ki-Hei")
are in `unplaced`.

## 5. Examples

Two tables carry links at first:

1. **警視廳統計書 1935, table 藝妓本籍道府縣別** (geisha by prefecture of registered domicile, 31 Dec 1935).
   - One `count` column with `pc: true`, and a printed total.
   - Rows for `chosen` and `karafuto` are included; one row for Russia is not mapped, hence `total.mismatch`.
2. **家事年鑑 1939, table 出生、死産、死亡及自然増加** (births, stillbirths, deaths and natural increase per 1,000
   population, 1937).
   - Four `rate` columns with `pc: false`.
   - The total row is the national rate.
   - A few cells are `"?"` or misprints such as `"17 03"`.

Their current URLs are printed by `python3 build/maplinks.py --list` on the site side.

## 6. What the map should show (suggestions, not requirements)

- A panel with:
  - the title (Japanese and English);
  - the volume title and year;
  - the figures' date;
  - the column picker (all `cols`, starting at `def`), with each column's unit;
  - the notes;
  - a link back to `src.url` ("source table").
- A legend with the colour scale.
  - If the per-capita view is on, also show the census year used.
  - Separate swatches for no data, unreadable (`"?"`) and nil (`"-"`).
- Tooltips with the printed `label` and the value as printed.
- Optionally, the printed `total`, and each prefecture's share of it.
