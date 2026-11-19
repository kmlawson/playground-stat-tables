#!/usr/bin/env python3
"""Consolidate advisory reviews; never modify vocabulary or assignments."""

import hashlib
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
TAGS = ROOT / "stat-tables-site/build/tags"
OUT = TAGS / "reviews/china-uncovered-2026-10-26"
KT = TAGS / "runs/korea-taiwan-direct-2026-10-26"
ALIASES = {
    "commodity-geography": "commodity-origins",
    "regional-products": "commodity-origins",
    "distances-and-journey-times": "route-distances",
    "holidays-and-commemorations": "public-holidays-and-commemorations",
}
RECOMMENDED = [
    "route-distances",
    "commodity-origins",
    "anthropometry",
    "census-and-survey-methods",
    "public-holidays-and-commemorations",
    "legal-profession",
    "writing-systems-and-phonetics",
    "real-estate",
    "printing",
    "professional-associations",
]
OPTIONAL = [
    "demobilisation", "asbestos", "mercury", "school-curricula",
    "domestic-service", "native-place-associations", "fish-and-fish-products",
    "militias-and-volunteer-forces",
]
BOUNDARY = [
    "diplomatic-claims", "colonies-and-leased-territories", "foreign-trade",
    "foreign-trade-relations",
]
NOTES = {
    "route-distances": "A reusable cross-mode discovery term. Many sea/river/rail examples already admit a transport-mode tag; the new term identifies the distance or journey-time reference itself.",
    "commodity-origins": "Merge all three proposed names into one tag. Especially useful for qualitative, multi-sector product-to-region inventories; do not select three arbitrary commodities instead.",
    "anthropometry": "Covers the source's bodily measurements and historical physical typologies. Keep the historical wording in the source without adopting its theories as modern classifications.",
    "census-and-survey-methods": "One broad methods tag can cover population census forms and agricultural sampling. The farm-sample table deferred by reviewer 4 fits this proposal from reviewer 1; no separate agricultural-surveys tag is needed.",
    "public-holidays-and-commemorations": "Keep observances distinct from calendar conversion/time reckoning. Reviewer 2's suggested calendars-and-time reuse would require a definition change and is not accepted under the current rules.",
    "legal-profession": "Practitioner qualification and licensing are distinct from court establishments/caseload and population-by-occupation distributions.",
    "writing-systems-and-phonetics": "Distinguishes scripts, phonetic symbols and sound representation from language distribution and language instruction.",
    "real-estate": "Useful for market rents and transactions in land and buildings. One of the three evidence records has an uncertain lead-in and needs context confirmation before assignment.",
    "printing": "A productive activity spanning books, newspapers and other printed matter; distinct from paper production and publication type.",
    "professional-associations": "Only one example in this subset, but the institution type is reusable across medical, legal and engineering professions. Keep separate from commercial associations and trade unions.",
    "demobilisation": "Existing army/public-budgets tags already fit the disbandment accounts. This adds process specificity.",
    "asbestos": "Existing industrial-output fits the evidence. Three editions repeat a company's manufactured-product series; recurrence is not three independent industries.",
    "mercury": "Existing exports/mineral-production already fit. Consider this as commodity precision consistent with other named mineral tags.",
    "school-curricula": "Existing primary-education fits the example. A cross-stage curriculum term is optional refinement.",
    "domestic-service": "A coherent household-labour subject, currently supported by one table in the reviewed subset.",
    "native-place-associations": "One clear origin-based association example. Do not generalise this tag to all guilds, businesses or overseas communities.",
    "fish-and-fish-products": "Could cover fish commodities in trade without assuming capture or cultivation. One example; first decide whether to broaden the existing fishing definition instead.",
    "militias-and-volunteer-forces": "Existing army already covers the volunteer-corps series. Optional narrower discovery term.",
    "diplomatic-claims": "One pending compensation-claims table. Decide whether indemnities should explicitly include claims not yet imposed or accepted before creating a separate term.",
    "colonies-and-leased-territories": "One political-possession inventory. Check boundaries with colonial-administration, annexation-and-protectorates and administrative-divisions; never apply merely because a table comes from a colonial volume.",
    "foreign-trade": "One clean aggregate example supports a combined merchandise-trade concept. Five other records have missing commodity/direction context; a broader tag cannot repair that source uncertainty. Compare allowing imports plus exports for combined totals.",
    "foreign-trade-relations": "The same seven-event first-contact chronology appears in six editions across batches. Prefer a deliberate decision about subject-specific historical-chronologies before adding a trade-history synonym.",
    "riots-and-civil-unrest": "Conditional on confirming the Pingyang casualty table's link to the running section The Korean Riots. Do not infer the cause from a vague disaster title alone.",
}


def read(path):
    return json.loads(path.read_text())


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(name, data):
    (OUT / name).write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n")


def append_unique(target, values):
    target.extend(x for x in values if x not in target)


def main():
    manifest = read(OUT / "manifest.json")
    source = ROOT / manifest["source"]
    assert digest(source) == manifest["source_sha256"]
    vocab = read(KT / "vocabulary.json")
    tag_ids = {x["id"] for x in vocab["tags"]}
    topic_ids = {x["id"] for x in vocab["topics"]}
    protected = [
        source, TAGS / "vocabulary.json", KT / "vocabulary.json",
        KT / "assignments.korea-taiwan.json", KT / "assignments.korea.json",
        KT / "assignments.taiwan.json",
        TAGS / "runs/china-direct-remainder-2026-10-26/assignments.china.json",
        TAGS / "runs/china-sonnet-2026-10-26/assignments.json",
    ]
    protected_hashes = {str(p.relative_to(ROOT)): digest(p) for p in protected}
    records, assessments, candidates, batch_counts, review_hashes = {}, {}, {}, {}, {}
    reviewer_existing_keys = set()

    for n in range(1, 5):
        batch = f"review-{n}"
        input_path, result_path = OUT / f"{batch}.input.json", OUT / f"{batch}.result.json"
        inputs, result = read(input_path), read(result_path)
        keys = [x["key"] for x in inputs["tables"]]
        assert len(keys) == len(set(keys)) == 95
        assert set(keys) == set(manifest["batches"][batch])
        assert len(result["reviewed_keys"]) == 95 and set(result["reviewed_keys"]) == set(keys)
        assert not (set(keys) & records.keys())
        batch_counts[batch] = len(keys)
        review_hashes[batch] = {"input_sha256": digest(input_path), "result_sha256": digest(result_path)}
        for record in inputs["tables"]:
            key = record["key"]
            assert record["existing_assignment"]["tags"] == []
            records[key] = record
            assessments[key] = {
                "key": key, "review_batch": batch,
                "reviewer_existing_tag_fits": [], "existing_tag_options": [],
                "candidate_ids": [], "deferred_notes": [], "consolidation_notes": [],
            }
        for fit in result["existing_tag_fits"]:
            key = fit["key"]
            assert key in keys and 1 <= len(fit["tags"]) <= 3
            assert set(fit["tags"]) <= tag_ids
            reviewer_existing_keys.add(key)
            assessments[key]["reviewer_existing_tag_fits"].append(fit)
            append_unique(assessments[key]["existing_tag_options"], fit["tags"])
        for item in result["deferred"]:
            assert item["key"] in keys
            assessments[item["key"]]["deferred_notes"].append(item["reason"])
        for proposal in result["candidates"]:
            assert set(proposal["evidence_keys"]) <= set(keys)
            assert proposal["id"] not in tag_ids
            assert set(proposal["related_topics"]) <= topic_ids
            identifier = ALIASES.get(proposal["id"], proposal["id"])
            if identifier not in candidates:
                candidates[identifier] = {
                    "id": identifier, "label": proposal["label"],
                    "definition": proposal["definition"], "includes": [], "excludes": [],
                    "related_topics": [], "proposed_name_variants": [], "evidence_keys": [],
                    "reviewer_sources": [], "consolidation_evidence": [],
                }
            candidate = candidates[identifier]
            for field in ("includes", "excludes", "related_topics", "evidence_keys"):
                append_unique(candidate[field], proposal[field])
            append_unique(candidate["proposed_name_variants"], [proposal["id"]])
            candidate["reviewer_sources"].append({"batch": batch, "proposal": proposal})

    assert len(records) == manifest["tables"] == 380
    source_data = read(source)
    source_keys = {x["key"] for x in source_data["tables"]}
    assert source_keys == set(records)

    candidates["route-distances"].update({
        "label": "route distances and journey times",
        "definition": "Measured distances or elapsed journey times between named places along travel routes, including comparative origin-destination references across transport modes.",
    })
    candidates["commodity-origins"]["label"] = "commodity origins"
    candidates["public-holidays-and-commemorations"]["label"] = "public holidays and commemorations"

    # Resolve cross-batch inconsistencies without changing any saved classification.
    calendar_key = "china-1922:p1009_1"
    assessments[calendar_key]["existing_tag_options"] = []
    assessments[calendar_key]["consolidation_notes"].append(NOTES["public-holidays-and-commemorations"])
    cross_batch_evidence = {
        "census-and-survey-methods": ["china-1929-30:p0971_1"],
        "foreign-trade-relations": [
            "china-1914:p0128_1", "china-1913:p0108_1",
            "china-1916:p0127_1", "china-1922:p0227_1",
        ],
    }
    for identifier, keys in cross_batch_evidence.items():
        candidate = candidates[identifier]
        for key in keys:
            assert key in records
            append_unique(candidate["evidence_keys"], [key])
            candidate["consolidation_evidence"].append({"key": key, "reason": NOTES[identifier]})
            assessments[key]["consolidation_notes"].append(NOTES[identifier])
    farm_key = "china-1929-30:p0971_1"
    assessments[farm_key]["resolved_reviewer_deferral"] = assessments[farm_key]["deferred_notes"]
    assessments[farm_key]["deferred_notes"] = []
    append_unique(candidates["census-and-survey-methods"]["related_topics"], ["agriculture"])
    candidates["census-and-survey-methods"]["includes"].append("Survey sample design and the allocation of sampled units by place or stratum.")

    order = RECOMMENDED + OPTIONAL + BOUNDARY + ["riots-and-civil-unrest"]
    assert set(order) == set(candidates)
    for identifier in order:
        candidate = candidates[identifier]
        candidate["status"] = "proposed-not-applied"
        candidate["recommendation"] = (
            "recommend" if identifier in RECOMMENDED else
            "optional-refinement" if identifier in OPTIONAL else
            "boundary-decision-first" if identifier in BOUNDARY else "conditional-source-check"
        )
        candidate["consolidation_note"] = NOTES[identifier]
        candidate["evidence_count"] = len(candidate["evidence_keys"])
        candidate["existing_vocabulary_options_count"] = sum(bool(assessments[k]["existing_tag_options"]) for k in candidate["evidence_keys"])
        candidate["deferred_evidence_keys"] = [k for k in candidate["evidence_keys"] if assessments[k]["deferred_notes"]]
        for key in candidate["evidence_keys"]:
            append_unique(assessments[key]["candidate_ids"], [identifier])

    for assessment in assessments.values():
        assessment["disposition"] = (
            "existing-vocabulary-option" if assessment["existing_tag_options"] else
            "unresolved-context-or-boundary" if assessment["deferred_notes"] else
            "proposed-vocabulary-candidate"
        )
        assert assessment["existing_tag_options"] or assessment["candidate_ids"] or assessment["deferred_notes"]
    dispositions = dict(Counter(x["disposition"] for x in assessments.values()))
    counts = {
        "reviewed_tables": len(records), "reviewers": 4, "tables_per_reviewer": batch_counts,
        "reviewer_existing_vocabulary_suggestions": len(reviewer_existing_keys),
        "consolidated_dispositions": dispositions, "merged_candidates": len(candidates),
        "recommended_candidates": len(RECOMMENDED), "optional_candidates": len(OPTIONAL),
        "boundary_decisions": len(BOUNDARY), "conditional_candidates": 1,
    }
    metadata = {
        "status": "advisory-review-complete", "vocabulary_version": vocab["vocabulary_version"],
        "vocabulary_modified": False, "assignments_modified": False,
        "method": "Four agents each examined 95 complete frozen records. Consolidation merges overlapping proposals, distinguishes existing-tag reuse from subject gaps, and resolves cross-batch methods/holiday inconsistencies. No external LLM CLI calls.",
        "counts": counts,
        "count_caveat": "Evidence counts refer only to the reviewed subset. Annual editions can repeat a series, candidates can overlap, and some evidence is conditional. Counts are not corpus-wide demand or automatic assignments.",
        "source": manifest["source"], "source_sha256": manifest["source_sha256"],
        "vocabulary_sha256": digest(KT / "vocabulary.json"), "review_files": review_hashes,
    }
    write("proposals.json", {**metadata, "candidates": [candidates[x] for x in order]})
    write("table-assessments.json", {**metadata, "tables": list(assessments.values())})

    lines = [
        "# China tables without detailed tags: four-agent vocabulary review", "",
        "Review complete. All **380** frozen records were examined in four batches of **95**, using their complete table bodies, headings and supplied context. These are proposals for evaluation; the vocabulary and saved classifications have not been changed.", "",
        "## What the review found", "",
        "The reviewers suggested possible existing tags for **301** tables. Consolidation retained **300** such options: one public-holiday table requires a new observance tag or an explicit definition change, rather than the current calendars-and-time tag.", "",
        "The other **80** records divide into **53** with a proposed vocabulary candidate and **27** still needing source-context or vocabulary-boundary decisions. Some of the 27 also have conditional candidate suggestions. Existing-tag options are advisory, not applied corrections.", "",
        "Overlapping reviewer names were merged into **23** candidate tags: **10 recommended**, **8 optional refinements**, **4 boundary decisions**, and **1 conditional candidate**. All fit within the current high-level structure; no additional high-level topic is proposed.", "",
        "## Recommended additions", "",
        "| Proposed detailed tag | Evidence tables | Purpose and boundary |", "| --- | ---: | --- |",
    ]
    for identifier in RECOMMENDED:
        c = candidates[identifier]
        lines.append(f"| `{identifier}` | {c['evidence_count']} | {NOTES[identifier]} |")
    lines.extend([
        "", "Evidence counts cover this 380-table subset only. The real-estate count includes one uncertain lead-in. Repeated annual series are not independent subjects. Route distances often already admit shipping, inland-navigation or railways; the new tag provides a common route-reference subject.", "",
        "The census-and-survey-methods proposal includes **one farm-sample distribution** noticed in another review batch, giving four examples without introducing a separate farm-surveys tag.", "",
        "## Optional refinements", "",
        "| Candidate | Evidence tables | Evaluation |", "| --- | ---: | --- |",
    ])
    for identifier in OPTIONAL:
        c = candidates[identifier]
        lines.append(f"| `{identifier}` | {c['evidence_count']} | {NOTES[identifier]} |")
    lines.extend(["", "## Decide existing-tag boundaries first", "", "| Candidate | Evidence tables | Decision |", "| --- | ---: | --- |"])
    for identifier in BOUNDARY:
        c = candidates[identifier]
        lines.append(f"| `{identifier}` | {c['evidence_count']} | {NOTES[identifier]} |")
    lines.extend([
        "", "## Conditional candidate", "",
        "`riots-and-civil-unrest` — one table. " + NOTES["riots-and-civil-unrest"], "",
        "## Evidence and audit files", "",
        "[Structured proposals](proposals.json) contain definitions, inclusion/exclusion boundaries, related high-level topics, all evidence keys, and the original reviewer proposals. [Per-table assessments](table-assessments.json) cover every one of the 380 records, including existing-tag options and unresolved questions. [Validation](validation.json) checks exact coverage, approved existing IDs and unchanged saved files.", "",
        "### Recommended-tag evidence", "",
    ])
    for identifier in RECOMMENDED:
        lines.extend([f"**{identifier}**", ""])
        for key in candidates[identifier]["evidence_keys"]:
            t = records[key]["table"]
            title = t.get("title") or t.get("title_en") or "Untitled table"
            title = title.replace("\n", " ").replace("[", "(").replace("]", ")")
            scans = t.get("scans", [])
            scan_url = next((x.get("url") for x in scans if x.get("url")), None)
            label = f"`{key}` — {title}"
            lines.append(f"- {label}" + (f" ([scan]({scan_url}))" if scan_url else ""))
        lines.append("")
    lines.extend(["## Individual reviews", ""])
    for n in range(1, 5):
        lines.append(f"- [Review {n}: 95 tables](review-{n}.REPORT.md) · [structured result](review-{n}.result.json)")
    (OUT / "REPORT.md").write_text("\n".join(lines) + "\n")

    assert all(digest(ROOT / path) == value for path, value in protected_hashes.items())
    write("validation.json", {
        "status": "passed", "validated_utc": datetime.now(timezone.utc).isoformat(),
        "counts": counts,
        "checks": {
            "four_disjoint_batches_of_95": True, "all_380_source_keys_reviewed_exactly": True,
            "all_candidate_evidence_in_reviewed_inputs": True, "existing_tag_suggestions_use_approved_ids": True,
            "candidate_ids_do_not_collide_with_existing_tags": True,
            "candidate_topics_use_approved_ids": True, "every_record_has_assessment": True,
            "saved_vocabulary_and_assignments_unchanged": True,
        },
        "protected_files_sha256": protected_hashes,
        "output_sha256": {name: digest(OUT / name) for name in ("proposals.json", "table-assessments.json", "REPORT.md")},
        "issues": [],
    })
    print(json.dumps(counts, indent=2))


if __name__ == "__main__":
    main()
