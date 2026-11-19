#!/usr/bin/env python3
"""Validate vocabulary, frozen inputs, exact pilot coverage and assignment structure.

These checks establish structural completeness and input integrity, not semantic
classification accuracy. Semantic questions are resolved in the review record.
"""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import re
import unicodedata
from prepare_pilot import digest

HERE = Path(__file__).resolve().parent
SITE = HERE.parent.parent


def read(path):
    return json.loads(path.read_text())


def normalise(value):
    return re.sub(r"[\W_]+", " ", unicodedata.normalize("NFKC", value).casefold()).strip()


def vocabulary_checks(vocab):
    issues = []
    ids = {}
    for kind in ("topics", "tags", "flags"):
        items = vocab[kind]
        ids[kind] = {x["id"] for x in items}
        if len(ids[kind]) != len(items):
            issues.append("Duplicate vocabulary IDs in " + kind)
        aliases = {}
        for item in items:
            id_ = item["id"]
            if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", id_):
                issues.append("Malformed ID: " + id_)
            for field in ("label", "definition"):
                if not isinstance(item.get(field), str) or not item[field].strip():
                    issues.append(id_ + ": missing " + field)
            for field in ("includes", "excludes"):
                if not item.get(field) or not all(isinstance(x, str) and x.strip() for x in item[field]):
                    issues.append(id_ + ": missing/invalid " + field)
            if not isinstance(item.get("aliases"), list):
                issues.append(id_ + ": aliases must be a list")
            for alias in [id_, item["label"], *item.get("aliases", [])]:
                key = normalise(alias)
                if key in aliases and aliases[key] != id_:
                    issues.append(f"Ambiguous {kind} alias {alias!r}: {aliases[key]} / {id_}")
                aliases[key] = id_
    for item in vocab["tags"]:
        related = item.get("related_topics", [])
        if not related or len(set(related)) != len(related) or set(related) - ids["topics"]:
            issues.append(item["id"] + ": invalid related_topics")
    seed = read(HERE / "vocabulary.seed.json")
    for kind in ("topics", "tags"):
        if {x["id"] for x in seed[kind]} - ids[kind]:
            issues.append("Seed IDs removed from " + kind)
    if vocab["limits"] != {"topics": {"min": 1, "max": 2}, "tags": {"min": 1, "max": 3}}:
        issues.append("Assignment limits changed")
    if ids["flags"] != {"text-tables"}:
        issues.append("Unexpected flag vocabulary")
    return ids, issues


def manifest_checks(manifest, vocab):
    issues = []
    if manifest["vocabulary_sha256"] != digest(vocab):
        issues.append("Vocabulary changed after the manifest was frozen")
    rules_hash = manifest.get("classification_rules_sha256")
    if rules_hash and hashlib.sha256((HERE / "README.md").read_bytes()).hexdigest() != rules_hash:
        issues.append("Classification rules changed after final calibration")
    initial = manifest.get("initial_vocabulary")
    if initial and digest(read(HERE / "pilot" / initial["path"])) != initial["sha256"]:
        issues.append("Archived initial vocabulary differs from its frozen hash")
    for archive in manifest.get("archived_vocabularies", []):
        if digest(read(HERE / "pilot" / archive["path"])) != archive["sha256"]:
            issues.append("Archived vocabulary differs from its frozen hash: " + archive["path"])
    for filename, expected in manifest["source_files"].items():
        if hashlib.sha256((SITE / filename).read_bytes()).hexdigest() != expected:
            issues.append("Published source changed: " + filename)
    keys = [e["key"] for e in manifest["tables"]]
    if len(keys) != len(set(keys)) or len(keys) != manifest["summary"]["pilot_tables"]:
        issues.append("Manifest has duplicate identities or incorrect table count")
    for entry in manifest["tables"]:
        wrapper = read(HERE / "pilot" / entry["input"])
        if wrapper["key"] != entry["key"] or wrapper["key"] != wrapper["book"]["slug"] + ":" + wrapper["table"]["id"]:
            issues.append("Incorrect input identity: " + entry["key"])
        if digest({"book": wrapper["book"], "table": wrapper["table"]}) != entry["input_sha256"]:
            issues.append("Pilot input changed: " + entry["key"])
    batch_keys = []
    for path in sorted((HERE / "pilot/batches").glob("*.json")):
        batch = read(path)
        batch_keys.extend(x["key"] for x in batch["items"])
        if {x["key"] for x in batch["items"]} != {e["key"] for e in manifest["tables"] if e["batch_id"] == batch["batch_id"]}:
            issues.append("Batch differs from manifest: " + batch["batch_id"])
    if Counter(batch_keys) != Counter(keys):
        issues.append("Batches are not an exact partition of the manifest")
    return issues


def result_checks(result, expected, ids, vocab):
    issues = []
    if result.get("vocabulary_version") != vocab["vocabulary_version"]:
        issues.append("Result vocabulary version mismatch")
    assignments = result.get("assignments", {})
    if set(assignments) != set(expected):
        issues.append("Result coverage mismatch; missing=" + repr(sorted(set(expected) - set(assignments)))
                      + "; extra=" + repr(sorted(set(assignments) - set(expected))))
    for key, row in assignments.items():
        for kind, lo, hi in (("topics", 1, 2), ("tags", 1, 3), ("flags", 0, 1)):
            values = row.get(kind)
            if not isinstance(values, list) or not all(isinstance(x, str) for x in values):
                issues.append(key + ": " + kind + " must be a string list")
                continue
            if not lo <= len(values) <= hi or len(set(values)) != len(values) or set(values) - ids[kind]:
                issues.append(key + ": invalid " + kind + " " + repr(values))
        if not isinstance(row.get("rationale"), str) or not row["rationale"].strip():
            issues.append(key + ": rationale missing")
        if not isinstance(row.get("review_questions"), list) or not all(isinstance(x, str) for x in row["review_questions"]):
            issues.append(key + ": review_questions must be a string list")
    return issues


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--vocabulary-only", action="store_true")
    parser.add_argument("--results", action="store_true")
    args = parser.parse_args()
    # Validate the historical pilot against its frozen vocabulary, independently
    # of later approved vocabulary additions and partial-classification rules.
    frozen = HERE / "pilot/vocabulary.final.json"
    vocab = read(frozen if frozen.exists() else HERE / "vocabulary.json")
    ids, issues = vocabulary_checks(vocab)
    report = {"vocabulary_version": vocab["vocabulary_version"], "topics": len(ids["topics"]),
              "detailed_tags": len(ids["tags"])}
    if not args.vocabulary_only:
        manifest = read(HERE / "pilot/manifest.json")
        issues += manifest_checks(manifest, vocab)
        report.update(manifest["summary"])
        if args.results:
            path = HERE / "pilot/assignments.json"
            result = read(path)
            issues += result_checks(result, [e["key"] for e in manifest["tables"]], ids, vocab)
            values = list(result["assignments"].values())
            report.update({"assignments": len(values), "text_tables": sum("text-tables" in r.get("flags", []) for r in values),
                           "topics_used": dict(Counter(x for r in values for x in r.get("topics", []))),
                           "detailed_tags_used": len({x for r in values for x in r.get("tags", [])}),
                           "open_review_questions": sum(bool(r.get("review_questions")) for r in values)})
    report["issues"] = issues
    print(json.dumps(report, ensure_ascii=False, indent=2))
    if issues:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
