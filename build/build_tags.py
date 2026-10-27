#!/usr/bin/env python3
"""Publish controlled tags without modifying transcription JSON or chart rules."""
import ast
from collections import Counter, defaultdict
import hashlib
import html
import json
from pathlib import Path
import re

HERE = Path(__file__).resolve().parent
SITE = HERE.parent
TAGS = HERE / "tags"
PUBLISHED = TAGS / "published"
COLLECTIONS = {"japan": "Japan", "china": "China", "korea": "Korea", "taiwan": "Taiwan", "manchuria": "Manchuria", "south-seas": "South Seas", "other": "Other"}
COLORS = ["#4e79a7", "#a64d50", "#43814b", "#8260a3", "#9a6c27", "#318188", "#a34d7e", "#6b6b30", "#625e9d", "#287254", "#964b32", "#306a91", "#8c477c", "#5a7250", "#865f43", "#645e69", "#91562c"]
RUNS = [("china-direct-remainder-2026-10-26/assignments.china.json", "complete-record"),
        ("korea-taiwan-direct-2026-10-26/assignments.korea-taiwan.json", "complete-record"),
        ("japan-manchuria-south-seas-metadata-2026-10-26/assignments.japan-manchuria-south-seas.json", "metadata-first-pass")]


def read(path):
    return json.loads(path.read_text())


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, separators=(",", ":")) + "\n")


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def inline(value):
    return json.dumps(value, ensure_ascii=False, separators=(",", ":")).replace("<", "\\u003c")


def prepare_assignments():
    """One stable, versioned source for the website, independent of raw run logs."""
    pilot = read(TAGS / "pilot/assignments.json")["assignments"]
    assignments = {key: {field: row[field] for field in ("topics", "tags", "flags")} | {"stage": "reviewed-pilot", "flag_status": "reviewed"} for key, row in pilot.items()}
    sources = []
    for filename, stage in RUNS:
        path = TAGS / "runs" / filename
        source = read(path)
        provenance_path = path.parent / "provenance.json"
        provenance = read(provenance_path).get("tables", {}) if provenance_path.exists() else {}
        for key, row in source["assignments"].items():
            a = {field: row[field] for field in ("topics", "tags", "flags")}
            flag_status = provenance.get(key, {}).get("flag_status", "reviewed")
            assignments[key] = a | {"stage": "reviewed-pilot" if key in pilot else stage, "flag_status": flag_status}
        sources.append({"file": str(path.relative_to(TAGS)), "sha256": sha(path), "tables": len(source["assignments"])})
    # Preserve the existing Far East topic pages while that collection awaits
    # controlled classification. Never fill a deliberately blank first-pass field.
    import build_site as site
    for key, pairs in site.TOPIC_TAGS.items():
        if key in assignments:
            continue
        topics = list(dict.fromkeys("crime-and-justice" if top == "crime" else top for top, _ in pairs))
        if topics:
            assignments[key] = {"topics": topics[:2], "tags": [], "flags": [], "stage": "legacy-topic-selection", "flag_status": "unknown-needs-contents"}
    PUBLISHED.mkdir(parents=True, exist_ok=True)
    write(PUBLISHED / "assignments.json", {"schema_version": 1, "vocabulary_version": read(TAGS / "vocabulary.json")["vocabulary_version"], "assignments": assignments})
    write(PUBLISHED / "sources.json", {"sources": sources, "pilot_sha256": sha(TAGS / "pilot/assignments.json"), "note": "Canonical website assignments exported from saved classification runs. Full historical run logs remain local; no CLI databases or credentials are published."})
    # Keep the exact 7,662-record cohort fixed even after subsequent reviews.
    source = TAGS / "runs/japan-manchuria-south-seas-metadata-2026-10-26/no-detailed-tags.json"
    cohort = read(source)
    assert cohort["count"] == len(cohort["tables"]) == 7662
    write(TAGS / "reviews/deferred-detailed-tags-2026-10-26.json", {"count": 7662, "status": "deferred-for-closer-evaluation", "source": str(source.relative_to(TAGS)), "source_sha256": sha(source), "tables": cohort["tables"]})
    (TAGS / "reviews/DEFERRED.md").write_text("# Deferred detailed-tag review\n\nThe fixed list in [deferred-detailed-tags-2026-10-26.json](deferred-detailed-tags-2026-10-26.json) records all **7,662** tables left without detailed tags after the metadata first pass. It preserves table keys, titles/descriptions, book identity and prior high-level assignments. This cohort is retained for later closer evaluation; high-level review does not remove entries from it.\n")
    print(f"Canonical assignments: {len(assignments):,}; deferred detailed-tag cohort: 7,662")


def load_assignments():
    path = PUBLISHED / "assignments.json"
    rows = read(path)["assignments"] if path.exists() else {}
    overrides = PUBLISHED / "overrides.json"
    if overrides.exists():
        for key, fields in read(overrides)["assignments"].items():
            assert key in rows, key
            rows[key] = rows[key] | fields
    return rows


def book_tags(slug, assignments=None):
    rows = assignments if assignments is not None else load_assignments()
    prefix = slug + ":"
    return {key[len(prefix):]: row for key, row in rows.items() if key.startswith(prefix)}


def shell(title, body, data):
    return '<!DOCTYPE html>\n<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">' + f'<title>{html.escape(title)}</title><link rel="stylesheet" href="../tags.css"></head><body class="tag-browser"><header class="band"><div><nav class="navigation"><a href="../index.html">← All books</a><a href="index.html">All topics and tags</a></nav><h1>{html.escape(title)}</h1></div></header><main>' + body + '</main><script id="tag-browser-data" type="application/json">' + inline(data) + '</script><script src="../data/tags/vocabulary.js"></script><script src="../tags.js"></script></body></html>\n'


def page_body(entry, scope, region, counts):
    description = html.escape(entry["definition"])
    nav = '<nav class="navigation">' + ' · '.join(f'<a href="{r}-{scope}.html">{name}</a>' for r, name in COLLECTIONS.items()) + '</nav>' if scope else ""
    return f'<p class="lede">{description}</p>{nav}<p class="status">{counts:,} tagged tables. Tagging is in progress; tables retain the original books’ categories, units and historical wording.</p>' + '''
<div class="controls"><label class="search-control">Search this selection<input type="search" id="query" placeholder="Titles, chapters, books or tags"></label><label>Collection<select id="collection"><option value="">All collections</option></select></label><label>Book<select id="book"><option value="">All books</option></select></label><label>Detailed tag<select id="detail"><option value="">All detailed tags</option></select></label><label>Group tables by<select id="group"><option value="book">Book</option><option value="year">Edition year</option></select></label><button id="reset" type="button">Reset filters</button></div>
<h2>Coverage at a glance</h2><div class="coverage-key" id="coverage-key" aria-label="Book series colour key"></div><div class="coverage" id="coverage"></div><p class="coverage-note" id="grid-note"></p><label><span><input type="checkbox" id="all-grid-tags"> Show every detailed tag in the grid</span></label>
<h2>Explore related tags</h2><div class="tag-list" id="related-tags"></div><details id="related-more"><summary>More related tags</summary><div class="tag-list" id="related-extra"></div></details>
<h2>Tables <span class="count" id="result-count" aria-live="polite"></span><button id="clear-pick" class="clear-filter" type="button" hidden>Clear grid selection</button></h2><div id="results"></div><button type="button" id="more" class="load-more" hidden>Show more</button><noscript><p>Enable JavaScript to filter and explore the table list. The original table data are available from each book.</p></noscript>'''


def build_tag_pages(pages):
    import build_site as site
    assignments, vocabulary = load_assignments(), read(TAGS / "vocabulary.json")
    labels = {kind: {entry["id"]: {key: entry[key] for key in ("label", "definition")} for entry in vocabulary[kind]} for kind in ("topics", "tags", "flags")}
    target = SITE / "data/tags"
    write(target / "vocabulary.json", vocabulary)
    (target / "vocabulary.js").write_text("window.TagVocabulary=" + inline(labels) + ";\n")
    topics_dir = SITE / "topics"
    topics_dir.mkdir(exist_ok=True)
    books, items, seen = [], [], set()
    series_names = {}
    for b, tables, _, _ in pages:
        group = site.group_of(b)
        series = next((name for _, (_, entries) in site.TOPIC_REGIONS.items() for _, name, rx in entries if re.match(rx, b["slug"])), COLLECTIONS[group])
        if series not in series_names:
            series_names[series] = COLORS[len(series_names) % len(COLORS)]
        books.append({"s": b["slug"], "title": b["title"], "y": site.years_of(b)[0] or 0, "ed": site.edition(b), "g": group, "series": series, "color": series_names[series]})
        rows = book_tags(b["slug"], assignments)
        write(target / "books" / (b["slug"] + ".json"), rows)
        for t in tables:
            key = b["slug"] + ":" + t["id"]
            seen.add(key)
            row = assignments.get(key, {"topics": [], "tags": [], "flags": []})
            for kind in labels:
                assert set(row[kind]) <= labels[kind].keys(), (key, kind)
            items.append({"s": b["slug"], "id": t["id"], "t": (f"Table {t['table_no']}. " if t.get("table_no") else "") + (t.get("title") or ""), "e": (t.get("en") or {}).get("t", ""), "c": t.get("chapter") or "", "pp": ", ".join(t.get("printed_pages") or []), **{kind: row[kind] for kind in labels}})
    assert assignments.keys() <= seen, f"Orphaned classifications: {assignments.keys() - seen}"
    books.sort(key=lambda b: (b["y"], b["s"]))
    groups = {b["s"]: b["g"] for b in books}
    counts, facet_counts, tag_topics = Counter(), Counter(), defaultdict(set)
    indexed = {kind: defaultdict(list) for kind in labels}
    for item in items:
        for kind in indexed:
            for identifier in item[kind]:
                indexed[kind][identifier].append(item)
                facet_counts[(kind, identifier)] += 1
                if kind == "topics":
                    counts[(groups[item["s"]], identifier)] += 1
        for identifier in item["tags"]:
            tag_topics[identifier].update(item["topics"])
    for entry in vocabulary["tags"]:
        tag_topics[entry["id"]].update(entry["related_topics"])
    write(target / "summary.json", {"tables": len(items), "classified_tables": len(assignments), "topics": len(labels["topics"]), "detailed_tags": len(labels["tags"]), "with_topics": sum(bool(x["topics"]) for x in items), "with_details": sum(bool(x["tags"]) for x in items)})
    for kind, entries in labels.items():
        for identifier, entry in entries.items():
            selected = indexed[kind][identifier]
            prefix = "topic" if kind == "topics" else "tag" if kind == "tags" else "flag"
            filename = f"{prefix}-{identifier}.html"
            common = {"mode": "facet", "collections": COLLECTIONS, "scope": {"kind": kind, "id": identifier}, "books": books, "items": selected}
            (topics_dir / filename).write_text(shell(entry["label"].capitalize() + " tables", page_body(entry, identifier if kind == "topics" else None, None, len(selected)), common))
            if kind == "topics":
                for region, region_name in COLLECTIONS.items():
                    local = [item for item in selected if groups[item["s"]] == region]
                    doc = shell(f"{region_name}: {entry['label']}", page_body(entry, identifier, region, len(local)), common | {"region": region, "items": local})
                    (topics_dir / f"{region}-{identifier}.html").write_text(doc)
                    if identifier == "crime-and-justice":
                        (topics_dir / f"{region}-crime.html").write_text(doc)
    rows = []
    for i, entry in enumerate(vocabulary["topics"]):
        identifier = entry["id"]
        cells = []
        for region, name in COLLECTIONS.items():
            n = counts[(region, identifier)]
            color = COLORS[list(COLLECTIONS).index(region)]
            cells.append(f'<td><a style="background:{color};color:#fff;opacity:{0.55 + min(n, 300) / 300 * 0.45:.2f}" href="{region}-{identifier}.html" aria-label="{html.escape(name)}: {html.escape(entry["label"])} — {n} tables">{n:,}</a></td>' if n else '<td class="zero">·</td>')
        rows.append(f'<tr><th><a href="topic-{identifier}.html">{html.escape(entry["label"].capitalize())}</a></th>' + "".join(cells) + "</tr>")
    body = f'<p class="lede">Explore {len(items):,} tables through {len(labels["topics"])} high-level topics and {len(labels["tags"])} detailed tags. Select a topic or collection in the coverage grid, then browse tables by book or edition year. Tagging is in progress.</p><h2>Topic coverage across collections</h2><div class="coverage"><table class="even"><thead><tr><th>High-level topic</th>' + ''.join(f'<th>{name}</th>' for name in COLLECTIONS.values()) + '</tr></thead><tbody>' + ''.join(rows) + '</tbody></table></div><p class="coverage-note">Numbers count tables with an assigned high-level topic. A table can appear under two topics. Empty cells indicate no assigned match; they do not establish that the subject is absent from a book.</p><p>' + '<a class="tag-chip flag" href="flag-text-tables.html">Text tables</a> — rosters and reference tables identified as containing text rather than statistical observations.</p><h2>Explore detailed tags <span id="tag-count" class="count"></span></h2><div class="controls"><label class="search-control">Find a detailed tag<input id="tag-query" type="search" placeholder="Search names and definitions"></label><label>Related high-level topic<select id="topic-filter"><option value="">All topics</option></select></label></div><div id="tag-cards" class="tag-cards"></div>'
    key_html = '<div class="coverage-key" aria-label="Collection colour key"><b>Collections:</b>' + ''.join(f'<span><i style="background:{COLORS[i]}"></i>{html.escape(name)}</span>' for i, name in enumerate(COLLECTIONS.values())) + '</div>'
    body = body.replace('<div class="coverage">', key_html + '<div class="coverage">', 1)
    (topics_dir / "index.html").write_text(shell("Tables by topic and tag", body, {"mode": "index", "books": books, "tagCounts": {identifier: facet_counts[("tags", identifier)] for identifier in labels["tags"]}, "tagTopics": {identifier: sorted(topics) for identifier, topics in tag_topics.items()}}))
    print(f"Tag pages: {len(labels['topics'])} topics, {len(labels['tags'])} details, {len(items):,} tables; original data unchanged")


def patch_book_pages(pages):
    assignments = load_assignments()
    for b, _, _, _ in pages:
        path = SITE / "book" / b["slug"] / "index.html"
        doc = path.read_text()
        marker = '<link rel="stylesheet" href="../../tags.css">'
        assets = marker + '<script src="../../data/tags/vocabulary.js"></script><script src="../../tags.js"></script>'
        if marker not in doc:
            doc = doc.replace("</head>", assets + "</head>", 1)
        data = "const TABLE_TAG_DATA=" + inline(book_tags(b["slug"], assignments)) + ";\n"
        if "const TABLE_TAG_DATA=" in doc:
            doc = re.sub(r"const TABLE_TAG_DATA=.*?;\n", lambda _: data, doc, count=1)
        else:
            doc = doc.replace("const T=", data + "const T=", 1)
        target = '</h2>${t.en?'
        replacement = '</h2>${!other?TableTags.render(TABLE_TAG_DATA[t.id],"../../"):""}${t.en?'
        if replacement not in doc:
            assert target in doc, b["slug"]
            doc = doc.replace(target, replacement, 1)
        list_target = '</small></a>`;n++'
        list_replacement = '</small></a>${TableTags.render(TABLE_TAG_DATA[t.id],"../../",{pending:false})}`;n++'
        if list_replacement not in doc:
            assert list_target in doc, b["slug"]
            doc = doc.replace(list_target, list_replacement, 1)
        path.write_text(doc)


def committed_pages():
    import build_site as site
    pages = []
    for b in site.BOOKS:
        path = SITE / "data" / (b["slug"] + ".json")
        if path.exists():
            tables = read(path)
            pages.append((b, tables, len(tables), 0))
    return pages


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--prepare", action="store_true")
    args = parser.parse_args()
    if args.prepare:
        prepare_assignments()
    pages = committed_pages()
    build_tag_pages(pages)
    patch_book_pages(pages)
