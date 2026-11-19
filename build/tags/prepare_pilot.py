#!/usr/bin/env python3
"""Prepare a reproducible, complete-record classification pilot; never edit site data."""
import argparse
import ast
from collections import Counter
import hashlib
import json
import os
from pathlib import Path
import random
import re

HERE = Path(__file__).resolve().parent
SITE = HERE.parent.parent
QUOTAS = {"japan": 40, "china": 38, "korea": 36, "taiwan": 24,
          "south-seas": 14, "manchuria": 22, "other": 6}
PATTERNS = {
    "geography": r"geograph|land area|location|地勢|位置|地形",
    "disasters": r"flood|disaster|storm|災害|水災|震災",
    "population": r"population|households|人口|戶口|戸口",
    "government": r"cabinet|government officials|官公吏|官吏|閣員",
    "informal-imperialism": r"extraterritorial|foreign concession|consular jurisdiction|租界",
    "colonial-rule": r"annexation|protectorate|governor.general|拓殖|植民|總督府",
    "indigenous-peoples": r"aborigin|indigenous|islanders|島民|蕃人|高砂族",
    "foreign-relations": r"treaties|treaty|diplomat|consular|外交|條約|領事",
    "military": r"army|navy|military|conscription|陸軍|海軍|國防|軍備",
    "economy": r"economic|reconstruction|price control|經濟|統制|產業獎勵",
    "finance": r"budget|bank|insurance|預金|銀行|歲入|歳入|公債",
    "trade": r"exports|imports|foreign trade|貿易|輸出|輸入|移出",
    "agriculture": r"rice|cultivat|arable|農業|農產|耕地|甘蔗",
    "forestry": r"forest|timber|afforest|林野|森林|林產|造林",
    "fisheries": r"fishery|fisheries|fishing|漁業|漁獲|水產",
    "mining": r"mineral|coal|gold mine|鑛業|鑛產|石炭|燐鑛",
    "manufacturing": r"manufactur|factor(?:y|ies)|製造|工產|工産|工場",
    "utilities": r"electric|waterworks|sewerage|電氣|電力|水道|土木",
    "transportation": r"railway|railroad|tramway|shipping|鐵道|軌道|船舶",
    "communications": r"postal|telegraph|telephone|郵便|電話|電信",
    "labour": r"labou?r|wages|賃銀|勞働|賃金|勞銀",
    "education": r"school|pupils|students|學校|學生|敎育|教育",
    "religion": r"religion|missions|church|寺院|神社|信徒|宗敎|宗教",
    "crime-and-justice": r"prison|court|crime|刑務|刑事|裁判|犯罪",
    "narcotics": r"opium|morphia|narcotic|阿片|痲藥",
    "health": r"disease|health|hospital|醫院|傳染病|衞生|衛生",
    "welfare": r"relief|charit|social work|救助|救恤|社會事業",
    "press": r"newspaper|periodical|publication|雜誌|新聞|出版",
    "culture": r"museum|theatre|fine arts|art exhibition|美術|博物館|古蹟",
    "sport": r"athletic|sports|baseball|swimming|體育|競技|野球|庭球",
    "science-and-technology": r"patent|research|weights.*measures|特許|研究|度量衡",
    "history": r"chronological table|chronology.*events|dynasties|年表",
}
COMPILED = {k: re.compile(v, re.I) for k, v in PATTERNS.items()}
ROSTER = re.compile(r"list of|directory|names of|personnel|index of|一覽|氏名|名簿|官制", re.I)


def digest(value):
    raw = json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    return hashlib.sha256(raw.encode()).hexdigest()


def collection(slug, fields):
    if "group" in fields:
        return ast.literal_eval(fields["group"])
    if slug.startswith(("manchuria-", "manchoukuo-", "manchukuo-")):
        return "manchuria"
    if slug.startswith("nanyo-"):
        return "south-seas"
    return slug.split("-")[0] if slug.split("-")[0] in QUOTAS else "other"


def load_corpus():
    tree = ast.parse((SITE / "build/build_site.py").read_text())
    books_node = next(n.value for n in tree.body if isinstance(n, ast.Assign)
                      and any(isinstance(x, ast.Name) and x.id == "BOOKS" for x in n.targets))
    records, sources = [], {}
    for node in books_node.elts:
        fields = {k.value: v for k, v in zip(node.keys, node.values) if isinstance(k, ast.Constant)}
        slug = ast.literal_eval(fields["slug"])
        path = SITE / "data" / (slug + ".json")
        if not path.exists():
            continue
        group = collection(slug, fields)
        book = {"slug": slug, "title": ast.literal_eval(fields["title"]), "collection": group}
        raw = path.read_bytes()
        sources[str(path.relative_to(SITE))] = hashlib.sha256(raw).hexdigest()
        for table in json.loads(raw):
            headings = " ".join(str(x or "") for x in
                [table.get("title"), table.get("chapter"), (table.get("en") or {}).get("t")]
                + [c for part in table.get("parts", []) for c in part.get("columns", [])])
            text = json.dumps(table, ensure_ascii=False)
            records.append({"key": slug + ":" + table["id"], "book": book, "table": table,
                            "chars": len(text), "themes": [k for k, rx in COMPILED.items() if rx.search(headings)],
                            "features": {"multipart": len(table.get("parts", [])) > 1,
                                         "roster_candidate": bool(ROSTER.search(headings)),
                                         "marked_unreadable": "[?]" in text,
                                         "japanese_original": bool(re.search(r"[㐀-鿿]", table.get("title", "")))},
                            "input_sha256": digest({"book": book, "table": table})})
    if len({r["key"] for r in records}) != len(records):
        raise ValueError("Duplicate published table identity")
    return records, sources


def select(records):
    rng = random.Random(20261026)
    ordered = list(records)
    rng.shuffle(ordered)
    by_book = {}
    for r in ordered:
        by_book.setdefault(r["book"]["slug"], []).append(r)
    selected, reasons = {}, {}
    selected_books = set()
    remaining_books = Counter(rs[0]["book"]["collection"] for rs in by_book.values())
    groups, themes = Counter(), Counter()

    def eligible(r):
        g = r["book"]["collection"]
        missing = remaining_books[g]
        already = r["book"]["slug"] in selected_books
        return r["key"] not in selected and groups[g] < QUOTAS[g] and (
            not already or QUOTAS[g] - groups[g] > missing)

    def add(r, why):
        selected[r["key"]] = r
        reasons[r["key"]] = why
        groups[r["book"]["collection"]] += 1
        themes.update(r["themes"])
        if r["book"]["slug"] not in selected_books:
            selected_books.add(r["book"]["slug"])
            remaining_books[r["book"]["collection"]] -= 1

    # One genuinely large input establishes that workers can classify complete records.
    add(max(ordered, key=lambda r: r["chars"]), "large complete-record edge case")
    for theme in PATTERNS:
        candidates = [r for r in ordered if eligible(r) and theme in r["themes"] and r["chars"] <= 18000]
        if candidates:
            add(min(candidates, key=lambda r: (groups[r["book"]["collection"]] / QUOTAS[r["book"]["collection"]],
                                              sum(themes[t] for t in r["themes"]), r["chars"] > 8000)),
                "theme sampling: " + theme)
    # Every published book is represented, with underrepresented themes preferred.
    for slug, rs in by_book.items():
        if slug in selected_books:
            continue
        candidates = [r for r in rs if eligible(r)]
        if not candidates:
            raise ValueError("Cannot meet per-book coverage: " + slug)
        add(max(candidates, key=lambda r: (sum(1 / (1 + themes[t]) for t in r["themes"]),
                                          r["chars"] <= 12000, r["features"]["roster_candidate"])),
            "all-book coverage")
    feature_counts = Counter(k for r in selected.values() for k, v in r["features"].items() if v)
    for g, target in QUOTAS.items():
        while groups[g] < target:
            candidates = [r for r in ordered if r["book"]["collection"] == g and eligible(r) and r["chars"] <= 18000]
            def score(r):
                return (sum(1 / (1 + themes[t]) for t in r["themes"])
                        + sum(1.5 / (1 + feature_counts[k]) for k, v in r["features"].items() if v))
            r = max(candidates, key=score)
            add(r, "collection balance and content diversity")
            feature_counts.update(k for k, v in r["features"].items() if v)
    return list(selected.values()), reasons


def main():
    try:
        os.nice(15)
    except OSError:
        pass  # Some managed execution environments forbid changing niceness.
    ap = argparse.ArgumentParser()
    ap.add_argument("--preview", action="store_true")
    args = ap.parse_args()
    records, sources = load_corpus()
    chosen, reasons = select(records)
    bins = [[], [], []]
    lengths = [0, 0, 0]
    for r in sorted(chosen, key=lambda r: r["chars"], reverse=True):
        i = min((i for i in range(3) if len(bins[i]) < 60), key=lambda i: lengths[i])
        bins[i].append(r)
        lengths[i] += r["chars"]
    summary = {"corpus_tables": len(records), "corpus_books": len(sources), "pilot_tables": len(chosen),
               "pilot_books": len({r["book"]["slug"] for r in chosen}),
               "collections": dict(Counter(r["book"]["collection"] for r in chosen)),
               "features": dict(Counter(k for r in chosen for k, v in r["features"].items() if v)),
               "batch_chars": lengths, "batch_tables": [len(b) for b in bins]}
    print(json.dumps(summary, indent=2))
    if args.preview:
        return
    vocab_path = HERE / "vocabulary.json"
    vocab = json.loads(vocab_path.read_text())
    out = HERE / "pilot"
    for d in ("input", "batches", "results"):
        (out / d).mkdir(parents=True, exist_ok=True)
    entries = []
    for batch_i, batch in enumerate(bins):
        batch_id = "pilot-" + "abc"[batch_i]
        items = []
        for r in sorted(batch, key=lambda r: r["key"]):
            filename = r["key"].replace(":", "--") + ".json"
            wrapper = {"key": r["key"], "book": r["book"], "table": r["table"]}
            (out / "input" / filename).write_text(json.dumps(wrapper, ensure_ascii=False, indent=1) + "\n")
            entry = {"key": r["key"], "batch_id": batch_id, "input": "input/" + filename,
                     "input_sha256": r["input_sha256"], "source": "data/" + r["book"]["slug"] + ".json",
                     "selection_reason": reasons[r["key"]], "features": r["features"], "chars": r["chars"]}
            entries.append(entry)
            items.append({"key": r["key"], "input": entry["input"]})
        (out / "batches" / (batch_id + ".json")).write_text(json.dumps({"batch_id": batch_id, "items": items}, indent=2) + "\n")
    manifest = {"schema_version": 1, "pilot_id": "calibration-001", "sampling_seed": 20261026,
                "vocabulary_version": vocab["vocabulary_version"], "vocabulary_sha256": digest(vocab),
                "summary": summary, "source_files": sources, "tables": entries}
    (out / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")


if __name__ == "__main__":
    main()
