# Population page — place aliases (agent brief)

The Population page matches the place names printed in the tables (row labels) against a gazetteer. Names it cannot
match become places of their own, "as printed". Your job: for the unmatched names, say which gazetteer place each one
is, which ones are spellings of the same unknown place, and which are not places at all.

## Files

- `build/population/work/unplaced.txt` — tab-separated: `count  region  label  kind  in`. `region` is the region the
  table is about (`japan`, `korea`, `taiwan`, `china`, `manchuria`, `nanyo`, `kwantung`, `karafuto`, `world`, or `*`
  when the table did not say); `kind` and `in` are what the table spec said (may be empty). Sorted by count.
- `build/population/work/gazetteer.tsv` — every known place: `id  en  ja  kind  parent`.
- If you need to see a name in its table, search the specs (`build/population/work/specs/*/b*.json`) and the table
  in `data/<slug>.json`. Never open scans or images; never use OCR.

## Output: `build/population/aliases.json`

```json
{"map": {"korea|Taiku": "c-taegu", "*|Suiyo-shima (Truk)": "n-truk-tol", "taiwan|蕃地": "-"},
 "new": {"n-truk-tol": {"en": "Tol (Suiyō-tō), Truk", "ja": "水曜島", "k": "island", "up": "ss-Chuuk"}}}
```

- Key: `<region>|<label exactly as in unplaced.txt>` (use the region column as given, including `*`).
- Value: a gazetteer id; or the id of a place you define under `new`; or `"-"` for a label that is not a place.
- `new` places: id `n-<short-ascii-slug>`, `en` (English/romanised name, period form, e.g. "Taikyū (Taegu)"), `ja` (CJK
  form if known), `k` (kind: `city`, `town`, `district`, `ward`, `island`, `county`, `settlement`, `country`, `region`,
  `other`), `up` (parent id from the gazetteer or another new place). Use `new` to gather spellings of one place the
  gazetteer lacks (Suiyo-shima / Suiyojima / 水曜島 → one id), and to put a place under the right parent (a Truk
  island under `ss-Chuuk`, a Tokyo ward under `c-tokyo`).

## Rules

- **Only when sure.** Map a label only when it is certainly that place: a romanisation (Japanese reading of a Korean
  or Chinese name: Taikyū = 大邱 = Taegu; Wade-Giles/postal ↔ pinyin), old/new characters, a misprint-level spelling
  difference, a suffix (-fu, -shi, 市, 府, 郡, 廳). When unsure, leave it out (it stays as printed — that is fine).
- **Same level only.** A town is not the county or province of the same name (Yenki county ≠ Yanji city; 新竹郡 ≠
  新竹州 ≠ 新竹市). A ward is not its city. An island is not its island group, nor a branch office its island
  (the Saipan branch office ≠ Saipan Island): such rows get a `new` place of the right kind under the right parent.
- **Not places → `"-"`**: sub-totals and category rows that slipped through (市部, 郡部, urban/rural totals, "Other
  islands", "Others", "Unknown", "At sea", 蕃地 when it is "aboriginal territory" repeated under every prefecture in a
  list, headers, notes). Only when clearly not a single place.
- Work down `unplaced.txt` from the top; cover at least every label with count ≥ 3 (about 4,600). Many lines will
  need nothing: that is fine — skip them. Write the file as you go (every few hundred lines) so nothing is lost, and
  check it parses: `python3 -c "import json;json.load(open('build/population/aliases.json'))"`.
- Do not edit any other file. Scratch files only in `build/population/work/alias_scratch/`.

When done, reply with only: how many labels mapped to the gazetteer, how many new places (and how many labels they
gather), how many dropped, and anything you could not decide.
