# Current table classification rules

The current vocabulary is version `1.2.0`: 32 high-level topics, 350 detailed tags
and the independent `text-tables` flag. The user approved all 23 consolidated
proposals from the four-agent China review, including the optional and conditional
proposals. Approval adds the terms; it does not resolve uncertain evidence in any
particular table or automatically change previous assignments.

The subject boundaries and guidance in [the original rules](README.md) continue to
apply, with the following later user instructions taking precedence:

- Detailed tags may be empty when no sufficiently supported term fits. Do not
  force a term or rerun untagged tables merely to fill the slot.
- The first pass for the remaining Japan, Manchuria and South Seas tables uses
  titles, descriptions/captions and chapter headings only. It must not inspect
  columns, rows, part labels, footnotes or neighbouring table bodies.
- Assign only high-confidence topics and details. Either field may independently
  remain empty for the later full-content pass. For example, a clear education
  chapter can support `education` while a generic table title leaves details empty.
- Partial first-pass records allow 0–2 topics and 0–3 details. Full-content
  classifications retain 1–2 topics and 0–3 details. A missing value is uncertainty,
  not a new subject or an assertion that the table has no subject.
- The text/statistical distinction normally requires contents review. First-pass
  records explicitly record an unknown flag assessment unless the metadata itself
  establishes a textual roster/reference list or quantitative observations.
  An empty flags list with unknown status does not establish that a table is statistical.
- Preserve prior reviewed assignments and their provenance. Do not replace a
  complete-record decision with a metadata inference.
- `related_topics` are browsing hints, not restrictions. Do not infer colonial,
  Indigenous or informal-imperialism subjects solely from a collection or book.
- Conventional/light railways remain distinct from street/interurban trams.
  Electric traction or the character 軌道 alone does not establish a tramway.
- Calendar reckoning/conversion remains `calendars-and-time`; recurring observances
  use the new `public-holidays-and-commemorations` tag.

All first-pass results must retain their exact allowed metadata, rule/evidence
provenance, and explicit queues for unresolved topics, details and flags. No source
transcriptions, previously saved classifications or published pages are modified
by saving a new classification run.
