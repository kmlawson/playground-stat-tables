#!/usr/bin/env python3
"""Conservative metadata-only first pass; no body fields reach classification."""
import argparse
import ast
from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path
import re
import unicodedata
from metadata_subject_rules import RULES

HERE = Path(__file__).resolve().parent
SITE = HERE.parent.parent
OUT = HERE / "runs/japan-manchuria-south-seas-metadata-2026-10-26"
GROUPS = ("japan", "manchuria", "south-seas")
FIELDS = ("title", "title_en", "description_en", "chapter", "chapter_raw", "caption", "description")


def read(path):
    return json.loads(path.read_text())


def write(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n")


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def digest(value):
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def norm(text):
    text = unicodedata.normalize("NFKC", text).lower()
    return re.sub(r"\s+", " ", text).strip()


def corpus():
    tree = ast.parse((SITE / "build/build_site.py").read_text())
    books_node = next(n.value for n in tree.body if isinstance(n, ast.Assign)
                      and any(isinstance(x, ast.Name) and x.id == "BOOKS" for x in n.targets))
    records, sources, books, input_hashes = [], {}, [], {}
    for node in books_node.elts:
        fields = {k.value: v for k, v in zip(node.keys, node.values) if isinstance(k, ast.Constant)}
        slug = ast.literal_eval(fields["slug"])
        group = ast.literal_eval(fields["group"]) if "group" in fields else (
            "manchuria" if slug.startswith(("manchuria-", "manchoukuo-", "manchukuo-")) else
            "south-seas" if slug.startswith("nanyo-") else slug.split("-")[0])
        if group not in GROUPS:
            continue
        path = SITE / "data" / f"{slug}.json"
        tables = read(path)
        sources[str(path.relative_to(SITE))] = sha(path)
        book = {"slug": slug, "title": ast.literal_eval(fields["title"]), "collection": group}
        books.append({**book, "tables": len(tables)})
        for table in tables:
            en = table.get("en") or {}
            metadata = dict(zip(FIELDS, [table.get("title") or "", en.get("t") or "", en.get("d") or "",
                                        table.get("chapter") or "", table.get("chapter_raw") or "",
                                        table.get("caption_extra") or "", table.get("context") or ""]))
            key = slug + ":" + table["id"]
            records.append({"key": key, "book": book, "metadata": metadata})
            # Integrity only: no body fields are selected for review/classification.
            input_hashes[key] = digest({"book": book, "table": table})
    assert len(records) == len({x["key"] for x in records})
    return records, sources, books, input_hashes


def prepare():
    if OUT.exists():
        raise ValueError("Run already prepared; preserve its frozen metadata")
    OUT.mkdir(parents=True)
    records, sources, books, input_hashes = corpus()
    pilot = read(HERE / "pilot/assignments.json")
    pilot_manifest = {x["key"]: x for x in read(HERE / "pilot/manifest.json")["tables"]}
    preserved = {}
    for record in records:
        key = record["key"]
        if key in pilot["assignments"]:
            assert input_hashes[key] == pilot_manifest[key]["input_sha256"], key
            preserved[key] = pilot["assignments"][key]
    write(OUT / "metadata.json", records)
    write(OUT / "preserved-pilot.json", {"pilot_id": pilot["pilot_id"], "assignments": preserved})
    (OUT / "vocabulary.json").write_bytes((HERE / "vocabulary.json").read_bytes())
    (OUT / "rules.md").write_bytes((HERE / "CLASSIFICATION.md").read_bytes())
    write(OUT / "manifest.json", {"schema_version": 1, "method": "metadata-only-first-pass",
          "allowed_metadata_fields": list(FIELDS), "excluded_content": ["parts", "columns", "rows", "footnotes", "transcriber_notes"],
          "tables": len(records), "books": books, "source_files": sources,
          "source_input_sha256": input_hashes, "metadata_sha256": sha(OUT / "metadata.json"),
          "vocabulary_sha256": sha(OUT / "vocabulary.json"), "rules_sha256": sha(OUT / "rules.md"),
          "preserved_pilot_sha256": sha(OUT / "preserved-pilot.json"), "preserved_tables": len(preserved)})
    groups = defaultdict(list)
    for i, r in enumerate(records):
        title = r["metadata"]["title_en"] or r["metadata"]["title"]
        groups[re.sub(r"\d+", "#", norm(title))].append(i)
    write(OUT / "title-groups.json", [{"title": title, "count": len(indices), "indices": indices} for title, indices in sorted(groups.items(), key=lambda x: -len(x[1]))])
    print(json.dumps({"tables": len(records), "books": len(books), "preserved": len(preserved), "title_groups": len(groups),
                      "collections": dict(Counter(x["book"]["collection"] for x in records))}))


CHAPTERS = [
    ("education", r"education|敎育|教育"), ("religion", r"religion|宗敎|宗教"),
    ("finance", r"financ|banking|banks|insurance|money market|財政|金融"),
    ("trade", r"foreign trade|home trade|commerce|貿易|商業| — trade$|^trade$"),
    ("agriculture", r"agricultur|農業|農產|農産"), ("forestry", r"forestry|森林|林業"),
    ("fisheries", r"fisher(?:y|ies)|水產|水産|漁業"), ("mining", r"mines|mining|鑛業|鉱業"),
    ("manufacturing", r"manufacturing|textile industry|machinery and engineering|miscellaneous industries|工業"),
    ("transportation", r"railway|shipping|mercantile marine|transportation|海運|鐵道|鉄道|交通"),
    ("communications", r"communications|post,? telegraph|郵便|通信"),
    ("military", r"army|navy|national defen[cs]e|軍事|國防|国防"),
    ("population", r"population|人口|戶口|戸口"), ("geography", r"geography|geographical|土地及氣象"),
    ("crime-and-justice", r"justice|judicature|prisons|司法|行刑"),
    ("health", r"medicine|sanitation|public health|衛生|衞生"),
    ("government", r"government|politics|imperial court|行政|政治"),
    ("welfare", r"charity|relief|social problems|social work|社會事業"),
    ("labour", r"labou?r|勞働|労働"), ("sport", r"sports|athletics|體育|体育"),
    ("culture", r"arts and crafts|fine arts|美術"), ("foreign-relations", r"diplomacy|foreign relations|外交"),
    ("disasters", r"earthquakes|volcanoes|disasters|震災|災害"),
]
CHAPTERS = [(topic, re.compile(expression, re.I)) for topic, expression in CHAPTERS]
COMMODITIES = {identifier for identifier, domain, _ in RULES if domain == "commodity"}
GENERIC = re.compile(r"^(?:\[?statistics\]?|production|returns|summary|expenditures?|revenue(?: and expenditure)?|assets|liabilities|profit and loss account|(?:table\s*)?[\divx. ()–—-]+)$", re.I)
TRADE_FLOW = {"imports", "exports", "re-exports", "transit-trade", "intra-imperial-trade", "foreign-trade"}
GENERAL_DETAIL = {
    "schools-and-pupils": {"primary-education", "secondary-education", "higher-education", "vocational-education", "teacher-training", "teachers", "kindergartens", "special-education", "school-boarding", "school-curricula", "education-finance", "language-education", "students-abroad", "mission-schools"},
    "taxation": {"land-tax", "salt-tax", "head-tax"},
    "savings-and-loans": {"agricultural-credit", "mutual-credit", "pawnshops"},
    "religious-institutions": {"buddhism", "shinto", "christianity", "islam", "taoism", "confucianism", "tenrikyo"},
    "offences-and-convictions": {"summary-justice", "juvenile-justice", "political-policing"},
    "diseases": {"epidemics", "malaria", "leprosy", "mental-health", "veterinary-health"},
    "fishing": {"aquaculture", "whaling", "fishing-rights-and-licences"},
    "electricity": {"hydroelectricity"},
    "prisons": {"prison-labour", "prisoner-aftercare"},
    "births-and-deaths": {"infant-mortality", "suicide"},
    "postal-services": {"postal-remittances"},
    "foreign-trade": TRADE_FLOW - {"foreign-trade"},
    "cereals": {"rice", "wheat", "barley"},
    "shipping": {"inland-navigation", "navy", "shipbuilding"},
    "construction": {"railways", "roads-and-bridges", "shipbuilding", "water-and-sewerage", "flood-control", "river-conservancy", "hydroelectricity", "land-reclamation"},
}


def find_hits(text, source):
    return {identifier: {"domain": domain, "field": source, "matched": match.group(0)}
            for identifier, domain, expression in RULES if (match := expression.search(text))}


def classify(metadata):
    assert set(metadata) == set(FIELDS), "Only whitelisted metadata may enter classification"
    title_field = "title_en" if metadata["title_en"] else "title"
    title = norm(metadata[title_field])
    chapter = norm(metadata["chapter"])
    description = norm(metadata["description_en"] or metadata["description"])
    combined = title + " " + description[:300] + " " + norm(metadata["caption"])
    hits = find_hits(title, title_field)
    notes = []
    if not hits and description and (GENERIC.fullmatch(title.strip("[]")) or re.match(r"(?:gives|shows|lists|reports|records|compares|the table (?:gives|shows|lists|records))\b", description)):
        prefix = re.split(r"[.;]|\b(?:with|broken down|due to|following|to show|in order|illustrating|supporting)\b", description, maxsplit=1)[0]
        if len(prefix) <= 300 and not re.search(r"introduc|background|for example|other than|except|rather than|does not|not establish", prefix):
            proposed = find_hits(prefix, "description_en" if metadata["description_en"] else "description")
            chapter_domains = {topic for topic, expression in CHAPTERS if expression.search(chapter)}
            if GENERIC.fullmatch(title.strip("[]")):
                hits = proposed
            elif len(chapter_domains) == 1:
                # Unknown technical titles do not license tagging incidental
                # places, staff, causes or materials mentioned in a description.
                hits = {key: value for key, value in proposed.items() if value["domain"] in chapter_domains}
    if "diplomatic-service" in hits:
        for identifier in ("ports", "telephone", "postal-services"):
            if identifier in hits and hits[identifier]["field"].startswith("description"):
                hits.pop(identifier)
    # A correction is justified only by the title, not neighbouring rows or notes.
    if re.search(r"\b(?:tariffs?|customs duties|import duties|export duties)\b", title):
        hits.pop("imports", None); hits.pop("exports", None)
    if "public-budgets" in hits:
        # Budget totals may mention army/education etc.; retain dedicated finance
        # only when that sector is actually named by the title's own expression.
        hits.pop("securities-and-investment", None)
        if "companies" in hits and not re.search(r"\b(?:public|government|national|municipal|state)\b", title):
            hits.pop("public-budgets", None)
    if "taxation" in hits or set(hits) & {"land-tax", "salt-tax", "head-tax"}:
        for identifier in COMMODITIES:
            hits.pop(identifier, None)
    if "public-debt" in hits or "foreign-loans" in hits:
        hits.pop("savings-and-loans", None)
    if "prices" in hits:
        hits.pop("markets-and-exchanges", None)
    if "cost-of-living" in hits or "price-controls" in hits:
        hits.pop("prices", None)
    if "public-property" in hits:
        hits.pop("real-estate", None)
    if "household-budgets" in hits or "domestic-service" in hits:
        hits.pop("households", None)
        hits.pop("public-budgets", None)
    if "libraries" in hits:
        hits.pop("books", None)
    if "professional-associations" in hits:
        hits.pop("medical-services", None); hits.pop("business-associations", None)
    if "rayon" in hits and "artificial silk" in title:
        hits.pop("silk", None)
    if "rice-milling" in hits:
        hits.pop("rice", None)
    if "silk" in hits or "cotton" in hits or "wool" in hits or "rayon" in hits:
        hits.pop("textiles", None)
    if "phosphate-rock" in hits and re.search(r"\bphosphate (?:mining )?undertaking\b", title):
        hits.pop("companies", None)
    if "ports" in hits and (set(hits) & TRADE_FLOW):
        hits.pop("ports", None)
    if "treaty-ports" in hits:
        hits.pop("ports", None)
    if "forest-area" in hits or "arable-land" in hits:
        hits.pop("land-area", None)
    if "shipping" in hits or "fishing" in hits:
        hits.pop("iron-and-steel", None)
    if "labour-disputes" in hits:
        hits.pop("newspapers", None)
    if "trams" in hits and not re.search(r"(?<!street )\brailways?\b|light rail", title):
        hits.pop("railways", None)
    if "companies" in hits and set(hits) & {"railways", "banking", "insurance-and-pensions", "shipping", "electricity", "telephone", "telegraph"}:
        hits.pop("companies", None)
    if "teacher-training" in hits:
        hits.pop("teachers", None)
    if "population-totals" in hits and set(hits) & {"age-and-sex", "occupations", "nationality-and-ethnicity"}:
        hits.pop("population-totals", None)
    if "crop-production" in hits and "miscellaneous grains" in title:
        hits.pop("crop-production", None)
    if "sericulture" in hits and not re.search(r"\bsilk\b", title):
        hits.pop("silk", None)
    if "sports-records" in hits:
        hits.pop("schools-and-pupils", None)
    if "production-subsidies" in hits and "freight-and-transport-costs" in hits:
        hits.pop("production-subsidies", None)
    non_demographic = {h["domain"] for h in hits.values()} - {"population", "commodity", "breakdown"}
    if non_demographic:
        for identifier in {"households", "occupations", "population-totals"} & hits.keys():
            hits[identifier]["domain"] = "breakdown"
    for general, specific in GENERAL_DETAIL.items():
        if general in hits and set(hits) & specific:
            hits.pop(general)
    if "age-and-sex" in hits and not ("population" in title or "inhabitants" in title):
        # Do not let the demographic breakdown determine the main topic.
        hits["age-and-sex"]["domain"] = "breakdown"

    commodity_hits = set(hits) & COMMODITIES
    if len(commodity_hits) > 2 or (len(hits) > 3 and len(commodity_hits) > 1):
        for identifier in commodity_hits:
            hits.pop(identifier)
        notes.append("Multiple commodity subjects: no arbitrary subset selected; retain explicit aggregate/measure subjects only.")
    all_hits = dict(hits)
    tags = list(hits) if len(hits) <= 3 else []
    if not tags and hits:
        notes.append("More than three independent detailed candidates; leave details for contents review rather than truncate.")

    domains = list(dict.fromkeys(h["domain"] for h in hits.values() if h["domain"] not in {"commodity", "breakdown"}))
    chapters = list(dict.fromkeys(topic for topic, expression in CHAPTERS if expression.search(chapter)))
    chapter_detail = None
    if not hits and re.search(r"\b(?:forestry|forest products|forests)\b", title):
        domains = ["forestry"]
    if not hits and re.search(r"\b(?:narcotics|narcotic drugs)\b", title):
        domains = ["narcotics"]
    if not domains and "leather-and-furs" in hits and re.search(r"\b(?:production|producing|manufactur\w*)\b", combined):
        domains = ["manufacturing"]
    if not domains and re.search(r"\b(?:manufactur\w*|spinning|weaving|fabrics|piece goods|refineries|brew\w*)\b", title):
        domains = ["manufacturing"]
    if not domains and set(hits) & {"coal", "gold", "silver", "copper", "iron-ore", "tin", "lead-and-zinc", "antimony", "phosphate-rock", "mercury"} and re.search(r"\b(?:mining|mines?|output|ore|deposits)\b", title):
        domains = ["mining"]
    if not domains and re.search(r"\b(?:trade (?:in|of|with)|trade returns|commercial exchange|retail sales|wholesale sales)\b", title):
        domains = ["trade"]
    if not domains and len(chapters) == 1:
        domains = chapters
        if not tags and re.search(r"railways?", chapter) and not re.search(r"transport|communications|ship", chapter):
            chapter_detail = "railways"
        if not tags and re.fullmatch(r"(?:japan — )?(?:banks and banking business|banking)", chapter):
            chapter_detail = "banking"
    if chapter_detail:
        tags = [chapter_detail]
        all_hits[chapter_detail] = {"domain": domains[0], "field": "chapter", "matched": metadata["chapter"]}

    # Explicit measure/process combinations take precedence over a commodity's
    # production association or the book/chapter's publication setting.
    if set(hits) & TRADE_FLOW:
        domains = ["trade"] + (["narcotics"] if re.search(r"\b(?:opium|morphine|heroin|narcotics)\b", title) else [])
    elif "tariffs" in hits:
        domains = ["trade", "finance"]
    elif "education-finance" in hits:
        domains = ["education", "finance"]
    elif "prison-labour" in hits:
        domains = ["crime-and-justice", "labour"]
    elif "public-budgets" in hits:
        sectors = [x for x in domains if x not in {"finance", "government"}]
        domains = [sectors[0], "finance"] if len(sectors) == 1 else ["finance"]
    elif set(hits) & {"taxation", "land-tax", "salt-tax", "head-tax", "customs-revenue", "public-debt", "foreign-loans", "foreign-exchange"}:
        domains = ["finance"]
    elif "wages" in hits:
        sectors = [x for x in domains if x not in {"finance", "government", "labour"}]
        domains = [sectors[0], "labour"] if len(sectors) == 1 else ["labour"]
    elif "prices" in hits:
        domains = ["trade"]
    elif "insurance-and-pensions" in hits:
        domains = ["finance"]
    elif set(hits) & {"diseases", "epidemics", "medical-services", "infant-mortality", "mental-health", "veterinary-health", "vaccination", "malaria", "leprosy"}:
        if "infant-mortality" in hits and not (set(hits) & {"diseases", "epidemics", "medical-services"}):
            domains = ["population"]
        else:
            other = [x for x in domains if x not in {"population", "health", "agriculture"}]
            domains = ["health"] + (other[:1] if len(other) == 1 else [])
    elif re.search(r"\bhealth of .{0,20}students\b", title):
        domains = ["health", "education"]
        tags = []
    elif "production-subsidies" in hits:
        sectors = [x for x in domains if x != "economy"]
        domains = [sectors[0], "economy"] if len(sectors) == 1 else ["economy"]
    elif "government-offices" in hits:
        domains = ["government"]
    elif "imperial-household" in hits:
        domains = ["government"]
    elif "births-and-deaths" in hits and set(domains) - {"population"}:
        domains = [x for x in domains if x != "population"]
    if any(re.search(expression, title) for expression in [r"\b(?:aboriginal|indigenous|islanders?)\b", r"島民|蕃人|高砂族"]):
        if len(domains) < 2 and "indigenous-peoples" not in domains:
            domains.append("indigenous-peoples")
        # Explicit Indigenous subjects only; collection is never evidence.
    topics = domains if len(domains) <= 2 else []
    if len(domains) > 2:
        notes.append("Several incompatible principal-topic candidates; defer high-level assignment.")
    if not tags and commodity_hits and len(commodity_hits) <= 2 and not all_hits:
        notes.append("Commodity evidence insufficient for a detailed choice.")
    quantitative = bool(re.search(r"\b(?:number|numbers|quantity|quantities|amount|amounts|counts|count|percentages?|rates?|tonnage|acreage|output|production|expenditure|expenses|receipts|revenue|profit|loss|assets|liabilities|salaries|wages|prices?|population|deaths|births|mortality|enrolment|enrollment|attendance|totals|values?)\b", combined))
    textual = bool(re.search(r"\b(?:names of|names and|office[- ]holders|roster|directory|alphabet|phonetic symbols|list of (?:officials|ministers|treaties|members)|chronology|chronological table|equivalents of ranks|rank equivalents)\b", combined))
    flag_status = "statistical-from-metadata" if quantitative else "text-from-metadata" if textual else "unknown-needs-contents"
    flags = ["text-tables"] if flag_status == "text-from-metadata" else []
    questions = []
    if not topics:
        questions.append("Review full contents to establish high-level topics.")
    if not tags:
        questions.append("Review full contents to establish detailed tags.")
    if flag_status == "unknown-needs-contents":
        questions.append("Review full contents to determine the text/statistical flag.")
    used = {identifier: all_hits[identifier] for identifier in tags}
    evidence = "; ".join(f"{identifier}: {item['field']}={item['matched']!r}" for identifier, item in used.items())
    if not evidence:
        evidence = "No sufficiently specific detailed subject established by allowed metadata."
    row = {"topics": topics, "tags": tags, "flags": flags,
           "rationale": "Metadata-only first pass. " + evidence,
           "review_questions": questions}
    provenance = {"method": "metadata-only-first-pass", "confidence": {"topics": "high" if topics else "unassigned", "tags": "high" if tags else "unassigned"},
                  "detail_evidence": used, "topic_candidates": domains, "chapter_candidates": chapters,
                  "flag_status": flag_status, "notes": notes}
    return row, provenance


def build():
    manifest = read(OUT / "manifest.json")
    assert sha(OUT / "metadata.json") == manifest["metadata_sha256"]
    assert sha(OUT / "vocabulary.json") == manifest["vocabulary_sha256"]
    records = read(OUT / "metadata.json")
    vocab = read(OUT / "vocabulary.json")
    approved = {kind: {x["id"] for x in vocab[kind]} for kind in ("topics", "tags", "flags")}
    assert {x[0] for x in RULES} <= approved["tags"]
    preserved = read(OUT / "preserved-pilot.json")["assignments"]
    assignments, audit, queue = {}, {}, []
    for record in records:
        key = record["key"]
        if key in preserved:
            row = preserved[key]
            provenance = {"method": "preserved-complete-record-pilot", "flag_status": "preserved-reviewed", "confidence": {"topics": "previously-reviewed", "tags": "previously-reviewed"}}
        else:
            row, provenance = classify(record["metadata"])
        for field in approved:
            assert len(row[field]) == len(set(row[field])) and set(row[field]) <= approved[field], (key, field)
        assert len(row["topics"]) <= 2 and len(row["tags"]) <= 3
        assignments[key] = row
        audit[key] = provenance | {"metadata_sha256": digest(record["metadata"])}
        if not row["topics"] or not row["tags"] or provenance["flag_status"] == "unknown-needs-contents":
            queue.append({"key": key, "book": record["book"], "metadata": record["metadata"],
                          "topics": row["topics"], "tags": row["tags"], "flag_status": provenance["flag_status"], "questions": row["review_questions"]})
    result = {"schema_version": 1, "classifier": "assistant-authored-metadata-rules", "classification_stage": "metadata-only-first-pass",
              "review_status": "partial-awaiting-contents-review", "vocabulary_version": vocab["vocabulary_version"],
              "field_limits": {"topics": {"min": 0, "max": 2}, "tags": {"min": 0, "max": 3}},
              "flag_semantics": "An empty flags list with provenance flag_status unknown-needs-contents does not establish statistical content.", "assignments": assignments}
    write(OUT / "assignments.japan-manchuria-south-seas.json", result)
    for group in GROUPS:
        subset = {r["key"]: assignments[r["key"]] for r in records if r["book"]["collection"] == group}
        write(OUT / f"assignments.{group}.json", result | {"collection": group, "assignments": subset})
    write(OUT / "provenance.json", {"tables": audit})
    write(OUT / "review-queue.json", {"count": len(queue), "tables": queue})
    write(OUT / "no-topics.json", {"count": sum(not x["topics"] for x in assignments.values()), "tables": [r for r in queue if not r["topics"]]})
    write(OUT / "no-detailed-tags.json", {"count": sum(not x["tags"] for x in assignments.values()), "tables": [r for r in queue if not r["tags"]]})
    write(OUT / "flag-review-queue.json", {"count": sum(x["flag_status"] == "unknown-needs-contents" for x in audit.values()), "tables": [r for r in queue if r["flag_status"] == "unknown-needs-contents"]})
    write(OUT / "candidate-summary.json", {g: {"tables": sum(r["book"]["collection"] == g for r in records),
          "topics": sum(bool(assignments[r["key"]]["topics"]) for r in records if r["book"]["collection"] == g),
          "details": sum(bool(assignments[r["key"]]["tags"]) for r in records if r["book"]["collection"] == g),
          "preserved": sum(r["key"] in preserved for r in records if r["book"]["collection"] == g)} for g in GROUPS})
    print(json.dumps(read(OUT / "candidate-summary.json"), indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=["prepare", "build"])
    args = parser.parse_args()
    prepare() if args.action == "prepare" else build()
