#!/usr/bin/env python3
"""Append 20 explicit boundary cases without changing the initial 180 inputs."""
from collections import Counter
import json
from pathlib import Path
import re
from prepare_pilot import digest, ROSTER

HERE = Path(__file__).resolve().parent
SITE = HERE.parent.parent
CASES = [
    ("manchoukuo-1942", "IMG_5508_1", "general historical chronology"),
    ("manchoukuo-1942", "IMG_5455_1", "calendar years without statistical observations"),
    ("japan-1942-43", "p1068_6", "explicit foreign-concession subject"),
    ("japan-manchoukuo-1934", "p2-0003_2", "ordinary meteorology within a colonial territory"),
    ("japan-1939-40", "p1088_1", "ordinary budget within a colonial territory"),
    ("japan-manchoukuo-1940", "p0115_6", "reported bandit-surrender classification"),
    ("japan-manchoukuo-1938", "p1-0965_1", "narcotic treatment rather than commodity production"),
    ("japan-1920-21", "p0720_3", "confirmed urban tram traffic"),
    ("taiwan-tokei-1925", "p0263_2", "track and trolley terminology requiring functional interpretation"),
    ("japan-1939-40", "p0696_1", "dedicated education expenditure"),
    ("korea-tokanfu-1939", "p0246_1", "general government account"),
    ("japan-1920-21", "p0456_1", "textual patent-law reference list"),
    ("japan-1910", "p0347_2", "patent medicines as a lexical false friend"),
    ("far-east-1941", "IMG_5400_1", "three commodities crossing two production sectors"),
    ("japan-1930", "p0513_2", "invisible trade"),
    ("japan-manchoukuo-1939", "p1-0258_2", "living-cost indices rather than family budgets"),
    ("far-east-1941", "IMG_5089_4", "sporting venues rather than sporting results"),
    ("far-east-1941", "IMG_5124_2", "multi-religion affiliation summary"),
    ("far-east-1941", "IMG_4895_1", "table evidence contrary to its saved contents placement"),
    ("japan-1942-43", "p1157_1", "reign dates together with substantive durations"),
]


def main():
    out = HERE / "pilot"
    manifest = json.loads((out / "manifest.json").read_text())
    if (out / "batches/pilot-d.json").exists():
        raise SystemExit("Supplement already prepared; existing inputs were left intact.")
    seen = {e["key"] for e in manifest["tables"]}
    vocab = json.loads((HERE / "vocabulary.json").read_text())
    manifest["initial_vocabulary"] = {"version": manifest["vocabulary_version"],
        "sha256": manifest["vocabulary_sha256"], "path": "vocabulary.initial.json"}
    manifest["vocabulary_version"] = vocab["vocabulary_version"]
    manifest["vocabulary_sha256"] = digest(vocab)
    items, cache = [], {}
    chars = 0
    for slug, id_, reason in CASES:
        key = slug + ":" + id_
        if key in seen:
            raise ValueError("Supplement duplicates a selected table: " + key)
        if slug not in cache:
            cache[slug] = {t["id"]: t for t in json.loads((SITE / "data" / (slug + ".json")).read_text())}
        table = cache[slug][id_]
        example = next(e for e in manifest["tables"] if e["source"] == "data/" + slug + ".json")
        book = json.loads((out / example["input"]).read_text())["book"]
        wrapper = {"key": key, "book": book, "table": table}
        filename = "input/" + key.replace(":", "--") + ".json"
        (out / filename).write_text(json.dumps(wrapper, ensure_ascii=False, indent=1) + "\n")
        text = json.dumps(table, ensure_ascii=False)
        headings = " ".join(str(x or "") for x in [table.get("title"), table.get("chapter"), (table.get("en") or {}).get("t")]
                            + [c for p in table.get("parts", []) for c in p.get("columns", [])])
        features = {"multipart": len(table.get("parts", [])) > 1,
                    "roster_candidate": bool(ROSTER.search(headings)), "marked_unreadable": "[?]" in text,
                    "japanese_original": bool(re.search(r"[㐀-鿿]", table.get("title", "")))}
        entry = {"key": key, "batch_id": "pilot-d", "input": filename,
                 "input_sha256": digest({"book": book, "table": table}), "source": example["source"],
                 "selection_reason": "targeted boundary: " + reason, "features": features, "chars": len(text)}
        manifest["tables"].append(entry)
        items.append({"key": key, "input": filename})
        chars += len(text)
        seen.add(key)
    for batch_path in (out / "batches").glob("*.json"):
        batch = json.loads(batch_path.read_text())
        batch["vocabulary_version"] = manifest["initial_vocabulary"]["version"]
        batch_path.write_text(json.dumps(batch, indent=2) + "\n")
    (out / "batches/pilot-d.json").write_text(json.dumps({"batch_id": "pilot-d", "vocabulary_version": vocab["vocabulary_version"], "items": items}, indent=2) + "\n")
    wrappers = [json.loads((out / e["input"]).read_text()) for e in manifest["tables"]]
    summary = manifest["summary"]
    summary["pilot_tables"] = len(manifest["tables"])
    summary["collections"] = dict(Counter(w["book"]["collection"] for w in wrappers))
    summary["features"] = dict(Counter(k for e in manifest["tables"] for k, value in e["features"].items() if value))
    summary["batch_chars"].append(chars)
    summary["batch_tables"].append(len(items))
    manifest["sampling_design"] = "180 all-book records plus 20 targeted boundary cases; a calibration sample, not a prevalence or accuracy estimate."
    (out / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
