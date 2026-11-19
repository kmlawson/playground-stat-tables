#!/usr/bin/env python3
"""Assist direct classification of only the remaining China records; no model API.

Profiles expose body structure and representative values to avoid rereading long
numeric series. Decisions are explicitly authored, never inferred by keyword rules.
Uncertain records can be printed in full with the full action.
"""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import re

from prepare_pilot import digest
from run_china_sonnet import row_issues

HERE = Path(__file__).resolve().parent
BASE = HERE / "runs/china-sonnet-2026-10-26"
OUT = HERE / "runs/china-direct-remainder-2026-10-26"


def read(path):
    return json.loads(path.read_text())


def write(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n")


def compact(value):
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"))


def records():
    manifest = read(BASE / "manifest.json")
    accepted = read(BASE / "assignments.json")["assignments"]
    result = []
    for batch in manifest["batches"]:
        for wrapper in read(BASE / "batches" / batch["id"] / "tables.json"):
            if wrapper["key"] not in accepted:
                result.append({**wrapper, "source_batch": batch["id"]})
    return result


def normalise_columns(parts):
    return [[re.sub(r"\b(?:18|19)\d{2}\b", "YEAR", str(x)) for x in p.get("columns", [])] for p in parts]


def profile(wrapper, index, headers):
    table = wrapper["table"]
    parts = table.get("parts", [])
    columns = normalise_columns(parts)
    signature = compact(columns)
    if signature not in headers:
        headers[signature] = "H" + str(len(headers))
    samples = []
    for part in parts:
        rows = part.get("rows", [])
        selected = sorted({i for i in [0, 1, len(rows) - 1] if 0 <= i < len(rows)})
        samples.append({"label": part.get("label"), "rows": len(rows),
                        "sample": [rows[i] for i in selected]})
    return {"i": index, "key": wrapper["key"], "T": table["title"],
            "H": headers[signature], "parts": samples,
            **({"caption": table["caption_extra"]} if table.get("caption_extra") else {}),
            **({"context": table["context"]} if table.get("context") else {}),
            **({"footnotes": table["footnotes"]} if table.get("footnotes") else {}),
            **({"en": table["en"]} if table.get("en") else {})}


def prepare():
    if OUT.exists():
        raise SystemExit("Remainder directory already exists")
    OUT.mkdir(parents=True)
    wrappers = records()
    assert len(wrappers) == 2016
    headers = {}
    profiles = [profile(w, i, headers) for i, w in enumerate(wrappers)]
    write(OUT / "headers.json", {id_: json.loads(sig) for sig, id_ in headers.items()})
    write(OUT / "profiles.json", profiles)
    write(OUT / "manifest.json", {
        "classifier": "assistant-direct", "vocabulary_version": read(BASE / "vocabulary.json")["vocabulary_version"],
        "source_run": str(BASE), "existing_assignments_sha256": hashlib.sha256((BASE / "assignments.json").read_bytes()).hexdigest(),
        "tables": [{"i": i, "key": w["key"], "batch": w["source_batch"],
                    "input_sha256": digest({"book": w["book"], "table": w["table"]})} for i, w in enumerate(wrappers)],
        "method": "Direct review of body profiles; explicit shared decisions for repeated structures; full-record reads for ambiguities. Complete original JSON is parsed and remains available. No external model calls or OCR.",
    })
    (OUT / "decisions.tsv").write_text("# index/range|topics (comma separated)|details (comma separated, empty allowed)|s or t|rationale\n")
    print(compact({"tables": len(wrappers), "header_signatures": len(headers),
                   "profile_chars": sum(len(compact(p)) for p in profiles), "header_chars": sum(len(s) for s in headers)}))


def show(start, count):
    ps = read(OUT / "profiles.json")[start:start + count]
    hs = read(OUT / "headers.json")
    seen = set()
    for p in ps:
        if p["H"] not in seen:
            print(p["H"], compact(hs[p["H"]])); seen.add(p["H"])
        print(compact(p))


def apply():
    profiles = read(OUT / "profiles.json")
    manifest = read(OUT / "manifest.json")
    vocab = read(BASE / "vocabulary.json")
    assignments, decisions = {}, {}
    for line in (OUT / "decisions.tsv").read_text().splitlines():
        if not line or line.startswith("#"):
            continue
        positions, topics, tags, mode, reason = line.split("|", 4)
        chosen = []
        for span in positions.split(","):
            bounds = span.split("-")
            chosen.extend(range(int(bounds[0]), int(bounds[-1]) + 1))
        for i in chosen:
            key = profiles[i]["key"]
            if key in assignments:
                raise ValueError("Duplicate decision: " + str(i))
            if mode not in ["s", "t"]:
                raise ValueError("Invalid text/statistical decision")
            tag_ids = tags.split(",") if tags else []
            assignments[key] = {"topics": topics.split(","), "tags": tag_ids,
                                "flags": ["text-tables"] if mode == "t" else [],
                                "rationale": reason,
                                "review_questions": [] if tag_ids else ["No fitting detailed tag assigned; retained for the user's later review."]}
            decisions[key] = {"index": i, "header_profile": profiles[i]["H"], "method": "assistant-direct", "input_sha256": manifest["tables"][i]["input_sha256"]}
    notes_path = OUT / "review-notes.json"
    if notes_path.exists():
        for key, questions in read(notes_path).items():
            if key not in assignments or not isinstance(questions, list) or not all(isinstance(q, str) and q.strip() for q in questions):
                raise ValueError("Invalid direct review notes: " + key)
            assignments[key]["review_questions"] = questions
    result = {"schema_version": 1, "classifier": "assistant-direct", "vocabulary_version": vocab["vocabulary_version"], "assignments": assignments}
    errors = row_issues(result, {"keys": list(assignments)}, vocab)
    if errors:
        raise ValueError(errors)
    write(OUT / "assignments.remainder.json", result)
    write(OUT / "decisions.json", decisions)
    print(compact({"saved": len(assignments), "remaining": 2016 - len(assignments), "without_details": sum(not r["tags"] for r in assignments.values())}))


def full(index):
    print(compact(records()[index]))


def lean(start, count):
    profiles = read(OUT / "profiles.json")[start:start + count]
    headers = read(OUT / "headers.json")
    for p in profiles:
        cols = list(dict.fromkeys(x for part in headers[p["H"]] for x in part))
        body = []
        for part in p["parts"]:
            # Retain categorical example content and a numerical example; long
            # duplicated numeric series remain in the complete frozen record.
            row = next((r for r in part["sample"] if sum(bool(c) for c in r) > 1), part["sample"][0] if part["sample"] else [])
            body.append([part["label"], part["rows"], row])
        print(compact({"i": p["i"], "key": p["key"], "T": p["T"], "C": cols, "R": body}))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=["prepare", "show", "lean", "apply", "full"])
    parser.add_argument("--start", type=int, default=0)
    parser.add_argument("--count", type=int, default=30)
    args = parser.parse_args()
    {"prepare": prepare, "show": lambda: show(args.start, args.count), "lean": lambda: lean(args.start, args.count), "apply": apply, "full": lambda: full(args.start)}[args.action]()
