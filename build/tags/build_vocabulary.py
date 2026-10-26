#!/usr/bin/env python3
"""Merge separately reviewed definition contributions into the pilot vocabulary."""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def main():
    vocab = json.loads((HERE / "vocabulary.seed.json").read_text())
    existing = {kind: {x["id"]: x for x in vocab[kind]} for kind in ("topics", "tags")}
    owners = {"topics": set(), "tags": set()}
    added = {"topics": [], "tags": []}
    contributions = []
    names = ["resources", "society", "institutions"]
    if (HERE / "definitions/calibration.json").exists():
        names.append("calibration")
        vocab["vocabulary_version"] = "1.0.2-pilot"
    approved_path = HERE / "definitions/china-uncovered-approved.json"
    if approved_path.exists():
        names.append("china-uncovered-approved")
    for name in names:
        path = HERE / "definitions" / (name + ".json")
        contribution = json.loads(path.read_text())
        contributions.append(str(path.relative_to(HERE)))
        for kind in ("topics", "tags"):
            for id_, definition in contribution[kind].items():
                if id_ in owners[kind] or id_ not in existing[kind]:
                    raise ValueError("Invalid or multiply owned definition: " + id_)
                owners[kind].add(id_)
                existing[kind][id_].update(definition)
            for entry in contribution.get("proposed_additions", {}).get(kind, []):
                id_ = entry["id"]
                if id_ in existing[kind]:
                    raise ValueError("Duplicate proposed ID: " + id_)
                existing[kind][id_] = {**entry, "origin": "pilot-completion-review"}
                added[kind].append(id_)
    for kind in ("topics", "tags"):
        original = {x["id"] for x in vocab[kind]}
        if owners[kind] != original:
            raise ValueError("Missing definitions: " + repr(original - owners[kind]))
        vocab[kind] = list(existing[kind].values())
    vocab["classification_rules"] = "README.md"
    vocab["definition_sources"] = contributions
    vocab["pilot_additions"] = added
    if approved_path.exists():
        approved = json.loads(approved_path.read_text())
        approved_ids = [x["id"] for x in approved["proposed_additions"]["tags"]]
        vocab["pilot_additions"]["tags"] = [x for x in added["tags"] if x not in approved_ids]
        vocab["approved_additions"] = {"topics": [], "tags": approved_ids}
        vocab["vocabulary_version"] = "1.2.0"
        vocab["status"] = "approved-vocabulary"
        vocab["limits"]["tags"]["min"] = 0
        vocab["classification_rules"] = "CLASSIFICATION.md"
    vocab["flags"][0].update({
        "includes": ["Textual rosters, event chronologies and reference lists with incidental dates or identifiers."],
        "excludes": ["Substantive quantitative observations, mixed statistical/text tables, and unreadable statistical tables."],
        "aliases": ["text only", "non-statistical tables"]})
    (HERE / "vocabulary.json").write_text(json.dumps(vocab, ensure_ascii=False, indent=2) + "\n")
    if approved_path.exists():
        lines = ["# Table tagging vocabulary", "",
                 f"Version `{vocab['vocabulary_version']}`: {len(vocab['topics'])} high-level topics, {len(vocab['tags'])} detailed tags, plus `text-tables`.", "",
                 "All 23 consolidated China-review proposals were approved by the user. Definitions and inclusion/exclusion boundaries are in [vocabulary.json](vocabulary.json). Follow [current classification rules](CLASSIFICATION.md).", "",
                 "## High-level topics", "", "| ID | Definition |", "| --- | --- |"]
        lines.extend(f"| `{x['id']}` | {x['definition']} |" for x in vocab["topics"])
        lines.extend(["", "## Detailed tags", "", "An asterisk marks the 23 newly approved tags.", "", "| ID | Definition | Related topics |", "| --- | --- | --- |"])
        for x in sorted(vocab["tags"], key=lambda x: x["id"]):
            marker = " *" if x["id"] in approved_ids else ""
            lines.append(f"| `{x['id']}`{marker} | {x['definition']} | {', '.join(x['related_topics'])} |")
        (HERE / "VOCABULARY.md").write_text("\n".join(lines) + "\n")
    print(json.dumps({"topics": len(vocab["topics"]), "tags": len(vocab["tags"]), "pilot_additions": added}, indent=2))


if __name__ == "__main__":
    main()
