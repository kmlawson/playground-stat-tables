# Romanisation conversions (English layer only)

**Scope:** only our own English in `build/translations/<slug>.json` — each table entry's `t` (title) and `d`
(description) and the `_chapters` values. **Never transcriptions** (`tables/`, `directory/`, `chronology/`,
`toc.json`): they keep the romanisation as printed (CLAUDE.md hard rule, user 2026-11-28). A converted display option
for transcriptions may come later; not yet.

The rule itself is in `docs/stages/translations.md`.

## Files

- `conversions.json`: the master list. Each `conversions` item has `from`, `to`, `chars` (a regex for the characters
  the source table must contain), `alt` (other readings to check for) and `note`. It also has `keep` (forms not
  converted), `terms` (common nouns such as 縣, handled phrase by phrase) and `false_hits` (matches that look like old
  romanisation but aren't). Add every new form you meet here.
- `survey.py [OUT_DIR]`: makes no edits. It finds every listed form in the English layer and looks up the source
  table's characters. Results are `OK`, `ALT`/`BOTH` (another reading's characters are present), `NOTFOUND`, or
  `NOSRC` (no table file found).
- `convert.py [--write] [--only slugs]`: run without `--write` first for a preview (`./changes.tsv`). Entry-specific
  rewrites go in `SPECIFIC` and 縣 phrases in `HSIEN`; the token map then comes from `conversions.json`. Run it from
  the scratchpad so `changes.tsv` doesn't land in the repo.

## Method (use it again for any mass conversion, e.g. the Taiwan Hepburn (pinyin) pass)

1. **Find candidates three ways.** A pure regex misses forms, and a dictionary filter drops names that are also English
   words (Shantung, Canton, Peking, Nanking):
   - capitalised non-dictionary words;
   - Wade-Giles shapes (Hs-, Ts-, Kw-, -kiang, -chow, apostrophes);
   - an explicit list of conventional and Japanese-reading names (Mukden, Port Arthur, Dairen, Hōten, Shinkyō…).

   Always match whole words.
2. **Check against the source characters** with `survey.py`. Read every row that isn't OK in the table itself.
3. **Ask the user** about anything that isn't a place or personal name: common nouns (縣), era names (康德),
   conventional English names (Manchukuo, Hong Kong, Harbin), and cases where the printed form and the meaning differ
   (京師, 廣東 used for the city).
4. **Preview, then review every word-level substitution with counts** (one line per `old → new` pair) before
   `--write`.
5. **Rescan with `survey.py`.** Only `keep` and `false_hits` forms should be left.

## Lessons from the first run (2026-11-28: 513 strings, 28 files)

- **關東 vs 廣東.** Kwantung = 關東; Kwangtung = 廣東 = Guangdong. Some tables print both. 關東州 is an exception
  to pinyin (user, 2026-11-28): it went to "Guandong" first, then was rewritten (158 strings) as "the Kwantung Leased
  Territory" wherever the territory is meant, and "Kwantung Bureau/Government/Army/…" for institutions. Bare uses in
  lists needed "the" added. Kwantung is therefore in `keep`, not `conversions`.
- **廣東 often means the city** (Canton) in Japanese texts, e.g. 福州及廣東 or 香港及廣東. The user wants the meaning:
  Guangzhou.
- **京師** was translated "Peking". The user wants the meaning: Beijing. 北平 is Beiping.
- **Translations can be wrong, not just old-fashioned.** 江海關 had been rendered "Kiangsu Customs"; it is the Jianghai
  Customs (Shanghai).
- **Descriptions can claim what the table lacks.** Ten Minsei 1940 descriptions said "including Xinjing special city"
  where the table has no 新京 row (two only mention it in a transcriber's note: "no 新京"). They were fixed on
  2026-11-28. Check claims against the rows, columns and title, not against the whole file.
- **Empire-wide volumes use other forms.** Japanese, Korean and Taiwan books have Manchurian names in Korean or
  Japanese readings (Kando 間島, Tomun 圖們) and in Wade-Giles that looks like McCune–Reischauer (Hunch'un 琿春). Find
  them from the characters: take entries whose source rows, columns or title print a Chinese or Manchurian place, and
  list the English words they use. A Wade-Giles regex alone misses them.
- **Same characters, different place.** Matching characters is not enough in Korean, Japanese and Taiwan books.
  Check that the place really lies in China or Manchuria (look at the rows and addresses):
  - The Tomun Railway 圖們鐵道 (Korea Nenkan 1926) ran inside Korea, so it stays McCune–Reischauer "Tomun". It was
    converted to "Tumen" by mistake and reverted.
  - 安東 (Andong), 大同 (Taedong) and 江西 (Kangsŏ) are also Korean places; 基隆 is Kīrun in Taiwan.
  - Within China a form can match two places (Lintung 林東 vs 臨潼; Mukden 奉天 vs 瀋陽): `survey.py` checks the
    characters for each entry.
- **False hits:**
  - *mien-hsien* (麵線, noodles);
  - Koh (Koh Kong; the Taiwan unit 甲);
  - Shina inside Shinagawa;
  - Korean McCune–Reischauer apostrophes (P'yŏng-, Ch'ung-, Mokp'o). Korean names are never converted.
- **Hand-formatted files.** `korea-1942.json` is formatted by hand, so `convert.py` patches its raw text instead of
  re-dumping it.
