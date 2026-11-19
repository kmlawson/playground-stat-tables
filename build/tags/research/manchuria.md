# Manchuria saved-contents vocabulary review

This review covers **9 of 9 books** whose filenames in `stat-tables-site/data` begin with `manchuria`, `manchoukuo` or `manchukuo`. It uses saved transcriptions and existing table records only. No OCR, image transcription, table assignments or published-data changes were performed. The `japan-manchoukuo-*` books are outside this nine-book filename scope.

## Exact files and coverage

All paths below are relative to the repository root. Both the data TOC and its saved source counterpart were read. For every pair, the multisets of `(title, printed page)` agree exactly; the source files add transcription notes and contents-scan identifiers rather than extra headings.

| Data TOC | Saved source TOC | Entries | Nonempty printed pages | Linked table IDs |
|---|---|---:|---:|---:|
| `stat-tables-site/data/manchoukuo-1934-toc.json` | `_toc/manchoukuo-1934/toc.json` | 809 | 762 | 371 |
| `stat-tables-site/data/manchoukuo-1942-toc.json` | `_toc/manchoukuo-1942/toc.json` | 562 | 36 | 274 |
| `stat-tables-site/data/manchukuo-directory-1938-toc.json` | `_toc/manchukuo-directory-1938/toc.json` | 245 | 223 | 38 |
| `stat-tables-site/data/manchuria-1929-toc.json` | `_toc/manchuria-1929/toc.json` | 220 | 201 | 75 |
| `stat-tables-site/data/manchuria-1931-toc.json` | `_toc/manchuria-1931/toc.json` | 250 | 222 | 104 |
| `stat-tables-site/data/manchuria-1936-toc.json` | `_toc/manchuria-1936/toc.json` | 230 | 212 | 102 |
| `stat-tables-site/data/manchuria-1939-toc.json` | `_toc/manchuria-1939/toc.json` | 250 | 230 | 76 |
| `stat-tables-site/data/manchuria-year-book-1931-toc.json` | `_toc/manchuria-year-book-1931/toc.json` | 299 | 274 | 223 |
| `stat-tables-site/data/manchuria-year-book-1932-33-toc.json` | `_toc/manchuria-year-book-1932-33/toc.json` | 608 | 566 | 281 |
| **Total** | **18 saved TOC files, 9 books** | **3,473** | **2,726** | **1,544** |

The 3,473 data entries contain **3,022 exact heading strings**. Case folding, whitespace and terminal-period normalisation, and removal of leading chapter/section numbering reduce these to **2,618 distinct review headings**. Repeated headings and closely equivalent subjects reused one vocabulary decision, while book and chapter context remained available. English/Japanese directory headings were reviewed in their context; the distinct-string counts do not pretend to be a semantic bilingual deduplication. Linked table IDs are unique within each book; they are supplementary evidence, not a count of every table in the books.

The review includes substantive chapters, subheadings, statutory/documentary appendices, statistical-table lists, illustration/map lists and front matter. Map captions, portraits, advertisements, generic headings such as “General Outline”, and place-only directory headings do not independently justify vocabulary additions.

## Coverage and existing vocabulary decisions

| Recurring subject and saved evidence | Existing vocabulary that describes it |
|---|---|
| Geography, geology, climate and rivers throughout the yearbooks; natural agricultural conditions in 1934 | `physical-geography`, `land-area`, `weather`, `rivers-and-waterways`; add an agricultural topic only when the table's substance warrants it |
| Kaoliang, millet and maize in `manchuria-1929`, `manchuria-1931`, and the 1932–33, 1934 and 1942 yearbooks | `cereals`; no new tag for each cereal heading |
| Soybeans, bean cake and bean oil throughout the progress reports and yearbooks | `soybeans`, `vegetable-oils`, and transaction/activity tags such as `exports`, `warehousing` or `prices` as the table's actual subject warrants |
| Model farms and agricultural institutions in the 1929/1931 reports and yearbooks | `agricultural-extension`; `scientific-research` when research itself is substantive |
| Cotton, tobacco, tussah silk, flax/hemp/jute and wool | Reusable `cotton`, `tobacco`, `silk`, `sericulture`, `plant-fibres`, `wool` across production, processing and trade; topic choice follows the actual activity |
| Forest zones, standing timber, forest control and lumber enterprises | `forest-area`, `forest-management`, `timber`, `afforestation` |
| Marine and freshwater fisheries, fishing households and prepared aquatic products | `fishing`, `aquaculture` where cultivation is established, and `food-processing` for processing |
| Salt manufacture, salt fields, monopoly and gabelle | `salt`, `state-monopolies`, `salt-tax`; the historical placement under aquatic products does not force the fisheries topic |
| Fushun shale oil and oil plants in the 1929/1931 reports; oil shale in the 1932–33/1934 yearbooks; shale oil and coal liquefaction in 1942 | `petroleum`, `coal` as substantive, `industrial-output`, `state-monopolies`; no separate oil-shale tag needed |
| Magnesite, steatite, dolomite, limestone, quartzite and building stones in the 1931/1932–33/1934 yearbooks, with a magnesite-region table in 1942 | `mineral-production`, `mineral-reserves`, `physical-geography` and specific processing tags as applicable; existing groups describe the activity/resource without a tag for every mineral heading |
| Matches, soap, dyes, paints, soda and chemical industries | `chemicals`; dedicated existing tags such as `fertilisers` or `pharmaceuticals` where sufficient |
| Flour milling and condiments in multiple yearbooks | `food-processing`; `wheat` or `soybeans` only when that commodity is substantive |
| Machinery, vehicles, railway workshops and arms manufacture | `machinery`, `railways`, `arms-and-arsenals`, `shipbuilding` as content warrants |
| Printing industry in 1934, and publications/cinema in 1942 | `industrial-output` for printing production; `newspapers`, `periodicals`, `books`, `theatre-and-cinema` for substantive publication/media subjects |
| Electricity, gas, waterworks, town construction and city development | `electricity`, `hydroelectricity`, `gas`, `water-and-sewerage`, `construction`, `urban-planning` |
| Railways, ports, bus lines, waterways, through traffic and freight rates | `railways`, `ports`, `road-transport`, `inland-navigation`, `freight-and-transport-costs`; retain distinct `trams` whenever a table concerns tramways |
| Leased territory, railway-zone jurisdiction and abolition of extraterritoriality in the reports and yearbooks | `foreign-concessions`, `extraterritoriality`, `colonial-administration`, `treaties`, `local-government`, according to substantive content |
| Immigration, Japanese/Chinese/Korean settlement and agricultural colonisation | `migration`, `settler-migration`, `nationality-and-ethnicity`, `rural-development`; origin or book location alone does not determine a topic |
| Bandit suppression and “peace preservation” in the 1931/1934/1936/1939 reports and 1942 yearbook | `police`, `political-policing`, `army`, `war-and-mobilisation` as supported by the actual record; retain source terminology as evidence without accepting its political characterisation automatically |
| Fiscal rehabilitation, industrial plans, financial controls, currency unification and trade | Existing `public-budgets`, `economic-planning`, `economic-controls`, `currency`, `foreign-exchange`, `banking`, `foreign-investment`, `imports`, `exports`, `tariffs` |
| Schools, religion, medicine, plague prevention, welfare, narcotics and labour | Existing sector topics and detailed tags; `buddhism` covers Lamaism, `islam` covers Mohammedanism, and `epidemics`/`diseases` cover plague |

Commodity values alone do not add the finance topic. A general budget with a school line remains a finance table; a table devoted to education budgets can warrant education plus finance. The related-topic lists are discovery guidance, not a binding hierarchy. The pilot still uses 1–2 substantive high-level topics, 1–3 detailed tags and an independent `text-tables` flag.

## Proposed additions: one substantive gap

Full definitions are in `stat-tables-site/build/tags/definitions/resources.json`, under `proposed_additions`: topic `history` and detailed tag `historical-chronologies`.

General multi-subject historical chronologies recur across the yearbooks. A table spanning dynastic changes, diplomacy, war and other historical events is not adequately described by any one existing sector tag, and selecting several incidental sectors would not describe its overall subject within the tagging limits. The new entries cover this general historical substance. Single-sector chronologies continue to use the relevant subject's tags. The independent `text-tables` flag describes their textual content and is not replaced by a history tag.

Evidence in the main saved table datasets:

- `stat-tables-site/data/manchuria-year-book-1931.json`, table **`p0041_1`**, **“Chronological Table”**. Its saved columns are `Year` and `Event`; the opening entries concern the naming of the Ching polity, Russian exploration and imperial succession. The table is linked by entry 19 of `manchuria-year-book-1931-toc.json`, printed p. 21, “3. Chronological Table”.
- `stat-tables-site/data/manchoukuo-1942.json`, table **`IMG_5508_1`**, **“Chronology of Important Events”**. Its saved columns are `Year` and `Event`; the opening entries concern the Ching dynasty, Russian exploration and imperial succession. It is linked from entry 33, “Chapter II. History”, of `manchoukuo-1942-toc.json`; entry 59 separately lists “Chronology”.

Additional recurrence in saved contents:

- `manchuria-year-book-1931-toc.json`, entry 244, printed p. 319, “Chronology of China with Special Reference to Manchuria”.
- `manchuria-year-book-1932-33-toc.json`, entries 352–353, printed pp. 495 and 504, “Table of Outstanding Events in or relating to Manchurian History” and “Chronology (January, 1931—October, 1932)”.
- `manchoukuo-1934-toc.json`, entries 456–457, printed pp. 806 and 815, “Table of Outstanding Events in or Relating to Manchurian History” and “Chronology”.

No other additions are proposed from this corpus review. Broad existing subject groups cover the remaining recurring contents; the pilot can provide stronger table-level evidence if a narrower distinction proves necessary. This is not a vocabulary count cap.

## Gaps and limits

- **Saved-TOC coverage is complete for these nine books; full-book extraction coverage was not audited here.** The source notes describe the ends of their contents lists. This review cannot establish that every substantive table in each book has a published record.
- **1942 contents are unusually coarse.** The source explains that chapter page ranges are followed by dash-separated topic summaries; these became 526 unpaginated level-2 entries with inherited chapter links (`c`). Only 36 of its 562 entries have printed-page values. Its 559 URLs must not be interpreted as 559 precisely located substantive sections.
- **Directory scope is limited.** The 1938–39 directory mixes English and Japanese TOCs and restarts pagination by city. Its source explicitly says the Index to Advertisers is listed but not transcribed. The Japanese first page for Kaiyuan is unreadable (`[?]`), while the English TOC says 133. No attempt was made to recover those absent details.
- **Hierarchy and ranges are simplified in the saved sources.** The 1934 and 1932–33 source notes say deeper indentation was flattened to levels 2/3, and printed page ranges retain their first page. The 1936/1939 appendix hierarchies are also flattened. Titles sharing a parent therefore cannot establish identical table subjects.
- **Front matter, plates, maps and documentary texts are represented.** A contents heading is evidence of a subject's presence, not proof that it is a statistical table. Documents, directories and historical-event lists may instead require the independent text-table flag if they are in the table corpus.
- **Printed errors are preserved.** The 1931 source notes the printed “November 26, 1806”; the 1932–33 source notes errors including “Mireral”, “Manchnria” and “Number” for lumber; the 1939 source preserves “Frade” and “Contruction”. These do not create distinct subjects or new vocabulary.
