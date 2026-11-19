# China table classifications completed

All **8,866 tables in 20 China volumes** now have saved classifications.
The original **6,850 Sonnet assignments** are preserved exactly. The assistant
classified the remaining **2,016** directly, with **zero additional external model calls**.
These are draft classifications for user evaluation, not an accuracy-certified dataset.

## Saved files

- [Combined assignments for all 8,866 tables](assignments.china.json)
- [Only the 2,016 new assignments](assignments.remainder.json)
- [Tables without detailed tags](no-detailed-tags.json): **380**
  (373 original, 7 new).
- [Review questions](review-queue.json): **1,166 tables**.
- [Per-table classifier and input provenance](provenance.china.json)
- [Validation results and output hashes](validation.json)
- [Explicit direct decisions](decisions.tsv), [review notes](review-notes.json),
  [semantic check notes](qa.json).

## Method and scope

The direct pass parsed complete frozen table JSON and reviewed body profiles containing
titles, all column labels, part names, row counts and representative body rows.
Verified repeated structures share explicit, authored decisions. Ambiguous descriptions,
generic titles, and suspected numerical content in text tables were read in full as needed.
This was profile-assisted subject review, not a claim that every numerical cell was
individually reread. No keyword rule automatically assigned subjects, no agents or
external model services were invoked, and no OCR was performed.

The existing vocabulary remains version `1.1.0-optional-details`:
32 high-level topics and 327 detailed tags. Each table has 1–2 topics, 0–3 details,
and an independent `text-tables` flag. No detailed tag was forced when a suitable term
or sufficiently clear subject was absent. The original 373 tables without detailed
tags were retained without reclassification.

Text classification distinguishes dates, serials, rank identifiers, addresses and
enumerated lists from substantive quantities. Numerical output, dimensions, staffing,
rates, value thresholds and durations embedded in descriptions count as quantitative
content. The original unfilled survey instruments in the flood volume (direct indices
505–522) are text tables because they contain questions and empty fields, not collected
observations. This does not reclassify damaged or unreadable statistical tables as text.

There are **1,325 text tables** in the combined results,
including **346** in the new direct pass.

## Validation

Passed exact coverage and uniqueness for all 8,866 keys, disjoint classifier coverage,
approved IDs and cardinalities, direct input fingerprints, all 887 frozen batch inputs,
all 20 published source-file hashes, and equality between the 6,850 original aggregate
assignments and their 685 accepted batches. Original Sonnet output is unchanged.
These structural and preservation checks do not establish perfect semantic accuracy.

The labels are saved separately from source data. Website pages and Topics navigation
have not been modified or rebuilt. The expensive Sonnet runner remains stopped.

## Coverage

| Volume | Preserved Sonnet | Direct remainder | Total |
|---|---:|---:|---:|
| Peking: A Social Survey 1921 | 178 | 0 | 178 |
| China, a Commercial and Industrial Handbook 1926 | 313 | 0 | 313 |
| The China Year Book 1912 | 236 | 0 | 236 |
| The China Year Book 1914 | 413 | 0 | 413 |
| The China Year Book 1919 | 416 | 0 | 416 |
| The China Year Book 1913 | 354 | 0 | 354 |
| The China Year Book 1916 | 373 | 0 | 373 |
| The China Year Book 1921-2 | 377 | 0 | 377 |
| The China Year Book 1923 | 508 | 0 | 508 |
| The China Year Book 1924-5 | 517 | 0 | 517 |
| The China Year Book 1925-6 | 635 | 0 | 635 |
| The China Year Book 1926-7 | 615 | 0 | 615 |
| The China Year Book 1928 | 695 | 0 | 695 |
| The China Year Book 1929-30 | 644 | 0 | 644 |
| The China Year Book 1931-2 | 576 | 164 | 740 |
| China Handbook 1944 | 0 | 284 | 284 |
| The 1931 Flood in China: An Economic Survey | 0 | 75 | 75 |
| The China Year Book 1938 | 0 | 572 | 572 |
| China Handbook 1937-1943 | 0 | 573 | 573 |
| China Handbook 1950 | 0 | 348 | 348 |
| **Total** | **6,850** | **2,016** | **8,866** |
