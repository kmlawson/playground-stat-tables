# Japan, Manchuria and South Seas: metadata-only first pass

Completed the requested first pass across **28,734 tables in 42 books**: **28,644 new metadata-only assessments** and **90 preserved complete-record pilot assignments**.

All 23 proposed tags are now part of vocabulary **1.2.0**, giving **32 high-level topics and 350 detailed tags**. Existing definitions are unchanged. [Current vocabulary](../../VOCABULARY.md) · [Current rules](../../CLASSIFICATION.md).

| Collection | Books | Tables | New first-pass records | With high-level topics | With detailed tags |
| --- | ---: | ---: | ---: | ---: | ---: |
| japan | 26 | 20,972 | 20,924 | 18,725 | 15,383 |
| manchuria | 14 | 7,292 | 7,264 | 6,461 | 5,293 |
| south-seas | 2 | 470 | 456 | 434 | 396 |
| **Total** | **42** | **28,734** | **28,644** | **25,620** | **21,072** |

Coverage columns include the preserved pilot assignments; per-collection counts for new records alone are in validation.json.

**3,114 tables have blank high-level topics; 7,662 have blank detailed tags.** Both fields are blank for **2,668**. These are deliberately deferred, not failed calls, and the two blank-field counts overlap.

## Method and confidence

The assistant authored bilingual subject rules and checked metadata examples and boundary cases locally. Only titles, English titles/descriptions, chapter headings, captions and supplied descriptive context enter classification. Complete JSON files are parsed to extract those fields and compute integrity fingerprints; no rows, columns, part labels or footnotes are reviewed or used as classification evidence.

Explicit title subjects take precedence over a book's collection. Chapter-only inference is restricted to a clear subject heading, and detailed inference from descriptions is conservative. Cross-sector/ambiguous titles, insufficiently identified commodities and overfull detailed candidates are retained for the later full-content pass. No arbitrary three-commodity subset is selected from a broad product inventory.

This is a partial first pass, not a final complete-record classification. Each assigned field has rule/evidence provenance; empty topics and details are independent uncertainty states. Prior complete-record pilot assignments are preserved verbatim and separately marked.

The text/statistical flag remains **unknown for 12,571 records**. These are explicitly marked in provenance and queued. An empty flags list in such a record does not establish statistical content. The user-requested high-level/detailed first pass does not require guessing this flag.

## Saved files

- [Combined assignments](assignments.japan-manchuria-south-seas.json)
- [Japan assignments](assignments.japan.json)
- [Manchuria assignments](assignments.manchuria.json)
- [South Seas assignments](assignments.south-seas.json)
- [Tables without high-level topics](no-topics.json)
- [Tables without detailed tags](no-detailed-tags.json)
- [All remaining review questions](review-queue.json) and [unknown text flags](flag-review-queue.json)
- [Metadata evidence/provenance](provenance.json), [frozen allowed metadata](metadata.json), [manifest](manifest.json) and [validation](validation.json)

## Validation

Passed exact coverage and uniqueness, approved vocabulary/alias and cardinality checks, evidence-to-metadata checks, all source hashes, exact preservation of 90 pilot decisions, and prior China/Korea/Taiwan saved-output hashes. Boundary examples check trade versus extraction, family versus public budgets, trams versus electric railways, and publication-setting leakage. A body-field injection is rejected by the classifier. The historical pilot also passes validation against its restored exact frozen vocabulary.

No LLM CLI calls, full-content reviews, OCR, Git operations or site builds were performed. This run saves new draft classifications and queues for later review; it does not apply the earlier China-review suggestions to the 380 China records.

## Book coverage

| Collection | Book | Tables |
| --- | --- | ---: |
| japan | The Japan Year Book 1905 (`japan-1905`) | 403 |
| japan | The Japan Year Book 1906 (`japan-1906`) | 765 |
| japan | The Japan Year Book 1907 (`japan-1907`) | 762 |
| japan | The Japan Year Book 1908-09 (`japan-1908-09`) | 801 |
| japan | The Japan Year Book 1910 (`japan-1910`) | 752 |
| japan | The Japan Year Book 1911 (`japan-1911`) | 860 |
| japan | The Japan Year Book 1912 (`japan-1912`) | 836 |
| japan | The Japan Year Book 1913 (`japan-1913`) | 824 |
| japan | The Japan Year Book 1914 (`japan-1914`) | 860 |
| japan | The Japan Year Book 1915 (`japan-1915`) | 852 |
| japan | The Japan Year Book 1916 (`japan-1916`) | 810 |
| japan | The Japan Year Book 1917 (`japan-1917`) | 816 |
| japan | The Japan Year Book 1918 (`japan-1918`) | 808 |
| japan | The Japan Year Book 1919-20 (`japan-1919-20`) | 808 |
| japan | The Japan Year Book 1920-21 (`japan-1920-21`) | 697 |
| japan | The Japan Year Book 1923 (`japan-1923`) | 815 |
| japan | The Japan Year Book 1924-25 (`japan-1924-25`) | 966 |
| japan | The Japan Year Book 1930 (`japan-1930`) | 716 |
| japan | The Japan Year Book 1935 (`japan-1935`) | 1,207 |
| japan | The Japan Year Book 1937 (`japan-1937`) | 1,541 |
| japan | The Japan Year Book 1939-40 (`japan-1939-40`) | 1,268 |
| japan | The Japan Year Book 1942-43 (`japan-1942-43`) | 1,065 |
| japan | The Japan Year Book 1946-48 (`japan-1946-48`) | 574 |
| manchuria | Report on Progress in Manchuria 1929 (`manchuria-1929`) | 75 |
| manchuria | Second Report on Progress in Manchuria 1931 (`manchuria-1931`) | 106 |
| manchuria | Fifth Report on Progress in Manchuria 1936 (`manchuria-1936`) | 102 |
| manchuria | Sixth Report on Progress in Manchuria 1939 (`manchuria-1939`) | 76 |
| manchuria | The Manchuria Year Book 1931 (`manchuria-year-book-1931`) | 226 |
| manchuria | The Manchuria Year Book 1932-33 (`manchuria-year-book-1932-33`) | 283 |
| manchuria | The Manchoukuo Year Book 1934 (`manchoukuo-1934`) | 373 |
| manchuria | Manchukuo Directory 1938-9 (`manchukuo-directory-1938`) | 66 |
| manchuria | Japan-Manchoukuo Year Book 1934 (`japan-manchoukuo-1934`) | 1,151 |
| manchuria | Japan-Manchoukuo Year Book 1936 (`japan-manchoukuo-1936`) | 1,347 |
| manchuria | Japan-Manchoukuo Year Book 1938 (`japan-manchoukuo-1938`) | 1,364 |
| manchuria | Japan-Manchoukuo Year Book 1939 (`japan-manchoukuo-1939`) | 1,386 |
| manchuria | Japan-Manchoukuo Year Book 1940 (`japan-manchoukuo-1940`) | 459 |
| south-seas | 南洋廳統計年鑑 1937 (`nanyo-tokei-1937`) | 211 |
| south-seas | 南洋廳統計年鑑 1932 (`nanyo-tokei-1932`) | 259 |
| japan | 大日本帝國統計年鑑 1935 (`japan-tokei-1935`) | 455 |
| japan | 大日本帝國統計年鑑 1938 (`japan-tokei-1938`) | 496 |
| japan | 大日本帝國統計年鑑 1940 (`japan-tokei-1940`) | 215 |
| manchuria | The Manchoukuo Year Book 1942 (`manchoukuo-1942`) | 278 |
