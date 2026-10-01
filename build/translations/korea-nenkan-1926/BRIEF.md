# English titles and one-line descriptions: 朝鮮年鑑 1925 (Chōsen nenkan, Kyŏngsŏng 1925)

A Japanese-language yearbook of colonial Korea. Each input line (in/<batch>.txt) is one table:
`id | chapter | printed pages | TITLE | CAPTION | PARTS | COLUMNS | ROWS (first row labels) | NROWS`
Titles use the old character forms as printed (國, 數, 經濟, 敎育…) and 1920s katakana style (…ニ對スル…).
If a line is not enough, look the table up by "id" in
`/Volumes/Oma/Yale Backup/To Process/The Manchoukuo Year Book 1942/stat-tables-site/data/korea-1925.json`
with a short python3 script. Work only from this text/JSON; there are no scans to read and no OCR is involved.

For EVERY table in your batch write:
- "t": the table title in English: a faithful, natural translation of TITLE (title case, no final period). When the
  title is only a continuation or a place name (e.g. "— 釜山府"), keep that in the English (e.g. "Members of Municipal
  Councils — Pusan").
- "d": ONE concise English phrase or sentence (aim for ≤ 15 words; must fit on one line) saying what the table
  contains: the unit of observation and breakdown, main measures, and the year(s) if clear from the title, caption,
  columns or rows. Describe; do not quote figures, do not interpret or evaluate, do not add facts not in the table.

Conventions:
- Korean place names (in "t" and "d"): the Korean reading in McCune–Reischauer romanization ONLY, with its
  diacritics (ŏ, ŭ) and apostrophes for aspirates; no Japanese readings, no modern-spelling glosses. E.g. 京城
  Kyŏngsŏng, 釜山 Pusan, 仁川 Inch'ŏn, 平壤 P'yŏngyang, 大邱 Taegu, 元山 Wŏnsan, 開城 Kaesŏng, 木浦 Mokp'o,
  群山 Kunsan, 鎭南浦 Chinnamp'o, 新義州 Sinŭiju, 淸津 Ch'ŏngjin, 濟州島 Cheju Island, 鴨綠江 Amnok River,
  豆滿江 Tuman River, 間島 Kando. Provinces: 京畿道 Kyŏnggi Province, 慶尙南道 South Kyŏngsang Province,
  全羅北道 North Chŏlla Province, 咸鏡北道 North Hamgyŏng Province, 平安南道 South P'yŏngan Province,
  黃海道 Hwanghae Province, 江原道 Kangwŏn Province, 忠淸北道 North Ch'ungch'ŏng Province.
  Places outside Korea keep their usual English names (Tokyo, Osaka, Manchuria, Vladivostok).
  Japanese words that are not Korean place names (eras, units, institutions) use Hepburn (Taishō, koku, Chōsen).
- Administrative units: 道 province; 府 municipality (fu); 郡 county; 面 township (myŏn); 島 island.
- Eras: 大正 Taishō, 明治 Meiji; convert to Western years where obvious (大正十三年 = 1924), e.g. "1924 (Taishō 13)"
  only when the era year is the point; otherwise just "1924".
- Currency 圓 = yen; 里 ri; 町 chō; 石 koku; 貫 kan; 坪 tsubo; 反/段 tan; 町步 chōbu.
- 內地人 = Japanese (from Japan proper); 鮮人/朝鮮人 = Koreans; 外國人 = foreigners.
- 總督府 = Government-General; 同上 / 同 in a title means "ditto" — expand it from the previous table's title.
- Keep it neutral and period-appropriate; don't modernise the categories the table uses.

Output: write out/<batch>.json as a JSON object keyed by table id:
{"p0008_1": {"t": "Abridged Calendar for 1926 (Taishō 15)", "d": "Months of the solar and lunar calendars with their long/short months, holidays and Sundays."}, ...}
Every id in your input file must appear exactly once. Validate with
python3 -c "import json;d=json.load(open('out/<batch>.json'));print(len(d))" and check the count equals the number of
input lines. Reply with one line: batch, number written. Nothing else.
