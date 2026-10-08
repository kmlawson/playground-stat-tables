"""Listings for the korea-annual series: chapter topics as in chapters.py, plus statistical-appendix tables
("Statistical Tables" / "Statistics") assigned to subject topics by title keywords, so they can be matched
with the same tables printed in the chapters of other editions."""
import json, os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from chapters import SERIES
from make_listings import slug, cut, D

KW = [
    ("General survey and population", r"population|families|dwelling|area and|geograph|meteorolog|temperature|situation of chosen"),
    ("Local administration", r"local revenue|school associations|water-utilization|waterworks"),
    ("Justice and prisons", r"law courts|civil and criminal|prisoners|good offices|penal"),
    ("Finance", r"revenue|expenditure|taxation|budget"),
    ("Currency and banking", r"bank|money|savings|wages|prices"),
    ("Government undertakings and monopolies", r"lumber undertaking|coal mines|salt"),
    ("Civil engineering", r"harbour|roads"),
    ("Communications and transport", r"posts|postal|mail|telegraph|telephone|railway|vessels|shipping|parcels|money orders"),
    ("Commerce and foreign trade", r"trade|exports"),
    ("Agriculture", r"cultivated|rice|corn|beans|agricultural|fruits|silkworm|live-stock"),
    ("Companies and manufacturing", r"companies|factories"),
    ("Mining, forestry and fishery", r"mineral|forest|afforestation|fishery|lumber"),
    ("Sanitation", r"hospital|patients|physicians"),
    ("Education", r"school"),
    ("Religion and charity", r"religious|charity asylum"),
]
S = SERIES["korea-annual"]
data = {b: json.load(open(os.path.join(D, b + ".json"), encoding="utf-8")) for b in S["books"]}
APPX = {"Statistical Tables", "Statistics"}
for top, m in S["topics"].items():
    rx = dict(KW).get(top)
    L = [f"# Series: {S['name']} — topic: {top}", "# Editions: " + ", ".join(S["books"]),
         "# Format: slug | id | chapter | pp. | title | caption | columns | first-column row labels",
         "# Tables from a 'Statistical Tables'/'Statistics' appendix are included where their title fits this topic.", ""]
    for b in S["books"]:
        rows = []
        for t in data[b]:
            ch = t.get("chapter")
            if not (ch in m.get(b, []) or (rx and ch in APPX and top != "Statistical appendix"
                                            and re.search(rx, (t.get("title") or ""), re.I))):
                continue
            parts = t.get("parts") or []
            cols = [c for p in parts[:1] for c in p.get("columns", [])]
            stubs = [r[0] for p in parts[:1] for r in p.get("rows", []) if r and r[0] and r[0] != '"'][:8]
            rows.append(" | ".join([b, t["id"], cut(ch, 30), ",".join(t.get("printed_pages") or []),
                                    cut(t.get("title"), 170), cut(t.get("caption_extra"), 80),
                                    cut("; ".join(cols), 160), cut("; ".join(stubs), 120)]))
        if rows:
            L += [f"## {b}"] + rows
    with open(os.path.join(HERE, "listings", f"korea-annual--{slug(top)}.txt"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(L) + "\n")
    print(top, sum(1 for x in L if x.startswith("korea-")))
