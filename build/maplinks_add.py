#!/usr/bin/env python3
"""maplinks_add.py: add "View as Map" entries to build/maplinks.json for tables by prefecture.

    python3 build/maplinks_add.py --dry book/table [book/table ...]   # what it would add, and why not
    python3 build/maplinks_add.py book/table [book/table ...]         # add them

Each table named, and every other member of a "Similar tables" family it belongs to
(build/crosslinks/families), gets an entry when one of its parts names the prefectures down a column
(30 or more of the 47, by maplinks.match_place, the same matcher the link uses). The entry sends the
columns whose figures are mostly numbers, marks each as a count, amount, rate or index from its heading
(per-capita view only for counts), takes the printed total row when there is one, and dates the table by
the last year in its title (else the edition year), with the map period 1930 before 1938 and 1942 after.
Tables already in maplinks.json are left as they are; nothing else in the file is touched.
"""
import glob, json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
SITE = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import maplinks as M  # noqa: E402

TOTAL = re.compile(r"^(total|grand total|totals|whole (country|empire)|empire|all japan|japan proper|sum|"
                   r"計|合計|總計|総計|全國|全国|總數|総数|帝國|帝国|內地|内地)\b", re.I)
RATE = re.compile(r"per\b|%|percent|per cent|ratio|rate|average|mean|density|毎|千ニ付|千に付|比率|割合|平均|百分|歩合", re.I)
INDEX = re.compile(r"\bindex\b|指數|指数", re.I)
AMOUNT = re.compile(r"\byen\b|圓|円|value|amount|cost|expend|revenue|income|價額|金額|錢|銭|£|\$", re.I)
MIN_PREF = 30
TYPO = {"nngasaki": "42", "niye": "24", "osakafu": "27"}   # misprints or misreadings, pinned with row_ids
POP = re.compile(r"population|inhabitants|人口", re.I)
AREA = re.compile(r"\barea\b|sq\.|square|chobu|chō|町歩|面積|ri\b", re.I)
YEAR = re.compile(r"^\s*(1[89]\d\d)\b")
BLOCK = re.compile(r"\s*[—–]\s*(left|right|middle|first|second|third|fourth) block\s*$", re.I)


def place(label):
    """match_place, or the part before a dash when the cell adds a governor's name ("Tokyo-fu—M. Munekata")."""
    label = str(label).strip()
    if label.lower() in TYPO:
        return TYPO[label.lower()]
    pid = M.match_place(label)
    if not pid:
        m = re.match(r"^(\S+-(?:ken|fu|cho|chō))\b", label)
        if m:
            pid = M.match_place(m.group(1))
    if not pid and re.search(r"[—–]", label):
        bits = re.split(r"\s*[—–]\s*", label)
        pid = M.match_place(bits[0]) or M.match_place(bits[-1])   # "Tokyo-fu—M. Munekata", "1st Circuit — Tokyo"
    return pid


def load_families():
    fam = {}
    for f in glob.glob(os.path.join(HERE, "crosslinks", "families", "*.json")):
        d = json.load(open(f, encoding="utf-8"))
        for fm in d.get("families", []):
            for m in fm.get("members", []):
                fam.setdefault(m, set()).update(fm.get("members", []))
    return fam


_books = {}


def table(book, tid):
    if book not in _books:
        f = os.path.join(SITE, "data", book + ".json")
        _books[book] = {t["id"]: t for t in json.load(open(f, encoding="utf-8"))} if os.path.exists(f) else {}
    return _books[book].get(tid)


def year_of(book, t):
    ys = [int(y) for y in re.findall(r"\b(1[89]\d\d)\b", " ".join([t.get("title") or "", t.get("caption_extra") or ""]))]
    if ys:
        return str(max(ys))
    m = re.search(r"(1[89]\d\d)", book)
    return m.group(1) if m else None


def entry(book, tid):
    t = table(book, tid)
    if not t:
        return None, "no such table"
    best = None
    for pi, p in enumerate(t.get("parts") or []):
        for lc in (0, 1):
            ids = [place(r[lc]) if len(r) > lc else None for r in p["rows"]]
            n = len({i for i in ids if i and i.isdigit()})
            if n >= MIN_PREF and (best is None or n > best[2]):
                best = (pi, lc, n, ids)
    if not best:
        return joined(book, tid, t)
    pi, lc, n, ids = best
    return entry_for(book, tid, t, pi, lc, n)


def entry_for(book, tid, t, pi, lc, n, only=None):
    p = t["parts"][pi]
    if re.search(r"\bcit(y|ies)\b|市", str(p["columns"][lc]), re.I):
        return None, "a table of cities (its names overlap the prefectures'); the map link sends prefectures only"
    ids = [place(r[lc]) if len(r) > lc else None for r in p["rows"]]
    from collections import Counter
    if sum(1 for v in Counter(i for i in ids if i).values() if v > 1) >= 3:
        return None, "prefectures repeat (sub-rows, e.g. port and rest of prefecture)"
    rows = [r for r, i in zip(p["rows"], ids) if i]
    cols, meta = [], {}
    for j, c in enumerate(p["columns"]):
        if j == lc or (only is not None and j not in only):
            continue
        vals = [M.value(r[j]) for r in rows if j < len(r)]
        nums = sum(1 for v in vals if isinstance(v, (int, float)))
        if vals and nums >= 0.5 * len(vals):
            cols.append(j)
            name = str(c)
            title_rate = bool(RATE.search((t.get("title") or "") + " " + (t.get("caption_extra") or "")))
            kind = ("rate" if RATE.search(name) or title_rate else "index" if INDEX.search(name)
                    else "amount" if AMOUNT.search(name) else "other" if AREA.search(name) else "count")
            pc = kind == "count" and not POP.search(name)
            meta[str(j)] = {"unit": "", "kind": kind, "pc": pc, "color": "seq"}
    if not cols:
        return None, "no column of figures"
    total = None
    for ri, (r, i) in enumerate(zip(p["rows"], ids)):
        if not i and len(r) > lc and TOTAL.search(str(r[lc]).strip()):
            total = ri
            break
    row_ids = {str(ri): i for ri, (r, i) in enumerate(zip(p["rows"], ids))
               if i and len(r) > lc and not M.match_place(str(r[lc]))}
    y = year_of(book, t)
    years = [int(YEAR.match(str(p["columns"][j])).group(1)) if YEAR.match(str(p["columns"][j])) else None for j in cols]
    default = years.index(max(y for y in years if y)) if all(years) and len(cols) > 1 else 0
    en = {str(j): BLOCK.sub("", str(p["columns"][j])) for j in cols if BLOCK.search(str(p["columns"][j]))}
    e = {"book": book, "table": tid, "part": pi, "label_col": lc, "columns": cols, "default": default,
         "total_row": total, "date": y, "period": "1930" if y and int(y) < 1938 else "1942", "col_meta": meta}
    if row_ids:
        e["row_ids"] = row_ids
    if en:
        e["en_columns"] = en
    if any(m["kind"] in ("rate", "index") for m in meta.values()):
        e["check_total"] = False
    return e, f"{n} prefectures, part {pi}, label column {lc}, {len(cols)} columns"


def prefs(t):
    """[(part, label_col, set of prefecture ids, n columns)] for every part and label column of a table."""
    out = []
    for pi, p in enumerate(t.get("parts") or []):
        for lc in (0, 1):
            ids = {place(r[lc]) for r in p["rows"] if len(r) > lc} - {None}
            ids = {i for i in ids if i.isdigit()}
            if ids:
                out.append((pi, lc, ids, len(p["columns"])))
    return out


def joined(book, tid, t):
    """A prefecture table printed over two pages and stored as two records: pair it with the record before or
    after it when they have the same number of columns and name 30 prefectures between them."""
    if re.search(r"\bcit(y|ies)\b|\bdistricts?\b|\bports?\b|市", t.get("title") or "", re.I):
        return None, "a table of cities, districts or ports, not prefectures"   # their names overlap
    for pi, p in enumerate(t.get("parts") or []):   # two blocks printed side by side in one part
        nc = len(p["columns"])
        L = [c for c in range(nc) if len({place(r[c]) for r in p["rows"] if len(r) > c} - {None}) >= 5]
        w = L[1] - L[0] if len(L) >= 2 else 0
        if len(L) >= 2 and all(L[k + 1] - L[k] == w for k in range(len(L) - 1)) and nc - L[-1] == w:
            sets = [{place(r[c]) for r in p["rows"] if len(r) > c} - {None} for c in L]
            u = set().union(*sets)
            if len({x for x in u if x.isdigit()}) >= MIN_PREF:
                e, why = entry_for(book, tid, t, pi, L[0], len(u), list(range(L[0] + 1, L[1])))
                if e:
                    e["also"] = [{"table": tid, "part": pi, "label_col": c, "columns": [j + (c - L[0]) for j in e["columns"]]}
                                 for c in L[1:]]
                    return e, why + f"; {len(L)} blocks side by side ({' + '.join(str(len(x)) for x in sets)} prefectures)"
    P = prefs(t)                                       # one table stored as several parts
    for pi, lc, a, nc in sorted(P, key=lambda x: -len(x[2])):
        rest = [(qi, qlc, b) for qi, qlc, b, qnc in P if qi != pi and qnc == nc and qlc == lc]
        u = a.union(*[b for _, _, b in rest]) if rest else a
        if rest and len(u) >= MIN_PREF:
            e, why = entry_for(book, tid, t, pi, lc, len(u))
            if e:
                e["also"] = [{"table": tid, "part": qi, "label_col": qlc} for qi, qlc, _ in rest]
                return e, why + f"; parts {[pi] + [q for q, _, _ in rest]} of one table"
        break
    order = list(_books[book])
    i = order.index(tid)
    for j in (i + 1, i - 1):
        if not 0 <= j < len(order):
            continue
        o = _books[book][order[j]]
        if re.search(r"\bcit(y|ies)\b|\bdistricts?\b|\bports?\b|市", o.get("title") or "", re.I):
            continue
        for pi, lc, a, nc in prefs(t):
            for opi, olc, b, onc in prefs(o):
                if nc == onc and len(a | b) >= MIN_PREF and len(a) >= 5:
                    e, why = entry_for(book, tid, t, pi, lc, len(a | b))
                    if e:
                        e["also"] = [{"table": order[j], "part": opi, "label_col": olc}]
                        return e, why + f"; joined with {order[j]} ({len(a)} + {len(b)} prefectures)"
    return None, "no part names 30 prefectures down a column, and no neighbouring half to join"


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    dry = "--dry" in sys.argv
    fam = load_families()
    want = []
    for a in args:
        for m in sorted({a} | fam.get(a, set())):
            if m not in want:
                want.append(m)
    cfg_f = os.path.join(HERE, "maplinks.json")
    cfg = json.load(open(cfg_f, encoding="utf-8"))
    have = {(c["book"], c["table"]) for c in cfg["tables"]}
    added = []
    for m in want:
        book, tid = m.split("/", 1)
        if (book, tid) in have:
            print(f"have  {m}")
            continue
        e, why = entry(book, tid)
        print(("add   " if e else "skip  ") + f"{m}: {why}")
        if e:
            added.append(e)
    if added and not dry:
        cfg["tables"] += added
        open(cfg_f, "w", encoding="utf-8").write(json.dumps(cfg, ensure_ascii=False, indent=1) + "\n")
    print(f"{len(added)} {'would be ' if dry else ''}added; {len(want)} tables considered")


if __name__ == "__main__":
    main()
