# Ten-table CLI comparison: Haiku 5.5 and Sonnet 5.5

Both models returned valid structured data for all ten tables in one batched
response. Sonnet followed the supplied classification rules much more closely:
eight assignments exactly match the reviewed pilot, compared with two for Haiku.
The original pilot assignments and all published data remain unchanged.

## Identical experiment

- Models: `anthropic/claude-haiku-5-5` and `anthropic/claude-sonnet-5-5` through
  the installed LLM CLI, version 0.36.
- Ten complete existing records, drawn from all seven book collections; five
  have CJK original titles. Original and English layers, all parts, rows, notes
  and context were included. No OCR or new transcription was used.
- Rules and all 32 high-level / 327 detailed tag definitions, including their
  inclusion/exclusion guidance, were supplied once per ten-table batch.
- System prompt, user prompt, JSON schema, records, vocabulary and rules were
  byte-identical across the two runs. Hashes are in
  [model-comparison.json](model-comparison.json).
- Both used `thinking_effort=low`, `max_tokens=10000`, no streaming and no global
  CLI conversation logging. Provider metadata reports zero thinking tokens.
- Previous per-table assignments and review decisions were withheld. The
  reference was used only after the response for comparison.

The selected records are purposeful calibration cases, some of which informed
the supplied rules. This is a test of batching, structured output and rule
following, not an independent estimate of performance on unseen corpus tables.

## Results

| Check | Haiku 5.5 | Sonnet 5.5 |
|---|---:|---:|
| Complete assignments returned | 10/10 | 10/10 |
| Structural / permitted-ID checks | Pass | Pass |
| Exact match of topic, detail and flag sets | 2/10 | 8/10 |
| High-level topic sets match | 3/10 | 9/10 |
| Detailed tag sets match | 5/10 | 8/10 |
| Text/statistical flags match | 9/10 | 10/10 |
| Records raising review questions | 3 | 2 |
| Successful CLI request elapsed time | 17.24 s | 12.53 s |
| Input tokens reported | 71,944 | 71,944 |
| Output tokens reported | 1,357 | 1,112 |

Exact agreement is not itself an accuracy score. For example, Haiku's
education-only topic with `education-finance` is a defensible difference from
the two-topic reference. Other differences clearly conflict with the definitions.
There is only one qualifying text-only table in this ten-record selection.
Timing is one observation per model, not a latency benchmark.

## Table-by-table review

| Table | Haiku assessment | Sonnet assessment |
|---|---|---|
| `china-1916:p0125_6` — Electric Tramways | Correct `trams`, but incorrect utilities topic and missing text flag for a city-name list. | Exact match: transportation / trams / text-tables. |
| `korea-1942:p0131_1` — Athletic-meet participants | Culture contradicts the sport/culture split, despite correct sports-participation. | Exact match: sport / sports-participation. |
| `taiwan-tokei-1925:p0263_2` — Light railway lines and handcars | Adds trams despite the explicit hand-pushed/light-rail evidence and rule. | Exact railways match; also raises a review question. |
| `japan-1937:p0409_1` — Economic Index | Exact match. | Exact match. |
| `japan-1939-40:p0696_1` — Governmental Educational Expenditure | Education / education-finance is a defensible narrower choice; omits optional finance topic. | Exact education + finance / education-finance match. |
| `korea-tokanfu-1939:p0246_1` — General special account | Exact public-budget match. | Exact public-budget match. |
| `manchuria-1939:p0091_1` — Railway self-protective villages | Adds colonial-rule and settler-migration without the required evidence; omits cultivation. | Avoids colonial-rule but still chooses settler-migration without evidence and omits households/arable-land. Raises a review question. |
| `far-east-1941:IMG_5400_1` — Rubber, tin ore and rice | Omits rubber and substitutes broad representative tags, although all three commodities fit. | Exact agriculture + mining / rubber, tin, rice match. |
| `nanyo-tokei-1937:p0041_3` — Hunting licences | Adds culture and police from incidental purpose / chapter context. | Exact government / hunting match. |
| `taiwan-tokei-1933:p0353_2` — Licensed opium traders | Chooses health from the chapter instead of the substantive narcotics/trade subjects. | Correct topics and specific licensing tag; adds redundant broader opium tag. |

The two Sonnet differences have different significance. The settlement label
needs substantive review: organised cohorts alone do not establish colonial
expansion or foreign state sponsorship. The extra opium tag is a minor redundancy
under the specificity rule. Neither difference changes the original pilot labels.

## What this establishes

Ten tables in one call works. The schema and local validation produced an exact
identity map with valid vocabulary IDs and assignment limits. Sonnet is the
stronger candidate in this comparison, but the settlement case shows that valid
JSON and permitted labels do not establish correct classification. Its own review
question would route that case for inspection.

The current fully defined vocabulary makes the request long: 194,626 user-prompt
characters, including 19,317 characters of table records. A compact prompt or
caching strategy would need separate testing before a large run. Production
batches should account for record size as well as a ten-table target; this trial
does not test the largest multipart records. No full-corpus run was started.

## Setup and reproducibility

The initial Haiku attempt could not connect from the sandbox. A subsequent
network-enabled request was rejected because the schema repeated large tag-ID
enums. Removing those enums fixed compilation; the full vocabulary remained in
the prompt, and permitted IDs were enforced locally. The unsuccessful attempts
and original rejected schema are preserved in the Haiku directory. The successful
Sonnet run used the same simplified schema without that setup failure.

Raw results and comparisons:

- Haiku: [response](haiku-10-2026-10-26/response.json),
  [comparison](haiku-10-2026-10-26/comparison.json),
  [content assessment](haiku-10-2026-10-26/assessment.json).
- Sonnet: [response](sonnet-10-2026-10-26/response.json),
  [comparison](sonnet-10-2026-10-26/comparison.json),
  [content assessment](sonnet-10-2026-10-26/assessment.json).
- [Combined results and input hashes](model-comparison.json).

The harness is [test_llm_batch.py](../test_llm_batch.py). `evaluate` performs only
local comparison and can be rerun safely. `run` makes a paid model request and
refuses to overwrite an existing response. `prepare` refuses to overwrite an
existing frozen trial. No model response is automatically promoted to pilot or
published assignments.
