# Table classification: China Sonnet run

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

Each assignment has:

1. One high-level `topics` ID, or two when two subjects substantially organise the
   table. The order records the principal subject first.
2. Zero to three distinct detailed `tags` IDs, ordered from the most useful subject
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


## User-authorised rule for this complete China run

If none of the existing detailed tags fits the substantive subject, assign no
detailed tag: return `tags: []`. Do not force an approximate, unrelated or overly
broad label simply to fill a slot. Explain the uncovered subject in the rationale
and review_questions. We will revisit records without detailed tags later.
High-level topics remain mandatory (one or two); text-tables remains independent.
Use only the supplied vocabulary. Propose missing terms in review_questions;
do not invent tag IDs or add vocabulary during this run.
Do not include a speculative tag merely because a review question is also raised.
Keep the supported broader migration label when colonial/foreign sponsorship is
not established. Prefer opium-licensing alone for a pure opium-licence inventory.
