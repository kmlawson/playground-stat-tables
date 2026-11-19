# Korea and Taiwan table classifications

Saved classifications for **6,594 tables in 39 volumes**.

| Collection | Volumes | Tables | Without detailed tags | Text tables |
|---|---:|---:|---:|---:|
| Korea | 33 | 4,286 | 36 | 339 |
| Taiwan | 6 | 2,308 | 9 | 13 |

## Files

- [Combined Korea and Taiwan assignments](assignments.korea-taiwan.json)
- [Korea assignments](assignments.korea.json) and [Taiwan assignments](assignments.taiwan.json)
- [Tables without detailed tags](no-detailed-tags.json)
- [Review questions](review-queue.json)
- [Per-table provenance](provenance.json) and [validation](validation.json)
- [Applied subject rules](rules.applied.tsv), [explicit decisions](decisions.tsv),
  [body-review overrides](reviewed-overrides.json) and [body flag review](body-flag-review.json)

## Method

The assistant performed a local, rule-assisted classification pass with **no LLM CLI
calls** and no external classification service. Explicitly authored subject rules
handle repeated table families; bilingual titles and English descriptions are used
with original columns, part labels and body profiles. Every complete JSON record was
parsed, and all body fields were inspected programmatically for quantities and identifiers.
Ambiguous headings, orphaned continuations, special accounts, directories and boundary
cases were reviewed in full as needed. This is a scalable subject-rule pass, not a
claim that every numerical cell was individually reread by the assistant.

The **62 existing calibration assignments** whose complete input fingerprints exactly
match these records are preserved verbatim. All remaining assignments retain the
applied rule or explicit record decision in provenance. These are draft classifications
for user evaluation. Structural validation does not establish perfect semantic accuracy.

The vocabulary is unchanged: **32 high-level topics and 327 detailed tags**, version
`1.1.0-optional-details`. Each record has 1–2 topics, 0–3 detailed tags and an independent
`text-tables` flag. **45 records** have no fitting or
sufficiently supported detail and are left for later review. Missing numerical bodies
remain statistical when their headings and context establish the intended quantities.

Topics describe the table subject; ordinary colonial-era demographic and productive
statistics do not automatically receive a colonial-rule tag. Indigenous-specific
statistics, formal colonial institutions and guard-line policing are treated separately.
Street trams remain distinct from conventional and light railways. Dedicated school
finance and licensed opium commerce follow the agreed classification boundaries.

## Validation and scope

Passed exact coverage and uniqueness for all **6,594 keys**, approved vocabulary IDs,
cardinality limits, all 39 original file hashes, all record fingerprints, frozen
vocabulary checks, and preservation of the 62 calibration assignments. No OCR or Git
operations were used. Original source data, existing China classifications, website
pages and Topics navigation were not changed.

The separate four-agent review of the 380 China tables without details is advisory;
its proposed vocabulary additions have not been incorporated into this run.

## Volumes

| Volume | Tables |
|---|---:|
| Annual Report on Reforms and Progress in Chosen 1911-12 | 143 |
| Annual Report on Reforms and Progress in Chosen 1912-13 | 173 |
| Annual Report on Reforms and Progress in Chosen 1913-14 | 104 |
| Annual Report on Reforms and Progress in Chosen 1914-15 | 101 |
| Annual Report on Reforms and Progress in Chosen 1915-16 | 80 |
| Annual Report on Reforms and Progress in Chosen 1916-17 | 98 |
| Annual Report on Reforms and Progress in Chosen 1917-18 | 93 |
| Annual Report on Administration of Chosen 1930-32 | 46 |
| Annual Report on Administration of Chosen 1932-33 | 47 |
| Annual Report on Administration of Chosen 1933-34 | 57 |
| Annual Report on Administration of Chosen 1934-35 | 50 |
| Annual Report on Administration of Chosen 1935-36 | 50 |
| Annual Report on Administration of Tyosen 1936-37 | 61 |
| Annual Report on Administration of Tyosen 1937-38 | 57 |
| Annual Report on Administration of Tyosen 1938-39 | 56 |
| Annual Report on Reforms and Progress in Chosen 1918-21 | 102 |
| Annual Report on Reforms and Progress in Chosen 1921-22 | 116 |
| Annual Report on Reforms and Progress in Chosen 1922-23 | 53 |
| Annual Report on Reforms and Progress in Chosen 1923-24 | 35 |
| Annual Report on Administration of Chosen 1924-26 | 32 |
| Annual Report on Administration of Chosen 1926-27 | 33 |
| Annual Report on Administration of Chosen 1927-28 | 36 |
| Annual Report on Administration of Chosen 1928-29 | 40 |
| Annual Report on Administration of Chosen 1929-30 | 48 |
| 朝鮮年鑑 1926 | 601 |
| 第一次統監府統計年報 1908 | 228 |
| 朝鮮總督府統計年報 1939 | 470 |
| 朝鮮年鑑 1940 | 533 |
| 朝鮮事情 1935 | 103 |
| 朝鮮事情 1940 | 213 |
| 朝鮮事情 1942 | 147 |
| 朝鮮事情 1943 | 141 |
| 朝鮮事情 1944 | 139 |
| 臺灣總督府統計書 1933 | 542 |
| 臺灣總督府統計書 1942 | 373 |
| 臺灣總督府統計書 1938 | 503 |
| 臺灣總督府統計書 1925 | 513 |
| The Progress of Taiwan 1905 | 97 |
| The Statistical Summary of Taiwan 1912 | 280 |
| **Total** | **6,594** |
