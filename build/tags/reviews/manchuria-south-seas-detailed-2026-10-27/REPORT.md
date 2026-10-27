# Manchuria and South Seas detailed-tag review

Reviewed the **1,999 Manchuria and 74 South Seas tables** from the fixed 7,662-table deferred cohort using their existing complete transcriptions. No external LLM calls, OCR, new vocabulary terms or transcription changes were made.

Saved **2,044 new detailed assignments**; **29** remain blank. Corrected **114** high-level mismatches explicitly established by the contents and added **131** explicit text-table flags. Other existing high-level topics and flag assessments are preserved.

## Method

Local, assistant-authored rules process all part labels, columns and every row/cell, with the supplied descriptions, context and notes available to the review. Repeated subject families use central rules. Ambiguous records, broad aggregate tables, apparent cross-subject matches and reference/list tables received explicit record decisions. This is a rule-assisted subject classification, not a rereading of every printed digit or a new transcription.

The decisions distinguish actual table functions from incidental entries: court deposits are not bank savings; service prices are not transport fares; plant capital is not a count of textile output; multiple religions are not labelled as Buddhism alone; street-tram evidence is kept distinct from railway traction. Numbers that are dates, office/unit identifiers or article numbers alone do not make a reference list statistical. Uncertain subjects and vocabulary gaps remain blank.

## Saved records

- [Decisions, previous labels and body evidence](reviewed-decisions.json)
- [Explicit record decisions](manual-groups.json)
- [Unresolved detailed subjects](unresolved.json)
- [Validation](validation.json)
- [Current remainder of the original cohort](remaining-deferred-details.json)
- [Unchanged original 7,662-table list](../deferred-detailed-tags-2026-10-26.json)

The original list is retained unchanged. Its current remainder is **5,618 tables**: 5,589 in Japan and 29 reviewed Manchuria records. All 74 South Seas records now have detailed tags.

## By volume

| Volume | Reviewed | Assigned | Still blank |
| --- | ---: | ---: | ---: |
| Report on Progress in Manchuria 1929 | 8 | 8 | 0 |
| Second Report on Progress in Manchuria 1931 | 11 | 11 | 0 |
| Fifth Report on Progress in Manchuria 1936 | 30 | 30 | 0 |
| Sixth Report on Progress in Manchuria 1939 | 22 | 22 | 0 |
| The Manchuria Year Book 1931 | 48 | 44 | 4 |
| The Manchuria Year Book 1932-33 | 58 | 54 | 4 |
| The Manchoukuo Year Book 1934 | 87 | 87 | 0 |
| Manchukuo Directory 1938-9 | 28 | 28 | 0 |
| Japan-Manchoukuo Year Book 1934 | 318 | 315 | 3 |
| Japan-Manchoukuo Year Book 1936 | 420 | 414 | 6 |
| Japan-Manchoukuo Year Book 1938 | 394 | 389 | 5 |
| Japan-Manchoukuo Year Book 1939 | 369 | 364 | 5 |
| Japan-Manchoukuo Year Book 1940 | 123 | 123 | 0 |
| 南洋廳統計年鑑 1937 | 35 | 35 | 0 |
| 南洋廳統計年鑑 1932 | 39 | 39 | 0 |
| The Manchoukuo Year Book 1942 | 83 | 81 | 2 |

## Remaining questions

| Key | Title | Reason |
| --- | --- | --- |
| `manchuria-year-book-1931:p0121_1` | [Annual Figures, 1925–1929 (Continued from Previous Page)] | Continuation fragments omit the subject or measurement headings; leave details blank rather than infer them from neighbouring numbers. |
| `manchuria-year-book-1931:p0123_1` | [Annual Figures, 1927-1929 (continued from previous page)] | Continuation fragments omit the subject or measurement headings; leave details blank rather than infer them from neighbouring numbers. |
| `manchuria-year-book-1931:p0153_1` | [Statistics Continued from Previous Page (Year, Count and Value)] | Continuation fragments omit the subject or measurement headings; leave details blank rather than infer them from neighbouring numbers. |
| `manchuria-year-book-1931:p0205_1` | [Year-End Figures, 1925–1928 (continued from previous page)] | Continuation fragments omit the subject or measurement headings; leave details blank rather than infer them from neighbouring numbers. |
| `manchuria-year-book-1932-33:p0152_1` | [Statistics of Three Eastern Provinces, Kwantung Leased Territory and S.M.R. Zone, 1927–1930] | Continuation fragments omit the subject or measurement headings; leave details blank rather than infer them from neighbouring numbers. |
| `manchuria-year-book-1932-33:p0338_1` | [Untitled Table Continued from Previous Page] | Continuation fragments omit the subject or measurement headings; leave details blank rather than infer them from neighbouring numbers. |
| `manchuria-year-book-1932-33:p0344_1` | [Continued Revenue Table, 1915–1930 (Heading Not Printed on This Page)] | Continuation fragments omit the subject or measurement headings; leave details blank rather than infer them from neighbouring numbers. |
| `manchuria-year-book-1932-33:p0345_1` | [Untitled Table Continued From Previous Page] | Continuation fragments omit the subject or measurement headings; leave details blank rather than infer them from neighbouring numbers. |
| `japan-manchoukuo-1934:p1-0423_3` | Principal By-Products in Recent Years | A heterogeneous return of minor forest by-products (seeds, fruits, bark, mushrooms, charcoal and others). No current aggregate tag fits, and no incidental product is selected to stand for the whole table. |
| `japan-manchoukuo-1934:p2-0061_2` | [Crop rotation on large farms] | A rotation-of-crops prescription: no yield/output measure and no supported shifting-cultivation practice. Crop rotation lacks a precise current tag. The substantive fields are names, descriptions, dates or identifiers; mark as a text table. |
| `japan-manchoukuo-1934:p2-0322_1` | List of Abbreviations | An editorial abbreviations/errata reference, with no suitable approved detailed subject. The substantive fields are names, descriptions, dates or identifiers; mark as a text table. |
| `japan-manchoukuo-1936:p1-0043_2` | Errata | An editorial abbreviations/errata reference, with no suitable approved detailed subject. The substantive fields are names, descriptions, dates or identifiers; mark as a text table. |
| `japan-manchoukuo-1936:p1-0437_3` | Principal By-Products in Recent Years | A heterogeneous return of minor forest by-products (seeds, fruits, bark, mushrooms, charcoal and others). No current aggregate tag fits, and no incidental product is selected to stand for the whole table. |
| `japan-manchoukuo-1936:p1-0487_4` | Increase in the Demand for Metres | Demand for Metres has no identified meter/product in its complete transcription; adjoining industry tables do not establish the subject. |
| `japan-manchoukuo-1936:p1-1053_1` | List of Abbreviations | An editorial abbreviations/errata reference, with no suitable approved detailed subject. The substantive fields are names, descriptions, dates or identifiers; mark as a text table. |
| `japan-manchoukuo-1936:p1-1298_1` | Map Index of Place Names | A map/place-name index, without land-survey activity or measured physical features. No precise approved detailed tag fits. The substantive fields are names, descriptions, dates or identifiers; mark as a text table. |
| `japan-manchoukuo-1936:p1-1298_4` | Meaning of Common Endings | Meanings of geographic place-name suffixes, rather than a language-use survey or pronunciation notation; no precise current detailed tag fits. The substantive fields are names, descriptions, dates or identifiers; mark as a text table. |
| `japan-manchoukuo-1938:p1-0101_1` | Expatriated Japanese | Expatriated Japanese has only Year and Number, without defining whether it counts departures, overseas residents or changes of citizenship. The complete supplied transcription does not resolve that distinction; leave details blank. |
| `japan-manchoukuo-1938:p1-0419_2` | Principal By-Products in Recent Years | A heterogeneous return of minor forest by-products (seeds, fruits, bark, mushrooms, charcoal and others). No current aggregate tag fits, and no incidental product is selected to stand for the whole table. |
| `japan-manchoukuo-1938:p1-0462_2` | Increase in Demand for Metres | Demand for Metres has no identified meter/product in its complete transcription; adjoining industry tables do not establish the subject. |
| `japan-manchoukuo-1938:p1-0964_1` | Number of Licensed Traders | Licensed traders occur in the sanitation chapter, but neither the body nor source notes specify what they sell. Do not infer opium or pharmaceuticals. |
| `japan-manchoukuo-1938:p1-1026_1` | Abbreviations | An editorial abbreviations/errata reference, with no suitable approved detailed subject. The substantive fields are names, descriptions, dates or identifiers; mark as a text table. |
| `japan-manchoukuo-1939:p1-0408_1` | Principal By-Products | A heterogeneous return of minor forest by-products (seeds, fruits, bark, mushrooms, charcoal and others). No current aggregate tag fits, and no incidental product is selected to stand for the whole table. |
| `japan-manchoukuo-1939:p1-0892_2` | References (sources of the tables in this chapter) | A source-key/reference crosswalk rather than a table about one cited industry. No current detailed tag adequately describes this editorial source apparatus. The substantive fields are names, descriptions, dates or identifiers; mark as a text table. |
| `japan-manchoukuo-1939:p1-0921_1` | Number of Licensed Traders (End of 1935) | Licensed traders occur in the sanitation chapter, but neither the body nor source notes specify what they sell. Do not infer opium or pharmaceuticals. |
| `japan-manchoukuo-1939:p1-0976_4` | Distribution by Purpose, 1931 | The purpose breakdown does not identify the underlying financial flow sufficiently in this transcription; no banking tag is inferred from an incidental row. |
| `japan-manchoukuo-1939:p1-1002_1` | Abbreviations | An editorial abbreviations/errata reference, with no suitable approved detailed subject. The substantive fields are names, descriptions, dates or identifiers; mark as a text table. |
| `manchoukuo-1942:IMG_5479_3` | Sunrise and Sunset | Sunrise/sunset observations lack a time-system comparison; the calendars-and-time definition explicitly excludes them. |
| `manchoukuo-1942:IMG_5641_1` | [Recognition of Manchoukuo by the Powers] | Dates of diplomatic recognition; the vocabulary has no precise recognition tag, and these are not treaties or a diplomatic-service roster. The substantive fields are names, descriptions, dates or identifiers; mark as a text table. |
