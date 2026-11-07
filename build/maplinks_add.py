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
RATE = re.compile(r"per\b|%|percent|per cent|ratio|rate|average|mean|density|毎|ニ付|に付|當リ|當り|当り|當收|率|割合|平均|百分|歩合", re.I)
INDEX = re.compile(r"\bindex\b|指數|指数", re.I)
AMOUNT = re.compile(r"\byen\b|圓|円|value|amount|cost|expend|revenue|income|價額|金額|錢|銭|£|\$", re.I)
MIN_PREF = 30
TYPO = {"nngasaki": "42", "niye": "24", "osakafu": "27"}   # misprints or misreadings, pinned with row_ids
POP = re.compile(r"population|inhabitants|人口", re.I)
AREA = re.compile(r"\barea\b|sq\.|square|chobu|chō|町歩|面積|ri\b|[(（](町|反|坪|陌|方里|ヘクタール)[)）]", re.I)
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
    e = era_year(" ".join([t.get("title") or "", t.get("caption_extra") or ""]))
    if e:
        return e
    ys = [int(y) for y in re.findall(r"\b(1[89]\d\d)\b", " ".join([t.get("title") or "", t.get("caption_extra") or ""]))]
    if ys:
        return str(max(ys))
    m = re.search(r"(1[89]\d\d)", book)
    return m.group(1) if m else None


KN = {"〇": 0, "一": 1, "二": 2, "三": 3, "四": 4, "五": 5, "六": 6, "七": 7, "八": 8, "九": 9}


def era_year(label):
    """The year in a part label such as "地方別 (昭和八年)" or "府縣別 (昭和13年)", or None."""
    m = re.search(r"(明治|大正|昭和)\s*([〇一二三四五六七八九十]+|\d+)\s*年", str(label or ""))
    if not m:
        return None
    n = m.group(2)
    if not n.isdigit():
        v = 0
        for ch in n:
            v = (v or 1) * 10 if ch == "十" else v - v % 10 + KN[ch] if v % 10 == 0 and v >= 10 else v * 10 + KN[ch]
        n = v
    return str({"明治": 1867, "大正": 1911, "昭和": 1925}[m.group(1)] + int(n))


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
        e, why = joined(book, tid, t)
        if e:
            return e, why
        c, cwhy = city_entry(book, tid, t)
        return (c, cwhy) if c else (None, why + "; " + cwhy)
    pi, lc, n, ids = best
    e, why = entry_for(book, tid, t, pi, lc, n)
    if not e and why.startswith("a table of cities"):
        return city_entry(book, tid, t)
    return e, why


def entry_for(book, tid, t, pi, lc, n, only=None, pairs=False):
    p = t["parts"][pi]
    if re.search(r"\bcit(y|ies)\b|市", str(p["columns"][lc]), re.I):
        return None, "a table of cities (its names overlap the prefectures'); the map link sends prefectures only"
    ids = [place(r[lc]) if len(r) > lc else None for r in p["rows"]]
    from collections import Counter
    rep = Counter(i for i in ids if i)
    ids = [None if i and not i.isdigit() and rep[i] > 1 else i for i in ids]   # 朝鮮 — 小學校 / 普通學校: sub-rows, not the colony
    if not pairs and sum(1 for k, v in Counter(i for i in ids if i).items() if v > 1) >= 3:
        # 男 / 女 rows under each prefecture: one entry, the sex column splitting the measures (maplinks.build_city)
        sc = lc + 1
        sx = [str(r[sc]).strip() if len(r) > sc else "" for r, i in zip(p["rows"], ids) if i]
        if sx and set(sx) <= {"男", "女", "計", "總數", "Male", "Female", "M", "F", "Total"} and len(set(sx)) >= 2:
            e, why = entry_for(book, tid, t, pi, lc, n, [j for j in range(len(p["columns"])) if j not in (lc, sc)], pairs=True)
            if e:
                e.pop("row_ids", None)
                e.update({"units": "prefecture", "split_col": sc, "ids": {str(ri): i for ri, i in enumerate(ids) if i}})
                e.pop("total_row", None)
                return e, why + "; 男 / 女 rows under each prefecture"
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
            title_rate = bool(RATE.search(t.get("title") or ""))
            yen = bool(re.search(r"Unit: ?(円|圓)|單位[^)）]*(円|圓)|歳出|歳入|豫算|決算", (t.get("title") or "") + " " + (t.get("caption_extra") or "")))
            kind = ("rate" if RATE.search(name) or title_rate else "index" if INDEX.search(name)
                    else "amount" if AMOUNT.search(name) or yen else "other" if AREA.search(name) else "count")
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
    y = era_year(p.get("label")) or year_of(book, t)
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


_CITY = None


def city_index():
    """The map's city gazetteer as the candidates page reads it: (folder, {folded name: city id}, clean)."""
    global _CITY
    if _CITY is None:
        import importlib.util
        spec = importlib.util.spec_from_file_location("bc", os.path.join(HERE, "build_candidates.py"))
        bc = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(bc)
        F = bc.Folder(M)
        ix, _ = bc.build_indexes(F, M)
        _CITY = (F, ix["cities"], bc.clean, bc, ix)
    return _CITY


# The units other than prefectures and the empire's parts that a link can carry, by the candidates page's set names,
# and the "units" value each is sent as (MAPLINK_SPEC 4b, 4c). Ids are the map's own: its city ids, and the "key"
# column of texts/territories/sub-units/<file>.csv for the rest.
UNITS = {"prefectures": "prefecture", "cities": "city", "countries": "country", "china": "china-province", "korea": "korea-province", "manchukuo": "manchukuo-province",
         "taiwan-shu": "taiwan-prefecture", "taiwan-gun": "taiwan-district", "mandate": "nanyo-group"}


def city_entry(book, tid, t):
    """A table of cities or of provinces, prefectures or groups the map draws outside Japan proper: the part and axis
    the candidates page's classifier names best (bc.classify), with the ids from the same gazetteer."""
    F, cities, clean, bc, ix = city_index()
    best = None
    for pi, p in enumerate(t.get("parts") or []):
        axes = [(lc, False, [r[lc] if len(r) > lc else "" for r in p["rows"]]) for lc in (0, 1)]
        axes.append((0, True, [""] + list((p.get("columns") or [])[1:])))
        for lc, across, labs in axes:
            c = bc.classify([l for l in labs if str(l).strip()], M, F, ix, False)
            if not c or c[1] not in UNITS:
                continue
            if c[1] == "prefectures":     # only reached across the top: a prefecture table down the side is entry()'s
                index, fold = None, None
            else:
                index = ix[c[1]]
                fold = F.city if c[1] in ("cities", "taiwan-gun") else F.prov
            def look(l):
                if index is None:
                    p_ = place(l)
                    return p_ if p_ and p_.isdigit() else None
                if c[1] == "cities":      # "青森縣／青森市", "Tairen (Dalny)", never the bracketed prefecture
                    return bc.match_city(l, M, F, ix)
                hit = index.get(fold(clean(l)))
                if not hit and re.search(r"[(（]", str(l)):   # "Chihli (Hopei)": either name
                    hit = next((index.get(fold(x.strip())) for x in re.split(r"[()（）]", str(l)) if x.strip() and index.get(fold(x.strip()))), None)
                return hit
            ids = {k: look(l) for k, l in enumerate(labs) if str(l).strip() and not (across and k == 0)}
            ids = {k: v for k, v in ids.items() if v}
            n = len(set(ids.values()))
            if n and (best is None or n > best[3]):
                best = (pi, lc, across, n, ids, c[1])
    if not best:
        return territory_entry(book, tid, t)
    pi, lc, across, n, ids, unit = best
    p = t["parts"][pi]
    title_rate = bool(RATE.search(t.get("title") or ""))
    yen = bool(re.search(r"Unit: ?(円|圓)|單位[^)）]*(円|圓)|歳出|歳入|豫算|決算", (t.get("title") or "") + " " + (t.get("caption_extra") or "")))
    weather = bool(re.search(r"temperature|precipitat|rain|gale|wind|humidity|weather|climat|snow|氣溫|気温|降水|雨|風|濕度|氣象", (t.get("title") or ""), re.I))
    def kind_of(name):
        if weather:
            return {"unit": "", "kind": "other", "pc": False, "color": "seq"}
        k = ("rate" if RATE.search(name) or title_rate else "index" if INDEX.search(name)
             else "amount" if AMOUNT.search(name) or yen else "other" if AREA.search(name) else "count")
        return {"unit": "", "kind": k, "pc": k == "count" and not POP.search(name), "color": "seq"}
    meta, total, blocks = {}, None, None
    if across:
        lines = []
        for li, r in enumerate(p["rows"]):
            vals = [v for v in (M.value(r[j]) for j in ids if j < len(r)) if v not in ("", "-")]
            if vals and sum(isinstance(v, (int, float)) for v in vals) >= 0.5 * len(vals) and str(r[lc]).strip():
                lines.append(li)
                meta[str(li)] = kind_of(str(r[lc]))
        if not lines:
            return None, "a table of cities across the top with no row of figures"
        tc = next((j for j, h in enumerate(p["columns"]) if j not in ids and j > 0 and TOTAL.search(str(h).strip())), None)
        cols = lines
    else:
        cols = []
        for j, c in enumerate(p["columns"]):
            if j == lc:
                continue
            vals = [v for v in (M.value(p["rows"][ri][j]) for ri in ids if j < len(p["rows"][ri])) if v not in ("", "-")]
            if vals and sum(isinstance(v, (int, float)) for v in vals) >= 0.5 * len(vals):
                cols.append(j)
                meta[str(j)] = kind_of(str(c))
        if not cols:
            return None, "a table of cities with no column of figures"
        total = next((ri for ri, r in enumerate(p["rows"]) if ri not in ids and len(r) > lc and TOTAL.search(str(r[lc]).strip())), None)
        # the same places printed again in a second block below (the first place reappears, most of the others too)
        first = ids[min(ids)]
        starts = [ri for ri in sorted(ids) if ids[ri] == first]
        if len(starts) > 1:
            bounds = starts + [len(p["rows"])]
            B = [[bounds[k], bounds[k + 1]] for k in range(len(starts))]
            sets = [{ids[ri] for ri in ids if a <= ri < z} for a, z in B]
            if all(len(x & sets[0]) >= 0.5 * len(sets[0]) for x in sets[1:]):
                B[0][0] = 0
                blocks = B
    y = era_year(p.get("label")) or year_of(book, t)
    names = [str(p["rows"][li][lc]) for li in cols] if across else [str(p["columns"][j]) for j in cols]
    years = [int(YEAR.match(x).group(1)) if YEAR.match(x) else None for x in names]
    default = years.index(max(v for v in years if v)) if all(years) and len(cols) > 1 else 0
    e = {"book": book, "table": tid, "units": UNITS[unit], "part": pi, "label_col": lc, "default": default, "date": y,
         "period": "1930" if y and int(y) < 1938 else "1942", "col_meta": meta, "ids": {str(k): v for k, v in ids.items()}}
    # Taiwan's prefectures were redrawn again and again (1895–1920), so tables by them are not linked (user,
    # 2026-11-06): neither the 州・廳 of 1920 nor the earlier 縣・廳, which would otherwise pass as their seats' towns.
    if unit in ("taiwan-shu", "taiwan-gun"):
        return None, "a table of Taiwan's prefectures or districts: not linked (their boundaries changed too often)"
    if unit == "cities" and book.startswith("taiwan") and y and int(y) < 1920:
        return None, "a table of Taiwan's prefectures of the time (縣・廳), not of towns: not linked"
    if across:
        e.update({"across": True, "lines": cols, **({"total_col": tc} if tc is not None else {})})
    else:
        e.update({"columns": cols, **({"total_row": total} if total is not None else {}), **({"blocks": blocks} if blocks else {})})
    return e, f"{n} {UNITS[unit]}, part {pi}, {'across the top' if across else 'down column %d' % lc}, {len(cols)} measures"


def territory_entry(book, tid, t):
    """A small table of the empire's parts (内地, 朝鮮, 臺灣, 樺太 …), down the side or across the top: an entry in
    the hand-written territory form (maplinks.build_territory), each printed line or column a column of its own."""
    best = None
    for pi, p in enumerate(t.get("parts") or []):
        heads = p.get("columns") or []
        across = [j for j, h in enumerate(heads) if j and M.match_territory(h)]
        down = [ri for ri, r in enumerate(p["rows"]) if r and M.match_territory(r[0])]
        for kind, hit in (("across", across), ("down", down)):
            if len({M.match_territory(heads[j] if kind == "across" else p["rows"][j][0]) for j in hit}) >= 3 and (best is None or len(hit) > best[2]):
                best = (pi, kind, len(hit))
    if not best:
        return None, "nor a set of the map's cities, provinces or the empire's parts"
    pi, kind, n = best
    p = t["parts"][pi]
    title_rate = bool(RATE.search(t.get("title") or ""))
    def meta(name):
        k = "rate" if RATE.search(name) or title_rate else "index" if INDEX.search(name) else "amount" if AMOUNT.search(name) else "count"
        return {"unit": "", "kind": k, "color": "seq"}
    cols = []
    if kind == "across":
        for li, r in enumerate(p["rows"]):
            vals = [M.value(r[j]) for j, h in enumerate(p["columns"]) if j and M.match_territory(h) and j < len(r)]
            if r and str(r[0]).strip() and sum(isinstance(v, (int, float)) for v in vals) >= 0.5 * max(1, len(vals)):
                cols.append({"part": pi, "line": li, "name": str(r[0]).strip(), **meta(str(r[0]))})
    else:
        for j, h in enumerate(p["columns"]):
            if j == 0:
                continue
            vals = [M.value(r[j]) for r in p["rows"] if r and M.match_territory(r[0]) and j < len(r)]
            if sum(isinstance(v, (int, float)) for v in vals) >= 0.5 * max(1, len(vals)):
                cols.append({"part": pi, "line": j, "name": str(h).strip(), **meta(str(h))})
    if not cols:
        return None, "a table of the empire's parts with no figures"
    if kind == "down":
        from collections import Counter
        rep_ = Counter(M.match_territory(r[0]) for r in p["rows"] if r and M.match_territory(r[0]))
        if max(rep_.values()) > 1:
            # each part printed once a year: the column of years splits the measures (one column per measure and year)
            yc = next((j for j in range(1, len(p["columns"])) if sum(1 for r in p["rows"] if len(r) > j and YEAR.match(str(r[j]))) >= 0.6 * len(p["rows"])), None)
            if yc is None:
                return None, "the empire's parts repeat with no column of years to tell the rows apart"
            yrs = list(dict.fromkeys(M.FOOTMARK.sub("", str(r[yc])).strip() for r in p["rows"] if len(r) > yc and YEAR.match(str(r[yc]))))
            cols = [dict(c, name=f"{c['name']} — {y_}", when=y_, series=c["name"], date=y_[:4])
                    for c in cols if c["line"] != yc for y_ in yrs]
            extra = {"split_col": yc}
        else:
            extra = {}
    else:
        extra = {}
    labels = [str(h).strip() for h in p["columns"]] if kind == "across" else [str(r[0]).strip() for r in p["rows"] if r]
    tot = next((l for l in labels if re.match(r"^(帝國|總數|合計|總計|全國|Total|Empire)$", l)), None)
    y = era_year(p.get("label")) or year_of(book, t)
    e = {"book": book, "table": tid, "units": "territory", "label_col": 0, "cols": cols, "default": 0, "date": y,
         "period": "1930" if y and int(y) < 1938 else "1942", **({"across": True} if kind == "across" else {}),
         **({"total": {"label": tot, "en": "Empire" if tot == "帝國" else "Total"}} if tot else {}), **extra}
    return e, f"{n} parts of the empire, {kind}, {len(cols)} measures"


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
