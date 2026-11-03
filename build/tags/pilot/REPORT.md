# Classification rules and calibration pilot

Completed 26 October 2026. The pilot assigns 200 complete table records from all
102 volumes, covering every one of the 32 high-level topics. The current pilot
vocabulary contains 327 detailed tags and the independent `text-tables` flag.
Published table data, existing Topics assignments, generated pages and search
indexes were not changed. Full-corpus tagging has not begun.

Open [all 200 assignments](REVIEW.md), the [classification rules](../README.md),
or the [readable vocabulary](../VOCABULARY.md). A [CSV copy](review.csv) includes
every identity, book, title, assignment and rationale. The canonical assignments
are in [assignments.json](assignments.json); their provenance and review history
are in [review.json](review.json).

## Rules now in place

- One or two high-level topics and one to three detailed tags per table. No cap
  on vocabulary size. Detailed tags are shared globally across topics.
- Read the complete existing transcription: all parts, rows, headings, context
  and notes. No classification from contents headings alone; no OCR.
- Classify the substantive subject. A general budget remains finance; a school
  budget can be education plus finance. Currency values alone do not establish
  finance, and a demographic breakdown alone does not establish population.
- Use aggregate tags for genuine broad summaries rather than choosing a few
  incidental components. Economic barometers and general welfare inventories
  now have explicit aggregate tags.
- Keep sport separate from culture and trams separate from railways. Electric
  traction or the word 軌道 alone does not establish a tramway; hand-pushed light
  tracks remain railways.
- Require evidence for informal imperialism, colonial rule, Indigenous subjects
  and settler migration. A book's collection or an incidental territory row
  does not justify these labels.
- `text-tables` depends on substantive content. Office dates, era years, serials
  and accession dates remain textual. Quantities, measured areas, heights,
  course lengths and actual service durations make mixed records statistical.
- Record unknowns and use the supported broader label. Do not invent a term,
  silently repair a transcription or infer an undocumented historical identity.

Every vocabulary entry now has a definition, inclusion/exclusion guidance and
aliases; detailed tags also have browsing associations. The complete fields are
in [vocabulary.json](../vocabulary.json).

## Vocabulary additions

The contents-review proposal had 31 high-level topics and 312 detailed tags.
Completion research and calibration add one high-level topic, `history`, for
general historical chronologies. It is not a default for every historical table.

| New detailed tag | Pilot tables using it |
|---|---:|
| `historical-chronologies` | 2 |
| `banditry` | 2 |
| `addiction-treatment` | 1 |
| `balance-of-payments` | 0 |
| `services-and-invisible-trade` | 1 |
| `migrant-remittances` | 0 |
| `labour-productivity` | 0 |
| `cost-of-living` | 1 |
| `sports-organisations-and-facilities` | 1 |
| `calendars-and-time` | 2 |
| `religious-affiliation` | 3 |
| `sports-participation` | 1 |
| `hunting` | 1 |
| `economic-indicators` | 4 |
| `welfare-institutions` | 1 |

The first eleven terms arose while completing the definitions and remaining
Manchuria/Far East contents surveys. The last four arose from actual pilot
records. Three additions have contents evidence and definitions but no assignment
in this pilot; they still need calibration on full table bodies in the future.
These remain a pilot vocabulary for the user's evaluation. Earlier contents-review
visualizations preserve the earlier proposal; the files linked here are current.

## Sample and review method

The published corpus has 45,563 table records. An initial seeded sample of 180
used collection quotas, at least one table from every volume, thematic selection
hints and difficult formats. A targeted 20-record supplement tested the gaps and
boundaries exposed by the first batches. The exact keys, selection reasons,
source-file hashes and input fingerprints are preserved in the
[manifest](manifest.json). Selection hints were not assignment answers.

| Collection | Pilot tables |
|---|---:|
| Japan | 48 |
| China | 38 |
| Korea | 37 |
| Taiwan | 25 |
| Manchuria | 28 |
| South Seas Mandate | 14 |
| Far East / other | 10 |
| **Total** | **200** |

The sample includes 57 multipart records, 52 containing `[?]`, and 68 detected by
a CJK-title heuristic. A 17-image industrial-products record was read completely.
Roster heuristics helped selection but did not determine the text flag.

Four disjoint agent batches classified 60, 60, 60 and 20 complete existing records.
The final worker also reread six boundary cases. A separate consistency review
reread nine records in repeated school-finance and opium-licensing families.
Central reconciliation covered these 15 records and three related economic
summaries, for 18 targeted decisions. Raw results remain intact.

This is a purposeful calibration sample, not a representative prevalence sample
or a blinded accuracy study. The targeted second reviews cannot provide an
agreement rate for the corpus.

## Results

- 200 assignments: 184 statistical/mixed records and 16 `text-tables`.
- 138 tables have one high-level topic; 62 have two.
- 87 have one detailed tag, 55 have two and 58 have three.
- All 32 high-level topics and 136 of the 327 detailed tags appear.
- 11 assignments changed after vocabulary calibration and consistency review.
  That count includes new vocabulary and harmonised conventions; it is not an
  error-rate estimate.
- No classification question remains open in the reconciled assignments.
  Source-context limitations remain documented below.

### Important decisions

| Case | Final decision |
|---|---|
| Athletic-meet entrants | `sport` / `sports-participation`; entrant counts are distinct from results or venues. |
| Hunting licences | `government` / `hunting`; recreational, commercial and research licences are all present. |
| Multi-domain economic indices | Use `economic-indicators`; do not select three incidental components of an eight-series summary. |
| General social-work facilities | `welfare` / `welfare-institutions`; not every establishment is demonstrably charitable. |
| Railway self-protective villages | `population`, `agriculture` / `migration`, `households`, `arable-land`; nationality and foreign sponsorship are not established. |
| Major Chosen tramways | `transportation` / `trams`; substantial confirmed urban systems support the table-level tag despite one ambiguous minor line. |
| Taiwan hand-pushed track inventory | `transportation` / `railways`; its light push-car systems do not meet the tram definition. |
| Repeated school-association accounts | `education`, `finance` / `education-finance` consistently; household funding burden does not require a separate broader tax label. |
| Repeated opium-business inventories | `narcotics`, `trade` / `opium-licensing`; their commercial categories organise the whole body. |
| General colonial-territory budgets | `finance` / `public-budgets`; no imperial topic inferred from account ownership. |
| Meteorological observatory inventory | `science-and-technology` / `scientific-research`; coordinates and heights make it statistical, while weather readings are absent. |
| Emperor/era roster | `text-tables`; the column headed duration contains calendar ranges, not measured reign lengths. |

Exact reasons, before/after assignments and source limitations are preserved in
[resolutions.json](resolutions.json). One school table's supplied title identifies
Korean schools while its context describes Japanese financing; the pilot preserves
that conflict and assigns only the subjects supported under either reading.
The ambiguous village sponsorship and individual tram line likewise do not block
the conservative table-level classifications.

## Verification and limits

`python3 -B build/tags/validate_pilot.py --results` passes. The saved
[validation result](validation.json) checks:

- exact 200-key coverage and disjoint batches;
- approved IDs, uniqueness and assignment cardinalities;
- definitions, aliases, browsing associations and retained proposal IDs;
- frozen complete-record fingerprints and all 102 published table-data file hashes;
- archived vocabularies, final rules and zero open assignment questions.

Batch results also validate against the vocabulary version each worker used.
`1.0.0-pilot` is archived before the four calibration tags; `1.0.1-pilot` is
archived after those additions. Final `1.0.2-pilot` clarifies the migration boundary
to match the narrower settler-migration definition. The final rules are hashed.

These checks establish structural completeness and source integrity, not semantic
accuracy. The 191 unused detailed tags have definitions but no pilot assignments,
and several high-level topics have only one example. Transcription uncertainty,
incorrect contents attachments and historical category ambiguity will continue
to require targeted review during a full run.

The rules, controlled vocabulary, versioned batches and review workflow are ready
for evaluation. The pilot does not establish that the remaining 45,363 tables can
be tagged without further exceptions or vocabulary refinement. No full-corpus
assignment or Topics interface implementation was undertaken.
