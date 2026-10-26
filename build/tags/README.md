# Table classification: pilot rules

This directory holds the vocabulary and a calibration pilot. The pilot does not
modify the published table data, book pages, existing topic files, or search index.
Full-corpus assignment and interface work follow the user's review of this pilot.

## Unit of classification

- Classify every selected record as one complete table, including all its parts,
  continuation pages, rows, captions, printed notes, and relevant context.
- Identify it by `book-slug:table-id`; a local table ID alone is not globally unique.
- Use the original title and English layer together. Read the complete supplied
  JSON. A title or contents heading alone is insufficient for final assignment.
- Treat the book's collection as bibliographic context. It is not the territory
  necessarily described by a particular table, and does not itself justify a tag.
- Keep all printed historical classifications intact. Tags aid discovery; they do
  not reconcile figures, standardise populations, or endorse an author's categories.
- No OCR, ever. This is classification of existing transcriptions, not a new
  transcription or numerical correction pass.

## Assignment limits

Each final pilot assignment has:

1. One high-level `topics` ID, or two when two subjects substantially organise the
   table. The order records the principal subject first.
2. One to three distinct detailed `tags` IDs, ordered from the most useful subject
   to secondary subjects or substantial analytical breakdowns.
3. An optional independent `text-tables` flag. This does not consume either limit.

There is no numerical cap on vocabulary size. New terms are proposed in the review
queue and incorporated centrally, with definitions, before they are used. Agents
must not invent IDs in assignments or bypass limits by joining arbitrary words.

## Subject, measure, and context

- Choose the principal subject shown by the actual rows and columns. A general
  budget with an education row is `finance`; a table devoted to school budgets can
  be `education` plus `finance`.
- A currency amount does not automatically make a table finance. Gold exports are
  `trade` with `exports` and `gold`; mined gold output is `mining`; gold reserves
  are `finance`.
- School pupils by nationality remain primarily `education`. A substantial
  nationality breakdown can receive `nationality-and-ethnicity`; this does not
  automatically add the high-level topic `population`. Apply the same principle
  to prisoners, soldiers, patients, and workers.
- Use an aggregate detailed tag such as `crop-production`, `mineral-production`,
  or `industrial-output` for genuine multi-product summaries. Do not select three
  incidental commodities to represent a table covering twenty equally.
- Use `economic-indicators` for general multi-domain economic barometers, and
  `welfare-institutions` for multi-function social-work facility inventories. Do
  not represent these summaries by choosing three incidental components.
- Detailed tags are shared across topics. `related_topics` in the vocabulary are
  browsing associations, not a whitelist restricting valid combinations.
- Prefer the most specific fitting detailed tag. Do not spend a slot redundantly
  on its broader equivalent unless the table independently covers the wider subject.
- Do not tag every incidental row, denominator, note, place, or date. A tag should
  help a reader find a table substantially concerned with that subject.

## Boundaries requiring care

- `trams` covers street and interurban tramways. Conventional and light railways
  remain `railways`. Electric traction alone does not establish a tramway; Japanese
  軌道 can include other track systems. Escalate unclear cases instead of inferring
  the category from that word alone.
  Confirmed tram content can justify a table-level `trams` tag in a mixed inventory;
  an ambiguous minor line does not require a speculative additional `railways` tag.
- `informal-imperialism` concerns explicit foreign privileges, extraterritorial
  jurisdiction, concession systems, or foreign control in a nominally sovereign
  setting. `colonial-rule` concerns formal colonial administration, annexation,
  protectorate institutions, settler policies, or explicit assimilation measures.
  Ordinary demographic or production data do not acquire either topic from their
  publication setting. Kwantung's formal leased-territory administration and
  Manchoukuo's nominal sovereignty need their particular table context examined.
- `indigenous-peoples` requires the table's main subject to be Indigenous peoples
  or institutions directed at them. It is not a default for all South Seas or
  Taiwan tables. Preserve the printed population labels and their limitations.
- `settler-migration` requires evidence of settlement associated with colonial
  expansion or foreign state sponsorship. Dated settlement groups alone can
  support `migration` without establishing that narrower association.
- `sericulture` covers silkworms, cocoons, and mulberry husbandry; `silk` identifies
  the material, manufacture, or trade. Assign both only when both are substantial.
- `suicide` identifies the reported cause or event. Do not infer a psychiatric
  diagnosis or automatically add `mental-health`.
- A table of hunting licences spanning recreational, commercial and scientific
  purposes is principally government administration with `hunting`; the presence
  of recreational licences alone does not make the whole table a sporting survey.
- `sports-participation` covers entrants and active participants. Competitive
  outcomes belong to `sports-records`; club/venue inventories belong to
  `sports-organisations-and-facilities`.
- Distinguish financial budgets, company operating accounts, trade values,
  economic policy, and production quantities from their numerical appearance.
- For dedicated school-funding tables, use `education-finance` for budgets and
  undifferentiated household funding burdens. Add `taxation` for a substantial
  separately identified tax measure, rather than inferring it from burden alone.
- Opium-licence inventories organised throughout by wholesalers, retailers and
  commercial suppliers can use `narcotics` plus `trade`. A combined sugar-output
  and opium-stock table retains the two substantial subjects of its actual body.

## Text tables

Use `text-tables` when the substantive content is textual: office-holder lists,
treaty lists, place-name indexes, organisational descriptions, or bibliographies.
Appointment dates, calendar/reign years, numbering, identifiers, ranks, or page
references alone do not make these statistical tables.
Numbers mentioned incidentally in narrative event descriptions do not themselves
form a statistical series; assess their substantive role in the complete record.

A table of substantive quantities, amounts, rates, measurements, durations, or
comparable quantitative observations is statistical. A mixed table is statistical.
An unreadable or blank numerical transcription can still be a statistical table
when its structure and notes establish the intended quantities. Never decide this
flag solely by a numeric-character count or the presence of `[?]`.

## Pilot workflow and audit

1. Freeze a manifest of selected published records and their input hashes. Sampling
   spans every book and collection, content themes, languages, text rosters, mixed
   tables, multipart tables, and unusually large or uncertain records.
2. Each worker receives a disjoint batch and the same versioned vocabulary/rules.
   Selection heuristics and old topic assignments are not shown as label answers.
3. A result records IDs, topics, detailed tags, flags, a short evidence-based
   rationale, and any review questions. Do not alter an input record.
4. Validate exact batch coverage, global identity, approved IDs, cardinalities,
   duplicate labels, and unchanged source inputs. Verify every vocabulary entry has
   a definition, inclusion/exclusion guidance, and valid browsing associations.
5. Review uncertain cases, proposed terms, text/statistical edge cases, context
   leakage, and significant disagreement. Record resolutions and rule changes.
6. Produce a pilot report, final pilot assignments, and a concise queue of any
   decisions still requiring the user. Stop before full-corpus assignment or UI work.

## Files

- `vocabulary.json`: versioned pilot vocabulary, definitions and aliases.
- `definitions/*.json`: separately authored definition contributions.
- `research/*.md`: remaining contents surveys and evidence for new terms.
- `pilot/manifest.json`: frozen selection, source hashes, and sampling reasons.
- `pilot/input/*.json`: complete original table records with book metadata.
- `pilot/batches/*.json`: disjoint lists of assigned keys.
- `pilot/results/*.json`: worker output before central review.
- `pilot/assignments.json`: reconciled pilot assignments.
- `pilot/review.json`: rationale, questions, decisions, and input fingerprints.
- `pilot/REVIEW.md` and `pilot/review.csv`: readable copies of all pilot assignments.
- `pilot/resolutions.json`: central decisions, preserving reasons for changes.
- `pilot/REPORT.md`: pilot findings and readiness for a full run.
- `VOCABULARY.md`: readable topic and detailed-tag definitions.

## Checking this pilot

Run `python3 -B build/tags/validate_pilot.py --results` from the site directory.
This checks definitions, permitted IDs, exact coverage, assignment limits, frozen
inputs and all 102 published table-data files. It does not establish semantic
accuracy. Raw worker results and targeted reviews remain available for inspection.

`finish_pilot.py` rebuilds review copies from the frozen batches, raw results and
explicit resolutions. `prepare_pilot.py` and `prepare_supplement.py` created the
sample; do not rerun them over an already reviewed pilot. A fresh pilot needs its
own preserved selection and review record.
