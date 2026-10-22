# Topic tagging — Korea tables

You get a listing file: one table per line, tab-separated:
`<slug>:<id>  <chapter>  <title>  [en] <English title, if any>  [cols] <first column headers>`.
Books: English *Annual Report on Reforms and Progress in Chosen* (korea-19xx-yy), Japanese 朝鮮事情 (korea-19xx),
朝鮮年鑑 (korea-nenkan-*), 統監府/總督府統計年報 (korea-tokanfu-*).

Tag every table that belongs to one or more of these four topics. Use ONLY these subtopic labels:

- **population**: `totals and density` · `by nationality` (内地人/朝鮮人/外國人, Japanese/Koreans/foreigners) ·
  `by province or district` · `households` · `births, deaths and marriages` · `migration and foreign residents` ·
  `occupations` · `age and sex`
- **education**: `schools and pupils, overview` · `elementary and common schools` · `secondary and higher schools` ·
  `vocational and normal schools` · `private schools and sŏdang` · `teachers` · `finance` · `libraries, students abroad and other`
- **religion**: `overview` · `Shinto and shrines` · `Buddhism` · `Christianity and missions` · `other religions and religious bodies`
- **crime**: `offences and arrests` · `prosecutions and courts` · `sentences and convictions` · `prisons and prisoners` ·
  `police` · `summary punishments` · `thought and public-order offences` · `juvenile`

Rules:
- Judge from chapter, title and column headers. A table belongs to a topic when its figures are about that topic
  (a table of school buildings' costs is education/finance; a general budget table listing an education line is NOT).
- A table may get several tags (e.g. pupils by nationality → education/`elementary and common schools` only, unless it is
  really a population count; a prison table with nationality columns → crime/`prisons and prisoners`). Usually one or two.
- A table with a population column used only as a denominator (e.g. "per 1,000 inhabitants" in a health table) is not population.
- Health, hygiene, public welfare, finance, trade, agriculture, communications etc. are out of scope — leave untagged.
- Untagged tables are simply omitted.

Output: write `/Users/kml/shell/projects/yearbooks/japanyearbooks/stat-tables-site/build/topics/tags_<N>.json` where N is your
listing number:
`{"<slug>:<id>": [["population","by nationality"], ["education","teachers"]], ...}`
It must parse (check with `python3 -m json.tool`). Use only the labels above, spelled exactly.
Work from the listing only; do not open images or other files. No sub-agents. Never write in /tmp.
Reply in ≤3 lines: number of tables tagged per topic, and anything ambiguous you decided.
