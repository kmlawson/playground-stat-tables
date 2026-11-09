"""Build the Population page: figures/population.html and data/population/*.json (+ table_links.json).

    python3 build/finders/population/build_population.py   (normally run by build/finders/build_all.py at the end of
                                                             build_site.py; it copies the home page's header, footer
                                                             and styles from index.html)

Claims come from extract.py (specs in specs/, fixes in spec_fixes.json, places in ../places/). Figures are exactly as transcribed;
the page groups the same figure from several tables and shows differing figures side by side, never averaging,
smoothing or filling gaps.
"""
import html, json, os, re, statistics, sys
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))     # build/finders/population
BUILD = os.path.dirname(os.path.dirname(HERE))
SITE = os.path.dirname(BUILD)
sys.path.insert(0, HERE)
import extract as X  # noqa: E402
import make_previews as MP  # noqa: E402

OUT = os.path.join(SITE, "data", "population")
BUCKETS = ["japan", "korea", "taiwan", "karafuto", "kwantung", "nanyo", "manchuria", "china", "world", "empire"]
METRICS = ["total", "male", "female", "households"]
TOPS = ["empire", "japan", "korea", "taiwan", "karafuto", "kwantung-zone", "nanyo", "manchuria", "china", "world"]


def edition_year(b):
    m = re.search(r"(1[89]\d\d|19\d\d)", b.get("title", ""))
    return int(m.group(1)) if m else None


def main(chrome=None):
    if chrome is None:
        sys.path.insert(0, os.path.dirname(HERE))
        from build_all import chrome
    B = MP.books()
    editions = {s: edition_year(b) for s, b in B.items()}
    specs = X.load_specs()
    claims, made, unplaced, problems = X.claims(specs, editions)
    places = dict(X.PL)
    places.update(made)
    # the page's own tree where it differs from the gazetteer's (config "place_up": Kwantung and the Railway Zone sit
    # under the combined unit the tables usually print, so the home tile is the combined unit)
    CFG = json.load(open(os.path.join(HERE, "config.json")))
    for pid, up in CFG.get("place_up", {}).items():
        if pid in places and up in places:
            places[pid] = dict(places[pid], up=up)
    MERGE = {a: b for a, b in CFG.get("place_merge", {}).items() if b in places}
    for c in claims:
        c["place"] = MERGE.get(c["place"], c["place"])
    for pid, p in list(places.items()):
        if p.get("up") in MERGE:
            places[pid] = dict(p, up=MERGE[p["up"]])

    # drop claims whose metric is not one we show; normalise groups
    claims = [c for c in claims if c["m"] in METRICS]
    for c in claims:
        g = re.sub(r"[^a-z\- ]", "", (c["g"] or "all").lower()).strip() or "all"
        c["g"] = {"japanese subjects": "all", "natives": "islander", "kanaka": "islander", "chamorro": "chamorro",
                  "foreigners": "foreign", "han": "taiwanese", "formosan": "taiwanese", "hondo": "japanese",
                  "naichijin": "japanese", "americans": "american", "british subjects": "british", "manchoukuoan": "manchurian",
                  "manchukuoan": "manchurian", "manchurians": "manchurian", "kanakas": "kanaka", "chamorros": "chamorro",
                  "koreans": "korean", "chinese nationals": "chinese", "japanese nationals": "japanese", "foreign": "foreign",
                  "english": "british", "czecho-slovak": "czechoslovak", "austrohungarian": "austro-hungarian"}.get(g, g)

    # ancestors and bucket of each place
    def chain(pid):
        out, seen = [], set()
        while pid and pid in places and pid not in seen:
            seen.add(pid)
            out.append(pid)
            pid = places[pid]["up"]
        return out

    def bucket(pid):
        ch = chain(pid)
        for p in ch:
            if p in BUCKETS and p != "empire":
                return p
        return "empire"

    # sources
    src_ix, srcs = {}, []
    TR = {}
    for c in claims:
        k = c["src"]
        if k in src_ix:
            continue
        slug, tid = k.split(":", 1)
        t = X.table(slug, tid) or {}
        if slug not in TR:
            p = os.path.join(BUILD, "translations", slug + ".json")
            TR[slug] = json.load(open(p)) if os.path.exists(p) else {}
        en = (TR[slug].get(tid) or {}).get("t")
        b = B.get(slug, {})
        src_ix[k] = len(srcs)
        srcs.append([slug, tid, b.get("title", slug), editions.get(slug) or 0, (t.get("title") or "").strip(), en or "",
                     ", ".join(t.get("printed_pages") or [])])

    labels, label_ix = [], {}
    notes, note_ix = [], {}

    def intern(s, L, I):
        if s in (None, ""):
            return -1
        if s not in I:
            I[s] = len(L)
            L.append(s)
        return I[s]

    BASES = ["", "census", "registered", "resident", "estimate", "survey", "police", "other"]
    groups = Counter(c["g"] for c in claims)
    GROUPS = ["all"] + [g for g, _ in groups.most_common() if g != "all"]
    per_bucket = defaultdict(lambda: defaultdict(list))
    bucket_lists = defaultdict(lambda: {"L": [], "LI": {}, "N": [], "NI": {}})
    stats = defaultdict(lambda: {"n": 0, "y0": 9999, "y1": 0, "tot": Counter(), "g": Counter(), "m": Counter()})
    for c in claims:
        b = c["b"] if c["b"] in BASES else ("other" if c["b"] else "")
        mult = 0
        row = [c["year"], c["date"] if c["date"] != str(c["year"]) else "", METRICS.index(c["m"]), GROUPS.index(c["g"]), c["v"],
               src_ix[c["src"]], c["part"], c["row"], c["col"], BASES.index(b), -1,
               1 if c["approx"] else 0, -1]
        bk = bucket(c["place"])
        BL = bucket_lists[bk]
        row[10] = intern(c["n"], BL["N"], BL["NI"])
        # the figure as printed, where it is not the figure shown: printed in thousands (19,523 -> 19,523,000) or
        # with a point for the comma ("65.687"); the page shows both, so the reader can find it in the table
        raw = X.number(c["cell"], 1)
        f = c.get("mult") or 1
        if raw != c["v"] or f != 1:
            row.append(intern(f"{str(c['cell']).strip()}|{f if f > 1 else ''}", BL["L"], BL["LI"]))
        row[12] = intern(c["label"], BL["L"], BL["LI"])
        per_bucket[bk][c["place"]].append(row)
        s = stats[c["place"]]
        s["n"] += 1
        s["y0"] = min(s["y0"], c["year"])
        s["y1"] = max(s["y1"], c["year"])
        s["g"][c["g"]] += 1
        s["m"][c["m"]] += 1
        if c["m"] == "total" and c["g"] == "all":
            s["tot"][(c["year"], c["v"])] += 1

    # place index: only places with figures, plus their ancestors
    keep = set()
    for pid in stats:
        keep.update(chain(pid))
    P = {}
    for pid in keep:
        p = places[pid]
        s = stats.get(pid)
        latest = None
        if s and s["tot"]:
            y = max(y for y, v in s["tot"])
            v = max(((n, v) for (yy, v), n in s["tot"].items() if yy == y))[1]
            latest = [y, v]
        P[pid] = {"en": p["en"], "ja": p.get("ja") or "", "k": p["k"], "up": p["up"] if p["up"] in keep else None,
                  "n": s["n"] if s else 0, "y": [s["y0"], s["y1"]] if s else None, "l": latest,
                  "b": bucket(pid)}
    # printed forms per place, for search
    forms = defaultdict(Counter)
    for c in claims:
        forms[c["place"]][c["label"]] += 1
    for pid, f in forms.items():
        al = [l for l, _ in f.most_common(6) if l not in (P[pid]["en"], P[pid]["ja"]) and len(l) < 40]
        if al:
            P[pid]["a"] = al
    # whole-subtree counts
    for pid in keep:
        P[pid]["nt"] = 0
    for pid, s in stats.items():
        for a in chain(pid):
            P[a]["nt"] += s["n"]

    os.makedirs(OUT, exist_ok=True)
    # compact form: id -> [en, ja, kind, parent, n, first year, last year, latest year, latest figure, file, n within, printed forms]
    PC = {pid: [p["en"], p["ja"], p["k"], p["up"] or "", p["n"], (p["y"] or [0, 0])[0], (p["y"] or [0, 0])[1],
                (p["l"] or [0, 0])[0], (p["l"] or [0, 0])[1], p["b"], p["nt"]] + ([p["a"]] if p.get("a") else []) for pid, p in P.items()}
    idx = {"places": PC, "src": srcs, "groups": GROUPS, "bases": BASES, "metrics": METRICS,
           "tops": [t for t in TOPS if t in P], "n": len(claims), "tables": len(src_ix),
           "pn": {k: v for k, v in CFG.get("place_notes", {}).items() if k in P},
           "cb": {k: v for k, v in CFG.get("chart_break", {}).items() if k in P},
           "srcs": sources(P),
           "tn": {k: v for k, v in CFG.get("top_notes", {}).items() if k in P}}
    json.dump(idx, open(os.path.join(OUT, "index.json"), "w"), ensure_ascii=False, separators=(",", ":"))
    for b, d in per_bucket.items():
        json.dump({"c": d, "labels": bucket_lists[b]["L"], "notes": bucket_lists[b]["N"]}, open(os.path.join(OUT, b + ".json"), "w"),
                  ensure_ascii=False, separators=(",", ":"))
    write_page(idx, chrome)
    # each table's figures -> the place to open on the page (one place: that place; several: the unit they are in), for
    # the "Across all books" link on table pages (read by build_site.py through registry.table_links(): one build behind)
    by_src = defaultdict(Counter)
    for c in claims:
        by_src[c["src"]][c["place"]] += 1
    links = {}
    for k, cnt in by_src.items():
        ps = list(cnt)
        grp = [g for g, within in CFG.get("link_groups", {}).items()
               if g in cnt and all(p == g or set(chain(p)) & set(within) for p in ps)]
        if grp:
            target = grp[0]
        elif len(ps) == 1:
            target = ps[0]
        else:
            ups = Counter(P[p]["up"] for p in ps if p in P)
            # the unit most of the places are in, if it has a page; else the most frequent place
            up, n = ups.most_common(1)[0] if ups else (None, 0)
            target = up if up and up in P and n >= len(ps) / 2 else cnt.most_common(1)[0][0]
        slug, tid = k.split(":", 1)
        links.setdefault(slug, {})[tid] = [target, P[target]["en"] if target in P else target]
    json.dump(links, open(os.path.join(HERE, "table_links.json"), "w"), ensure_ascii=False, separators=(",", ":"), sort_keys=True)
    # report
    sizes = {f: os.path.getsize(os.path.join(OUT, f)) // 1024 for f in os.listdir(OUT)}
    print(f"population: {len(claims):,} figures from {len(src_ix):,} tables, {len(P):,} places; files (KB) {sizes}")
    print(f"population: {sum(1 for s in specs.values() if 'x' in s):,} tables used, {sum(1 for s in specs.values() if 'skip' in s):,} skipped")
    os.makedirs(os.path.join(HERE, "work"), exist_ok=True)
    with open(os.path.join(HERE, "work", "unplaced.txt"), "w") as fh:
        for (lab, pt, w, rk), n in unplaced.most_common():
            fh.write(f"{n}\t{rk}\t{lab}\t{pt}\t{w}\n")
    with open(os.path.join(HERE, "work", "problems.txt"), "w") as fh:
        for k, n in problems.most_common():
            fh.write(f"{n}\t{k}\n")
    print(f"population: {len(unplaced):,} labels not in the gazetteer (work/unplaced.txt), {len(problems)} spec problems (work/problems.txt)")
    if X.L.STALE:
        print(f"population: {len(X.L.STALE)} specs left out because their table changed (run build/finders/status.py)")
    return {"n": len(claims), "tables": len(src_ix), "places": len(P)}


def sources(P):
    """sources.json: {region id: [{name, by, kind, home, deep, lang, what}]} -> what the page shows above a place's
    figures (the nearest region up the tree that has a list)."""
    p = os.path.join(HERE, "sources.json")
    if not os.path.exists(p):
        return {}
    S = json.load(open(p))
    return {k: [[x["name"], x.get("by", ""), x.get("kind", ""), x.get("home", ""), x.get("deep", ""), x.get("lang", ""),
                 x.get("what", "")] for x in v] for k, v in S.items() if k in P and not k.startswith("_")}


def noscript_list(idx):
    """A plain list of the places with most figures, for readers and robots without JavaScript."""
    P = idx["places"]
    kids = defaultdict(list)
    for pid, a in P.items():
        if a[3] and a[10] >= 10:
            kids[a[3]].append(pid)
    def li(pid, depth):
        a = P[pid]
        sub = sorted(kids.get(pid, []), key=lambda k: -P[k][10])
        inner = ("<ul>" + "".join(li(k, depth + 1) for k in sub) + "</ul>") if sub and depth < 2 else ""
        yrs = f", {a[5]}–{a[6]}" if a[4] else ""
        return f'<li><a href="#p={html.escape(pid)}">{html.escape(a[0])}</a> {html.escape(a[1])} ({a[10]:,} figures{yrs}){inner}</li>'
    return "<noscript><p>This page needs JavaScript to show the figures. The places it covers:</p><ul>" + "".join(li(t, 0) for t in idx["tops"]) + "</ul></noscript>"


def write_page(idx, chrome):
    head, style, band, foot = chrome("../")
    page = PAGE.replace("__HEAD__", head).replace("__STYLE__", style).replace("__BAND__", band).replace("__FOOT__", foot)
    page = page.replace("__N__", f"{idx['n']:,}").replace("__T__", f"{idx['tables']:,}").replace("__NOSCRIPT__", noscript_list(idx))
    os.makedirs(os.path.join(SITE, "figures"), exist_ok=True)
    open(os.path.join(SITE, "figures", "population.html"), "w", encoding="utf-8").write(page)


PAGE = open(os.path.join(HERE, "page.html"), encoding="utf-8").read() if os.path.exists(os.path.join(HERE, "page.html")) else ""

if __name__ == "__main__":
    main()
