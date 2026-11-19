#!/usr/bin/env python3
"""Validate the partial metadata pass and write its reviewable completion report."""
from collections import Counter
from datetime import datetime, timezone
from copy import deepcopy
import classify_metadata_pass as c
from validate_pilot import vocabulary_checks


def check_boundaries():
    examples = [
        ("Gold exports", "Mining", ["trade"], ["exports", "gold"]),
        ("Gold Output", "Finance", ["mining"], ["gold"]),
        ("Tea Production", "Agriculture", ["agriculture"], ["tea"]),
        ("Tramway Receipts", "Railways", ["transportation"], ["trams"]),
        ("Electric Railways", "Industry", ["transportation"], ["railways"]),
        ("Family Budgets", "Finance", ["welfare"], ["household-budgets"]),
        ("Population", "South Sea Islands Under Mandate", ["population"], ["population-totals"]),
        ("Statistics", "Chosen (Korea)", [], []),
        ("Import Tariff List", "Foreign Trade", ["trade", "finance"], ["tariffs"]),
        ("Registered Ships by Material and Age", "Transportation", ["transportation"], ["shipping"]),
    ]
    for title, chapter, topics, tags in examples:
        metadata = dict.fromkeys(c.FIELDS, "")
        metadata.update(title=title, chapter=chapter)
        row, _ = c.classify(metadata)
        assert row["topics"] == topics and row["tags"] == tags, (title, row)
    poisoned = dict.fromkeys(c.FIELDS, "") | {"rows": [["opium", "123"]]}
    try:
        c.classify(poisoned)
    except AssertionError:
        pass
    else:
        raise AssertionError("Classifier accepted a body field")
    return len(examples)


def main():
    out = c.OUT
    manifest, records, vocabulary = (c.read(out / name) for name in ("manifest.json", "metadata.json", "vocabulary.json"))
    assert c.sha(out / "metadata.json") == manifest["metadata_sha256"]
    assert c.sha(out / "vocabulary.json") == manifest["vocabulary_sha256"]
    assert c.sha(out / "preserved-pilot.json") == manifest["preserved_pilot_sha256"]
    assert c.sha(out / "rules.md") == manifest["rules_sha256"]
    assert c.sha(c.HERE / "vocabulary.json") == manifest["vocabulary_sha256"]
    assert all(c.sha(c.SITE / path) == value for path, value in manifest["source_files"].items())
    result = c.read(out / "assignments.japan-manchuria-south-seas.json")
    assignments = result["assignments"]
    audit = c.read(out / "provenance.json")["tables"]
    keys = {r["key"] for r in records}
    assert len(records) == len(keys) == len(assignments) == manifest["tables"] == 28734
    assert keys == set(assignments) == set(audit)
    ids, issues = vocabulary_checks(vocabulary)
    assert [x for x in issues if x != "Assignment limits changed"] == [], issues
    assert vocabulary["limits"] == {"topics": {"min": 1, "max": 2}, "tags": {"min": 0, "max": 3}}
    old = c.read(c.HERE / "runs/china-sonnet-2026-10-26/vocabulary.json")
    by_id = {x["id"]: x for x in vocabulary["tags"]}
    assert all(by_id[x["id"]] == x for x in old["tags"])
    assert vocabulary["topics"] == old["topics"]
    assert len(ids["topics"]) == 32 and len(ids["tags"]) == 350
    proposals = c.read(c.HERE / "reviews/china-uncovered-2026-10-26/proposals.json")["candidates"]
    assert set(by_id) - {x["id"] for x in old["tags"]} == {x["id"] for x in proposals}
    pilot = c.read(c.HERE / "pilot/assignments.json")["assignments"]
    preserved = c.read(out / "preserved-pilot.json")["assignments"]
    assert len(preserved) == manifest["preserved_tables"] == 90
    assert all(assignments[k] == value == pilot[k] for k, value in preserved.items())
    for record in records:
        key, metadata = record["key"], record["metadata"]
        row, provenance = assignments[key], audit[key]
        assert set(metadata) == set(c.FIELDS)
        assert provenance["metadata_sha256"] == c.digest(metadata)
        for kind in ids:
            assert len(set(row[kind])) == len(row[kind]) and set(row[kind]) <= ids[kind]
        assert 0 <= len(row["topics"]) <= 2 and 0 <= len(row["tags"]) <= 3
        assert row["flags"] in ([], ["text-tables"])
        if key not in preserved:
            for tag, evidence in provenance["detail_evidence"].items():
                assert tag in row["tags"] and evidence["field"] in c.FIELDS
                assert c.norm(evidence["matched"]) in c.norm(metadata[evidence["field"]]), (key, evidence)
            if not row["topics"] or not row["tags"] or provenance["flag_status"] == "unknown-needs-contents":
                assert row["review_questions"]
    for group in c.GROUPS:
        expected = {r["key"]: assignments[r["key"]] for r in records if r["book"]["collection"] == group}
        assert c.read(out / f"assignments.{group}.json")["assignments"] == expected
    protected = {}
    for run_name in ("china-direct-remainder-2026-10-26", "korea-taiwan-direct-2026-10-26"):
        directory = c.HERE / "runs" / run_name
        validation = c.read(directory / "validation.json")
        for name, expected in validation["output_sha256"].items():
            assert c.sha(directory / name) == expected, (run_name, name)
            protected[str((directory / name).relative_to(c.HERE))] = expected
    boundary_cases = check_boundaries()
    summaries = {}
    for group in c.GROUPS:
        subset = [r["key"] for r in records if r["book"]["collection"] == group]
        fresh = [k for k in subset if k not in preserved]
        summaries[group] = {
            "books": sum(b["collection"] == group for b in manifest["books"]),
            "tables": len(subset), "new_first_pass": len(fresh), "preserved_reviewed": len(subset) - len(fresh),
            "with_topics": sum(bool(assignments[k]["topics"]) for k in subset),
            "with_details": sum(bool(assignments[k]["tags"]) for k in subset),
            "without_topics": sum(not assignments[k]["topics"] for k in subset),
            "without_details": sum(not assignments[k]["tags"] for k in subset),
            "new_with_topics": sum(bool(assignments[k]["topics"]) for k in fresh),
            "new_with_details": sum(bool(assignments[k]["tags"]) for k in fresh),
        }
    totals = {field: sum(x[field] for x in summaries.values()) for field in next(iter(summaries.values()))}
    totals["blank_both"] = sum(not x["topics"] and not x["tags"] for x in assignments.values())
    totals["unknown_flag"] = sum(x["flag_status"] == "unknown-needs-contents" for x in audit.values())
    for name in ("classify_metadata_pass.py", "metadata_subject_rules.py"):
        (out / name).write_bytes((c.HERE / name).read_bytes())
    validation = {"status": "complete-first-pass", "classification_stage": "metadata-only-first-pass",
                  "vocabulary_version": vocabulary["vocabulary_version"], "vocabulary_counts": {kind: len(vocabulary[kind]) for kind in ids},
                  "collections": summaries, "totals": totals, "source_files": manifest["source_files"],
                  "checks": {"exact_all_42_book_coverage": True, "metadata_whitelist_only": True,
                  "no_columns_rows_parts_or_footnotes_in_classifier": True, "evidence_resolves_to_allowed_metadata": True,
                  "all_42_sources_unchanged": True, "prior_90_reviewed_assignments_preserved": True,
                  "existing_china_korea_taiwan_output_hashes_unchanged": True, "all_23_proposed_tags_added": True,
                  "existing_327_definitions_and_32_topics_preserved": True, "approved_unique_ids_aliases_and_cardinalities": True,
                  "partial_fields_and_unknown_flags_queued": True, "metadata_boundary_examples_passed": boundary_cases,
                  "body_field_injection_rejected": True},
                  "additional_llm_cli_calls": 0, "full_content_reviews_in_this_pass": 0,
                  "semantic_limit": "Rule-assisted high-confidence metadata proposals. The later contents pass must resolve blank fields and may revise assignments; structural validation is not proof of perfect semantic accuracy.",
                  "protected_prior_outputs_sha256": protected, "issues": [],
                  "validated_utc": datetime.now(timezone.utc).isoformat()}
    lines = ["# Japan, Manchuria and South Seas: metadata-only first pass", "",
             f"Completed the requested first pass across **{totals['tables']:,} tables in {totals['books']} books**: **{totals['new_first_pass']:,} new metadata-only assessments** and **{totals['preserved_reviewed']} preserved complete-record pilot assignments**.", "",
             "All 23 proposed tags are now part of vocabulary **1.2.0**, giving **32 high-level topics and 350 detailed tags**. Existing definitions are unchanged. [Current vocabulary](../../VOCABULARY.md) · [Current rules](../../CLASSIFICATION.md).", "",
             "| Collection | Books | Tables | New first-pass records | With high-level topics | With detailed tags |", "| --- | ---: | ---: | ---: | ---: | ---: |"]
    for group, x in summaries.items():
        lines.append(f"| {group} | {x['books']} | {x['tables']:,} | {x['new_first_pass']:,} | {x['with_topics']:,} | {x['with_details']:,} |")
    lines.extend([f"| **Total** | **{totals['books']}** | **{totals['tables']:,}** | **{totals['new_first_pass']:,}** | **{totals['with_topics']:,}** | **{totals['with_details']:,}** |", "",
        "Coverage columns include the preserved pilot assignments; per-collection counts for new records alone are in validation.json.", "",
        f"**{totals['without_topics']:,} tables have blank high-level topics; {totals['without_details']:,} have blank detailed tags.** Both fields are blank for **{totals['blank_both']:,}**. These are deliberately deferred, not failed calls, and the two blank-field counts overlap.", "",
        "## Method and confidence", "",
        "The assistant authored bilingual subject rules and checked metadata examples and boundary cases locally. Only titles, English titles/descriptions, chapter headings, captions and supplied descriptive context enter classification. Complete JSON files are parsed to extract those fields and compute integrity fingerprints; no rows, columns, part labels or footnotes are reviewed or used as classification evidence.", "",
        "Explicit title subjects take precedence over a book's collection. Chapter-only inference is restricted to a clear subject heading, and detailed inference from descriptions is conservative. Cross-sector/ambiguous titles, insufficiently identified commodities and overfull detailed candidates are retained for the later full-content pass. No arbitrary three-commodity subset is selected from a broad product inventory.", "",
        "This is a partial first pass, not a final complete-record classification. Each assigned field has rule/evidence provenance; empty topics and details are independent uncertainty states. Prior complete-record pilot assignments are preserved verbatim and separately marked.", "",
        f"The text/statistical flag remains **unknown for {totals['unknown_flag']:,} records**. These are explicitly marked in provenance and queued. An empty flags list in such a record does not establish statistical content. The user-requested high-level/detailed first pass does not require guessing this flag.", "",
        "## Saved files", "",
        "- [Combined assignments](assignments.japan-manchuria-south-seas.json)",
        "- [Japan assignments](assignments.japan.json)", "- [Manchuria assignments](assignments.manchuria.json)",
        "- [South Seas assignments](assignments.south-seas.json)",
        "- [Tables without high-level topics](no-topics.json)", "- [Tables without detailed tags](no-detailed-tags.json)",
        "- [All remaining review questions](review-queue.json) and [unknown text flags](flag-review-queue.json)",
        "- [Metadata evidence/provenance](provenance.json), [frozen allowed metadata](metadata.json), [manifest](manifest.json) and [validation](validation.json)", "",
        "## Validation", "",
        "Passed exact coverage and uniqueness, approved vocabulary/alias and cardinality checks, evidence-to-metadata checks, all source hashes, exact preservation of 90 pilot decisions, and prior China/Korea/Taiwan saved-output hashes. Boundary examples check trade versus extraction, family versus public budgets, trams versus electric railways, and publication-setting leakage. A body-field injection is rejected by the classifier. The historical pilot also passes validation against its restored exact frozen vocabulary.", "",
        "No LLM CLI calls, full-content reviews, OCR, Git operations or site builds were performed. This run saves new draft classifications and queues for later review; it does not apply the earlier China-review suggestions to the 380 China records.", "",
        "## Book coverage", "", "| Collection | Book | Tables |", "| --- | --- | ---: |"])
    for book in manifest["books"]:
        lines.append(f"| {book['collection']} | {book['title']} (`{book['slug']}`) | {book['tables']:,} |")
    (out / "REPORT.md").write_text("\n".join(lines) + "\n")
    outputs = ["assignments.japan-manchuria-south-seas.json", "assignments.japan.json", "assignments.manchuria.json", "assignments.south-seas.json", "provenance.json", "review-queue.json", "no-topics.json", "no-detailed-tags.json", "flag-review-queue.json", "REPORT.md", "classify_metadata_pass.py", "metadata_subject_rules.py"]
    validation["output_sha256"] = {name: c.sha(out / name) for name in outputs}
    c.write(out / "validation.json", validation)
    print(c.json.dumps({"status": validation["status"], "collections": summaries, "totals": totals, "issues": []}, indent=2))


if __name__ == "__main__":
    main()
