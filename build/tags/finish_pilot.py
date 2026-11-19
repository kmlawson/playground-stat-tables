#!/usr/bin/env python3
"""Reconcile reviewed batches and render a readable, auditable pilot package.

Reads only frozen pilot inputs and review decisions. Never writes published data.
"""
import csv
from collections import Counter
import json
from pathlib import Path

from validate_pilot import manifest_checks, result_checks, vocabulary_checks

HERE = Path(__file__).resolve().parent
PILOT = HERE / "pilot"


def read(path):
    return json.loads(path.read_text())


def write(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n")


def cell(value):
    return str(value).replace("|", "&#124;").replace("\n", " ")


def main():
    vocab = read(HERE / "vocabulary.json")
    manifest = read(PILOT / "manifest.json")
    decisions = read(PILOT / "resolutions.json")
    ids, issues = vocabulary_checks(vocab)
    issues += manifest_checks(manifest, vocab)
    if decisions["vocabulary_version"] != vocab["vocabulary_version"]:
        issues.append("Review decisions use a different vocabulary version")
    versions = {vocab["vocabulary_version"]: vocab}
    initial = manifest.get("initial_vocabulary")
    if initial:
        versions[initial["version"]] = read(PILOT / initial["path"])
    for archive in manifest.get("archived_vocabularies", []):
        versions[archive["version"]] = read(PILOT / archive["path"])

    raw, independent = {}, {}
    for path in sorted((PILOT / "batches").glob("*.json")):
        batch = read(path)
        result = read(PILOT / "results" / (batch["batch_id"] + ".json"))
        if result.get("batch_id") != batch["batch_id"]:
            issues.append("Result/batch identity mismatch: " + path.name)
        version = versions[batch["vocabulary_version"]]
        version_ids, version_issues = vocabulary_checks(version)
        issues += version_issues
        issues += result_checks(result, [x["key"] for x in batch["items"]], version_ids, version)
        for key, assignment in result["assignments"].items():
            if key in raw:
                issues.append("Duplicate result identity: " + key)
            raw[key] = {"assignment": assignment, "batch_id": batch["batch_id"],
                        "vocabulary_version": result["vocabulary_version"]}
        independent.update(result.get("boundary_reviews", {}))
    consistency = read(PILOT / "consistency-review.json")
    for key, review in consistency["reviews"].items():
        independent[key] = review
    expected = {e["key"] for e in manifest["tables"]}
    if set(raw) != expected:
        issues.append("Raw results do not cover exactly the frozen selection")
    if set(decisions["decisions"]) - expected or set(independent) - expected:
        issues.append("Review refers to a table outside the pilot")
    if issues:
        raise ValueError("\n".join(issues))

    final, review = {}, {}
    table_rows = []
    for entry in manifest["tables"]:
        key = entry["key"]
        original = raw[key]["assignment"]
        decision = decisions["decisions"].get(key)
        assignment = dict(original)
        if decision:
            for field in ("topics", "tags", "flags", "rationale"):
                assignment[field] = decision[field]
            assignment["review_questions"] = []
        if assignment["review_questions"]:
            raise ValueError("Unresolved classification: " + key)
        final[key] = assignment
        wrapper = read(PILOT / entry["input"])
        table = wrapper["table"]
        title = (table.get("en") or {}).get("t") or table.get("title_en") or table["title"]
        changed = any(assignment[f] != original[f] for f in ("topics", "tags", "flags"))
        review[key] = {
            "book": wrapper["book"], "title": title, "original_title": table["title"],
            "input": entry["input"], "input_sha256": entry["input_sha256"],
            "raw_batch": raw[key]["batch_id"],
            "raw_vocabulary_version": raw[key]["vocabulary_version"],
            "raw_assignment": original, "independent_review": independent.get(key),
            "central_decision": decision, "classification_changed": changed,
            "final_assignment": assignment,
        }
        table_rows.append({
            "key": key, "book": wrapper["book"]["title"],
            "collection": wrapper["book"]["collection"], "title": title,
            "original_title": table["title"],
            "topics": "; ".join(assignment["topics"]),
            "detailed_tags": "; ".join(assignment["tags"]),
            "text_table": "yes" if assignment["flags"] else "no",
            "rationale": assignment["rationale"], "input": entry["input"],
        })
    output = {"schema_version": 1, "pilot_id": manifest["pilot_id"],
              "vocabulary_version": vocab["vocabulary_version"], "assignments": final}
    issues = result_checks(output, expected, ids, vocab)
    if issues:
        raise ValueError("\n".join(issues))
    write(PILOT / "assignments.json", output)
    write(PILOT / "review.json", {
        "schema_version": 1, "pilot_id": manifest["pilot_id"],
        "vocabulary_version": vocab["vocabulary_version"],
        "review_method": "Full-record batch classification; targeted independent boundary and repeated-family reviews; central reconciliation. This is not an accuracy estimate.",
        "tables": review,
    })
    with (PILOT / "review.csv").open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(table_rows[0]))
        writer.writeheader()
        writer.writerows(table_rows)

    lines = ["# Pilot assignments for review", "",
             "200 complete tables from all 102 volumes. These are provisional pilot assignments; published data and pages are unchanged.", "",
             "English titles are shown where supplied. Each identity links to the complete frozen input; the original title remains there. Text = the independent `text-tables` flag. Topics and tags are ordered by importance.", "",
             "See [findings](REPORT.md), [rules](../README.md), [definitions](../VOCABULARY.md), and [review decisions](resolutions.json).", "",
             "| Table / book | High-level topics | Detailed tags | Text | Rationale |",
             "|---|---|---|---|---|"]
    for row in table_rows:
        label = f"[{cell(row['title'])}]({row['input']}) — {cell(row['book'])} (`{row['key']}`)"
        lines.append("| " + " | ".join([label, cell(row["topics"]), cell(row["detailed_tags"]),
                                          row["text_table"], cell(row["rationale"])]) + " |")
    (PILOT / "REVIEW.md").write_text("\n".join(lines) + "\n")

    lines = ["# Pilot vocabulary", "", f"Version `{vocab['vocabulary_version']}`: {len(vocab['topics'])} high-level topics, {len(vocab['tags'])} detailed tags, plus `text-tables`.", "",
             "Every entry has inclusion/exclusion guidance and aliases in [vocabulary.json](vocabulary.json). Follow the [classification rules](README.md). Detailed tags are global; browsing associations do not limit their use.", "",
             "## High-level topics", "", "| ID | Definition |", "|---|---|"]
    for item in vocab["topics"]:
        lines.append(f"| `{item['id']}` | {cell(item['definition'])} |")
    lines += ["", "## Detailed tags", "", "| ID | Definition | Browsing associations |", "|---|---|---|"]
    for item in sorted(vocab["tags"], key=lambda d: d["id"]):
        lines.append(f"| `{item['id']}` | {cell(item['definition'])} | {', '.join(item['related_topics'])} |")
    (HERE / "VOCABULARY.md").write_text("\n".join(lines) + "\n")
    summary = {"assignments": len(final), "text_tables": sum(bool(a["flags"]) for a in final.values()),
               "topics_used": dict(Counter(t for a in final.values() for t in a["topics"])),
               "detailed_tags_used": len({t for a in final.values() for t in a["tags"]}),
               "centrally_reviewed": len(decisions["decisions"]),
               "independently_reviewed": len(independent),
               "changed_assignments": sum(r["classification_changed"] for r in review.values())}
    write(PILOT / "summary.json", summary)
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
