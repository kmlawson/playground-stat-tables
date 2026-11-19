#!/usr/bin/env python3
"""Validate and merge saved China classifications without invoking a model."""
from collections import Counter
import classify_china_remainder as direct
import run_china_sonnet as sonnet


def main():
    base, out = direct.BASE, direct.OUT
    read, write = sonnet.read, sonnet.write
    manifest = read(base / 'manifest.json')
    direct_manifest = read(out / 'manifest.json')
    vocab = read(base / 'vocabulary.json')
    original_hash = sonnet.sha(base / 'assignments.json')
    if original_hash != direct_manifest['existing_assignments_sha256']:
        raise ValueError('Original Sonnet assignments changed during direct review')
    original = read(base / 'assignments.json')['assignments']
    accepted, done, issues, _ = sonnet.collect(manifest, vocab)
    issues += sonnet.frozen_checks(manifest)
    if accepted != original or len(original) != 6850 or len(done) != 685:
        issues.append('Original aggregate differs from its 685 accepted batches')
    wrappers, sources, inventory = sonnet.load_china()
    if sources != manifest['source_files']:
        issues.append('Published China sources changed')
    new = read(out / 'assignments.remainder.json')['assignments']
    decisions = read(out / 'decisions.json')
    expected = {w['key'] for w in wrappers} - set(original)
    if set(new) != expected or len(new) != 2016 or set(original) & set(new):
        issues.append('Direct assignments do not exactly cover the remainder')
    if set(decisions) != expected:
        issues.append('Direct provenance does not exactly cover the remainder')
    direct_inputs = {x['key']: x for x in direct_manifest['tables']}
    merged, provenance = {}, {}
    batches = {key: batch for batch in manifest['batches'] for key in batch['keys']}
    for wrapper in wrappers:
        key = wrapper['key']
        fingerprint = sonnet.digest({'book': wrapper['book'], 'table': wrapper['table']})
        batch = batches[key]
        if fingerprint != batch['input_sha256'][key]:
            issues.append('Current record differs from frozen input: ' + key)
        if key in original:
            merged[key] = original[key]
            provenance[key] = {'classifier': sonnet.MODEL, 'source_batch': batch['id'],
                               'input_sha256': fingerprint}
        elif key in new:
            merged[key] = new[key]
            provenance[key] = {**decisions[key], 'classifier': 'assistant-direct',
                               'source_batch': batch['id']}
            if fingerprint != direct_inputs[key]['input_sha256'] or fingerprint != decisions[key]['input_sha256']:
                issues.append('Direct input fingerprint differs: ' + key)
    result = {'schema_version': 1, 'collection': 'china', 'classifier': 'mixed',
              'vocabulary_version': vocab['vocabulary_version'],
              'review_status': 'draft-classifications-not-user-reviewed',
              'classifiers': {sonnet.MODEL: len(original), 'assistant-direct': len(new)},
              'assignments': merged}
    issues += sonnet.row_issues(result, {'keys': [w['key'] for w in wrappers]}, vocab)
    if issues:
        raise ValueError(issues)
    write(out / 'assignments.china.json', result)
    write(out / 'provenance.china.json', {'schema_version': 1, 'tables': provenance})
    brief = []
    for wrapper in wrappers:
        key = wrapper['key']
        brief.append({'key': key, 'book': wrapper['book'],
                      'title': (wrapper['table'].get('en') or {}).get('t') or wrapper['table']['title'],
                      **merged[key], 'classifier': provenance[key]['classifier']})
    no_details = [row for row in brief if not row['tags']]
    questions = [row for row in brief if row['review_questions']]
    write(out / 'no-detailed-tags.json', {'count': len(no_details), 'tables': no_details})
    write(out / 'review-queue.json', {'count': len(questions), 'tables': questions})
    if sonnet.sha(base / 'assignments.json') != original_hash:
        raise ValueError('Original output changed while finalizing')
    validation = {
        'status': 'complete', 'collection': 'china', 'tables': len(merged), 'books': len(inventory),
        'sonnet_preserved': len(original), 'direct_added': len(new), 'additional_external_model_calls': 0,
        'without_detailed_tags': len(no_details),
        'original_without_detailed_tags_preserved': sum(not r['tags'] for r in original.values()),
        'direct_without_detailed_tags': sum(not r['tags'] for r in new.values()),
        'text_tables': sum(bool(r['flags']) for r in merged.values()),
        'direct_text_tables': sum(bool(r['flags']) for r in new.values()),
        'tables_with_review_questions': len(questions),
        'vocabulary_version': vocab['vocabulary_version'],
        'vocabulary_counts': {k: len(vocab[k]) for k in ('topics', 'tags', 'flags')},
        'checks': {'exact_key_coverage': True, 'no_overlap': True, 'approved_ids_and_cardinalities': True,
                   'all_frozen_inputs_unchanged': True, 'all_published_source_hashes_unchanged': True,
                   'original_6850_assignments_unchanged': True, 'original_matches_accepted_batches': True,
                   'direct_input_fingerprints_match': True},
        'original_assignments_sha256': original_hash,
        'output_sha256': {name: sonnet.sha(out / name) for name in
                          ('assignments.remainder.json', 'assignments.china.json', 'provenance.china.json',
                           'no-detailed-tags.json', 'review-queue.json', 'decisions.tsv', 'review-notes.json')},
        'topic_counts': dict(Counter(t for r in merged.values() for t in r['topics'])),
        'tag_counts': dict(Counter(t for r in merged.values() for t in r['tags'])),
        'issues': [], 'validated_utc': sonnet.now()}
    write(out / 'validation.json', validation)
    book_lines = []
    for book in inventory:
        prefix = book['slug'] + ':'
        old_count = sum(k.startswith(prefix) for k in original)
        new_count = sum(k.startswith(prefix) for k in new)
        book_lines.append(f"| {book['title']} | {old_count:,} | {new_count:,} | {old_count + new_count:,} |")
    report = f"""# China table classifications completed

All **{len(merged):,} tables in {len(inventory)} China volumes** now have saved classifications.
The original **{len(original):,} Sonnet assignments** are preserved exactly. The assistant
classified the remaining **{len(new):,}** directly, with **zero additional external model calls**.
These are draft classifications for user evaluation, not an accuracy-certified dataset.

## Saved files

- [Combined assignments for all 8,866 tables](assignments.china.json)
- [Only the 2,016 new assignments](assignments.remainder.json)
- [Tables without detailed tags](no-detailed-tags.json): **{len(no_details):,}**
  ({validation['original_without_detailed_tags_preserved']} original, {validation['direct_without_detailed_tags']} new).
- [Review questions](review-queue.json): **{len(questions):,} tables**.
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

The existing vocabulary remains version `{vocab['vocabulary_version']}`:
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

There are **{validation['text_tables']:,} text tables** in the combined results,
including **{validation['direct_text_tables']}** in the new direct pass.

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
{chr(10).join(book_lines)}
| **Total** | **6,850** | **2,016** | **8,866** |
"""
    (out / 'REPORT.md').write_text(report)
    print(direct.compact({k: validation[k] for k in
                         ('status', 'tables', 'sonnet_preserved', 'direct_added', 'without_detailed_tags',
                          'direct_without_detailed_tags', 'text_tables', 'tables_with_review_questions', 'issues')}))


if __name__ == '__main__':
    main()
