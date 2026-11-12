"""maplinks.py — "Show on map" links for a small allow-list of tables (spec: build/MAPLINK_SPEC.md).

build/maplinks.json lists the tables that get a link; build_site.py calls map_url(book, table, translation) for
each table and stores the result as the table's "map" field. The payload is JSON, compressed with raw deflate and
base64url-encoded, in the URL fragment (#t=…) so that no server sees or limits it.
"""
import base64, json, os, re, unicodedata, zlib

HERE = os.path.dirname(os.path.abspath(__file__))
# Two copies of each site: the live one on froginawell.net and a draft on GitHub Pages. Links are built for the live
# copies; the table page swaps the map base for the GitHub one when it is itself on github.io (see build_site.py), and
# the map is expected to join src.path to the tables site on its own host (MAPLINK_SPEC.md, section 1).
HOSTS = {"live": {"tables": "https://froginawell.net/reference/old-tables/", "map": "https://froginawell.net/reference/japanese-empire/"},
         "gh": {"tables": "https://kmlawson.github.io/playground-stat-tables/", "map": "https://kmlawson.github.io/japanese-empire-student-map/"}}
SITE = HOSTS["live"]["tables"]
MAP = HOSTS["live"]["map"]
# named map views (query parameters): where = west,south,east,north in degrees
VIEWS = {"japan": {"where": "125.41,21.53,147.92,48.77", "layers": "2w"},
         "china": {"where": "73.5,17.5,135.5,53.8", "layers": "2w"},
         "korea": {"where": "123.8,33.0,131.2,43.2", "layers": "2w"},
         "taiwan": {"where": "119.2,21.8,122.3,25.4", "layers": "2w"},
         "manchuria": {"where": "114.0,38.2,135.5,53.6", "layers": "2w"},
         "south-seas": {"where": "130.0,0.0,173.5,21.5", "layers": "2w"},
         "empire": {"where": "112.0,0.0,175.0,51.0", "layers": "2w"},
         "asia": {"where": "60.0,-12.0,180.0,60.0", "layers": "2w"}}
UNIT_VIEW = {"china-province": "china", "korea-province": "korea", "manchukuo-province": "manchuria",
             "taiwan-prefecture": "taiwan", "taiwan-district": "taiwan", "nanyo-group": "south-seas",
             "territory": "empire", "country": "asia"}


def view_for(book, cfg):
    """The map view a link opens on: the entry's own "view", else the kind of place it carries, else (cities,
    prefectures) the region of the volume it comes from."""
    if cfg.get("view"):
        return cfg["view"]
    u = cfg.get("units")
    if u in UNIT_VIEW:
        return UNIT_VIEW[u]
    if u == "city":
        slug = book["slug"]
        for pre, v in (("china", "china"), ("korea", "korea"), ("taiwan", "taiwan"), ("manch", "manchuria"),
                       ("japan-manchoukuo", "manchuria"), ("nanyo", "south-seas"), ("mandate", "south-seas"),
                       ("gyosei", "south-seas"), ("far-east", "asia"), ("pacific", "asia")):
            if slug.startswith(pre):
                return v
    return "japan"
SUFFIX = re.compile(r"(府|縣|県|廳|庁|道|都|\s*prefecture|[-\s](?:fu|ken|cho|chō|do|dō))$", re.I)
VARCH = str.maketrans({"靑": "青", "縣": "県", "廣": "広", "靜": "静", "德": "徳", "兒": "児", "繩": "縄", "臺": "台", "灣": "湾",
                       "關": "関", "廳": "庁", "櫔": "栃", "杤": "栃"})


MARKS = re.compile(r"[*＊※†‡△▲×○◎]|\s*[(（]\s*\d+\s*[)）]\s*$|[.。]+$")


def _fold(s, keep=0):
    """keep: never strip a suffix that would leave fewer characters than this. The prefecture matcher leaves it 0
    (its index is built the same way); the gazetteer matcher of build_candidates passes 2, so that a two-character
    name ending in a suffix character stays whole (成都, 沙市, 萬縣, 江都 are towns, not 成, 沙, 萬, 江)."""
    s = unicodedata.normalize("NFKC", str(s)).strip()
    s = "".join(c for c in unicodedata.normalize("NFKD", s) if not unicodedata.combining(c))   # Tōkyō -> Tokyo
    s = MARKS.sub("", MARKS.sub("", s)).strip().translate(VARCH).lower()
    s = re.sub(r"^\d{1,2}\s+(?=\D)", "", s)   # a numbered row: "1 北海道" (統計年鑑)
    for _ in range(2):
        t = SUFFIX.sub("", s).strip()
        if len(re.sub(r"\s+", "", t)) < keep:
            break
        s = t
    return re.sub(r"\s+", "", s)


_INDEX = None
BOOK_TABLES = {}   # id -> table of the book being built, for "also" (set by build_site.add_maplinks)


def place_index():
    """{folded name: id} from build/places/japan_prefectures.json."""
    global _INDEX
    if _INDEX is None:
        P = json.load(open(os.path.join(HERE, "places", "japan_prefectures.json")))["places"]
        _INDEX = {}
        for pid, p in P.items():
            for name in [p["ja"], p["en"], *p.get("variants", [])]:
                _INDEX.setdefault(_fold(name), pid)
            _INDEX.setdefault(_fold(p["en"].split(" (")[0]), pid)
    return _INDEX


def match_place(label):
    return place_index().get(_fold(label))


NUM = re.compile(r"^[-−]?[\d,]*\.?\d+$")


def value(cell):
    """A printed cell as a map value: a number, or one of the codes "?" (unreadable), "" (blank in the original),
    "-" (printed dash), or the printed text itself when it is not a plain figure."""
    c = str(cell).strip()
    if c == "[?]":
        return "?"
    if c == "":
        return ""
    if c in ("—", "-", "–", "―", "－", "…", "‥"):
        return "-"
    t = c.replace(",", "").replace("−", "-")
    if NUM.match(c):
        f = float(t)
        return int(f) if f.is_integer() and "." not in t else f
    return c


def load_config():
    f = os.path.join(HERE, "maplinks.json")
    return json.load(open(f)) if os.path.exists(f) else {"tables": []}


def encode(payload):
    raw = json.dumps(payload, ensure_ascii=False, separators=(",", ":")).encode()
    co = zlib.compressobj(9, zlib.DEFLATED, -15)   # raw deflate = DecompressionStream("deflate-raw")
    return base64.urlsafe_b64encode(co.compress(raw) + co.flush()).decode().rstrip("=")


TERR = [("關東州", "kwantung"), ("関東州", "kwantung"), ("南洋", "nanyo"), ("內地", "naichi"), ("内地", "naichi"),
        ("朝鮮", "chosen"), ("臺灣", "taiwan"), ("台湾", "taiwan"), ("樺太", "karafuto"),
        # English year books (Far East Year Book, Pacific survey): "Japan" alone is left out, as it may be the empire
        ("Japan Proper", "naichi"), ("Chosen", "chosen"), ("Korea", "chosen"), ("Taiwan", "taiwan"), ("Formosa", "taiwan"),
        ("Karafuto", "karafuto"), ("Saghalien", "karafuto"), ("Kwantung", "kwantung"), ("Nanyo", "nanyo"),
        ("South Sea", "nanyo"), ("South Seas", "nanyo")]
FOOTMARK = re.compile(r"[*＊※†‡]")


def match_territory(label):
    """A part of the empire from a printed label (marks and a parenthesis after it ignored): naichi, chosen, …"""
    l = re.sub(r"\s*[(（].*$", "", FOOTMARK.sub("", str(label))).strip()
    if l in ("道府縣", "道府県"):   # beside 樺太, 朝鮮, 臺灣 (建築年鑑 1941, 木材需給): the prefectures, Japan proper
        return "naichi"
    return next((pid for k, pid in TERR if l.startswith(k)), None)


def clean_label(label):
    return re.sub(r"\s*[(（].*$", "", FOOTMARK.sub("", str(label))).strip()


def tvalue(cell):
    """value(), with footnote marks taken off the figure ("* 163.1" -> 163.1); their meaning is in the notes."""
    return value(FOOTMARK.sub("", str(cell)).strip())


def build_territory(book, t, tr, cfg):
    """A table of the empire's parts (spec additions in interactive-japan-map docs/table-links.md): one row per
    territory, each sent column given by hand in maplinks.json as {"part", "line", name, en, kind, unit, color,
    series, date}. "across": true when the printed table has the territories across the top, so that "line" is the
    printed row that becomes the column; otherwise the territories run down "label_col" and "line" is a printed
    column. "total": {"label", "en"} names the printed whole (a column when across, a row otherwise)."""
    lab = cfg.get("label_col", 0)
    tot = cfg.get("total") or {}
    places, tvals = {}, []
    for k, c in enumerate(cfg["cols"]):
        part = t["parts"][c.get("part", 0)]
        if cfg.get("across"):
            r = part["rows"][c["line"]]
            for j, h in enumerate(part["columns"]):
                pid = match_territory(h)
                if pid:
                    places.setdefault(pid, {"id": pid, "label": clean_label(h), "row": j, "v": [""] * len(cfg["cols"])})
                    places[pid]["v"][k] = tvalue(r[j]) if j < len(r) else ""
                elif tot and clean_label(h) == tot["label"]:
                    tvals.append(tvalue(r[j]) if j < len(r) else "")
        else:
            got = False
            sc = cfg.get("split_col")   # a place printed on several rows, told apart by this column (a year)
            for ri, r in enumerate(part["rows"]):
                pid = match_territory(r[lab])
                if pid and (sc is None or FOOTMARK.sub("", str(r[sc])).strip() == c.get("when")):
                    places.setdefault(pid, {"id": pid, "label": clean_label(r[lab]), "row": ri, "v": [""] * len(cfg["cols"])})
                    if places[pid]["v"][k] == "":
                        places[pid]["v"][k] = tvalue(r[c["line"]]) if c["line"] < len(r) else ""
                elif tot and clean_label(r[lab]) == tot["label"] and not got and (
                        sc is None or FOOTMARK.sub("", str(r[sc])).strip() == c.get("when")):
                    tvals.append(tvalue(r[c["line"]])); got = True
    rows = list(places.values())
    total = None
    if tot and len(tvals) == len(cfg["cols"]):
        total = {"label": tot["label"], "en": tot.get("en"), "v": tvals}
        for k, c in enumerate(cfg["cols"]):
            nums = [x["v"][k] for x in rows if isinstance(x["v"][k], (int, float))]
            if c.get("kind") in ("count", "amount") and nums and isinstance(tvals[k], (int, float)):
                sm = round(sum(nums), 6)
                if abs(sm - tvals[k]) > 1e-6:
                    total.setdefault("mismatch", {})[str(k)] = sm
    title_en = (tr or {}).get("t")
    keys = ("name", "en", "unit", "kind", "color", "series", "date")
    p = {
        "v": 1,
        "src": {"url": f"{SITE}book/{book['slug']}/#{t['id']}", "path": f"book/{book['slug']}/#{t['id']}",
                "book": book["slug"], "table": t["id"]},
        "title": {"ja": t.get("title", ""), **({"en": title_en} if title_en else {})},
        "volume": {"title": book["title"], "year": cfg.get("volume_year") or book.get("_year"),
                   **({"en": book["subtitle"]} if book.get("subtitle") else {})},
        "date": cfg.get("date"),
        "period": cfg.get("period"),
        "part": None,
        "units": "territory",
        "cols": [{k: c[k] for k in keys if c.get(k) is not None} for c in cfg["cols"]],
        "def": cfg.get("default", 0),
        "rows": rows,
        "total": total,
        "notes": cfg.get("notes") or [],
    }
    return p, []


# rows that are not places at all (years, ditto marks, totals, averages) are not "unplaced"; a leading mark
# (◇合計, ※計) is not part of the label
NOT_PLACE = re.compile('^[\\s\u25c7\u25c6\u25cb\u25cf\u203b*]*([\u3003\u2033\u201e",]+|同\\s*\\d|明治|大正|昭和|民國|Year|\\d{4}\\b|\\d+\\s*$|計$|合計|總數|總計|總額|総額|平均|Total|Grand Total|Average|Others?$)')


def build_city(book, t, tr, cfg):
    """A table of cities (units "city", MAPLINK_SPEC 4b). The ids are the map's own city ids, matched when the entry
    was written (maplinks_add.py, from the map's gazetteer) and stored in the entry, so this build needs no map
    checkout. Down the side: "ids" {printed row: id}, "columns" the printed columns sent. Across the top ("across"):
    "ids" {printed column: id}, "lines" the printed rows sent, each becoming a column."""
    part = t["parts"][cfg.get("part", 0)]
    lab = cfg.get("label_col", 0)
    ids = {int(k): v for k, v in cfg["ids"].items()}
    if not cfg.get("blocks") and cfg.get("split_col") is None and not cfg.get("measures") and len(set(ids.values())) < len(ids):
        # A place on two rows: only the first would be drawn, as if it were the whole (醫療機關表 sent its 內 row of
        # 內/鮮/外/計; a table of school kinds sent its first kind). Usually it is harmless (a city printed twice,
        # once with its wards), so the build says so rather than refusing: about a hundred entries do it.
        twice = sorted({v for v in ids.values() if list(ids.values()).count(v) > 1})
        print(f"maplinks: {book['slug']}:{t['id']}: places on more than one row, only the first drawn "
              f"({', '.join(twice[:6])}); if the rows are parts of a whole, pick the rows in ids or use blocks or split_col")
    meta = cfg.get("col_meta", {})
    rows, seen, unplaced, total = [], set(), [], None
    if cfg.get("across") and cfg.get("measures"):
        # each place printed over several columns, one per measure ("南京 — 件數", "南京 — 價值 (元)", "南京 — 面積"):
        # one column per measure and printed row, the measure as its series, so that no measure is dropped
        lines = cfg["lines"]
        by = {}
        for j in sorted(ids):
            by.setdefault(ids[j], []).append(j)
        k = max(len(v) for v in by.values())
        first = next(v for v in by.values() if len(v) == k)
        mnames = [re.split(r"\s+[—–]\s+", str(part["columns"][j]).strip(), maxsplit=1)[-1] for j in first]
        cols = [dict({"name": f"{str(part['rows'][li][lab]).strip()} — {m}", "series": m}, **meta.get(str(li), {}))
                for m in mnames for li in lines]
        for pid, js in by.items():
            vals = []
            for n in range(k):
                j = js[n] if n < len(js) else None
                vals += [value(part["rows"][li][j]) if j is not None and j < len(part["rows"][li]) else "" for li in lines]
            rows.append({"id": pid, "label": re.split(r"\s+[—–]\s+", str(part["columns"][js[0]]).strip())[0], "row": js[0], "v": vals})
        for j, h in enumerate(part["columns"]):
            if j != lab and j not in ids and cfg.get("total_col") != j and str(h).strip():
                if any(isinstance(value(part["rows"][li][j]) if j < len(part["rows"][li]) else "", (int, float)) for li in lines):
                    unplaced.append(str(h).strip())
    elif cfg.get("across"):
        lines = cfg["lines"]
        cols = [dict({"name": str(part["rows"][li][lab]).strip()}, **meta.get(str(li), {})) for li in lines]
        for j, h in enumerate(part["columns"]):
            if j == lab:
                continue
            vals = [value(part["rows"][li][j]) if j < len(part["rows"][li]) else "" for li in lines]
            if j in ids and ids[j] not in seen:
                seen.add(ids[j])
                rows.append({"id": ids[j], "label": str(h).strip(), "row": j, "v": vals})
            elif cfg.get("total_col") == j:
                total = {"label": str(h).strip(), "v": vals}
            elif str(h).strip() and any(isinstance(v, (int, float)) for v in vals):
                unplaced.append(str(h).strip())
    elif cfg.get("split_col") is not None:
        # each place printed on several rows told apart by a column (男 / 女): one column per measure and value
        sc, use = cfg["split_col"], cfg["columns"]
        svals = list(dict.fromkeys(str(r[sc]).strip() for ri, r in enumerate(part["rows"]) if ri in ids and len(r) > sc))
        if cfg.get("split_first") in svals:   # the whole (計) first, so the map opens on it rather than on one part
            svals.remove(cfg["split_first"]); svals.insert(0, cfg["split_first"])
        cols = [dict({"name": f"{part['columns'][j]} — {sv}"}, **meta.get(str(j), {})) for sv in svals for j in use]
        by = {}
        for ri, r in enumerate(part["rows"]):
            if ri not in ids:
                continue
            x = by.setdefault(ids[ri], {"id": ids[ri], "label": str(r[lab]).strip(), "row": ri, "v": [""] * len(cols)})
            k = svals.index(str(r[sc]).strip())
            for n, j in enumerate(use):
                x["v"][k * len(use) + n] = value(r[j]) if j < len(r) else ""
        rows = list(by.values())
    elif cfg.get("blocks"):
        # the places printed again further down (a second block of rows, with its own total): one set of columns
        # per block, "(block 2)" and so on, so that no block's figures are dropped; or named by "block_names" when
        # the table heads each block (one block per kind of school)
        use, B, BN = cfg["columns"], cfg["blocks"], cfg.get("block_names")
        cols = [dict({"name": part["columns"][j] + (f" ({BN[b]})" if BN else f" (block {b + 1})" if b else "")}, **meta.get(str(j), {}))
                for b in range(len(B)) for j in use]
        by = {}
        for b, (a, z) in enumerate(B):
            for ri in range(a, z):
                r = part["rows"][ri]
                if ri not in ids:
                    label = str(r[lab]).strip() if len(r) > lab else ""
                    if b == 0 and label and any(isinstance(value(r[j]), (int, float)) for j in use if j < len(r)) \
                            and not (cfg.get("total_row") == ri):
                        unplaced.append(label)
                    continue
                x = by.setdefault(ids[ri], {"id": ids[ri], "label": str(r[lab]).strip(), "row": ri, "v": [""] * len(cols)})
                for n, j in enumerate(use):
                    k = b * len(use) + n
                    if x["v"][k] == "":
                        x["v"][k] = value(r[j]) if j < len(r) else ""
        rows = list(by.values())
    else:
        use = cfg["columns"]
        cols = [dict({"name": part["columns"][j]}, **meta.get(str(j), {})) for j in use]
        for ri, r in enumerate(part["rows"]):
            label = str(r[lab]).strip() if len(r) > lab else ""
            vals = [value(r[j]) if j < len(r) else "" for j in use]
            if ri in ids and ids[ri] not in seen:
                seen.add(ids[ri])
                rows.append({"id": ids[ri], "label": label, "row": ri, "v": vals})
            elif cfg.get("total_row") == ri:
                total = {"label": label, "row": ri, "v": vals}
            elif label and any(isinstance(v, (int, float)) for v in vals):
                unplaced.append(label)
    notes = list(cfg.get("notes") or [n for n in (t.get("footnotes") or [])][:3])
    if cfg.get("blocks") and cfg.get("block_names"):
        notes.insert(0, f"The table prints the places {len(cfg['blocks'])} times, once for each of: {', '.join(cfg['block_names'])}. "
                     "Each is a set of columns here.")
    elif cfg.get("blocks"):
        notes.insert(0, f"The table prints the places {len(cfg['blocks'])} times, in blocks one under another; each block is a set of "
                     "columns here, (block 2) and so on. See the scan for what each block counts.")
    if cfg.get("units") == "manchukuo-province":
        # The map draws the 14 provinces of 1934. A table naming one created later (Mutankiang, Tunghua 1937;
        # Peian; Tungan 1939; Szeping 1941) is from a different scheme: those rows are left off, and the note says so.
        later = [u for u in unplaced if re.match(r"(?i)\s*(mutan|tunghua|peian|pei-an|tungan|tung-an|szeping|ssuping|牡丹江|通化|北安|東安|四平)", u)]
        if later:
            notes.insert(0, "Left off: " + ", ".join(dict.fromkeys(later)) + ", provinces created after the map's 1934 boundaries; "
                         "the provinces they were cut from are drawn with their 1934 outlines.")
    if cfg.get("units") == "china-province":
        # 統計提要 1947: the nine provinces the Northeast was divided into in 1945; 遼寧, 吉林 and 黑龍江 keep their names
        # but not their 1930s outlines, which the map draws
        later = [u for u in unplaced if re.match(r"\s*(安東|遼北|松江|合江|嫩江|興安)\s+[A-Z]", u)]
        if later:
            notes.insert(0, "Left off: " + ", ".join(dict.fromkeys(later)) + ", provinces of the 1945 division of the Northeast; "
                         "遼寧, 吉林 and 黑龍江 are drawn with their larger 1930s outlines.")
    title_en = (tr or {}).get("t")
    p = {
        "v": 1,
        "src": {"url": f"{SITE}book/{book['slug']}/#{t['id']}", "path": f"book/{book['slug']}/#{t['id']}",
                "book": book["slug"], "table": t["id"]},
        "title": {"ja": t.get("title", ""), **({"en": title_en} if title_en else {})},
        "volume": {"title": book["title"], "year": cfg.get("volume_year") or book.get("_year"),
                   **({"en": book["subtitle"]} if book.get("subtitle") else {})},
        "date": cfg.get("date"),
        "period": cfg.get("period"),
        "part": part.get("label") or None,
        "units": cfg.get("units", "city"),
        "cols": cols,
        "def": cfg.get("default", 0),
        "rows": rows,
        "total": total,
        # rows that are not places at all (years, ditto marks, 計) are not "unplaced"
        "unplaced": [u for u in unplaced if not NOT_PLACE.match(u)][:80],
        "notes": notes,
    }
    return p, []


def build_payload(book, t, tr, cfg):
    """The v1 payload for one table and its maplinks.json entry (see MAPLINK_SPEC.md)."""
    if cfg.get("units") == "territory":
        return build_territory(book, t, tr, cfg)
    if cfg.get("units") not in (None, "prefecture") or cfg.get("across") or cfg.get("split_col") is not None:
        return build_city(book, t, tr, cfg)   # city, china-province, korea-province … (keyed by the map's ids)
    part = t["parts"][cfg.get("part", 0)]
    cols = part["columns"]
    lab = cfg.get("label_col", 0)
    use = cfg.get("columns") or [j for j in range(len(cols)) if j != lab]
    en_cols = cfg.get("en_columns", {})
    meta = cfg.get("col_meta", {})
    rows, total, unmatched = [], None, []
    for ri, r in enumerate(part["rows"]):
        label = str(r[lab]).strip()
        # "only_ids": the rows named in row_ids and no others (a list of schools under each prefecture, sent by its
        # 計 rows only, where every school row also names the prefecture)
        pid = cfg.get("row_ids", {}).get(str(ri)) or (None if cfg.get("only_ids") else match_place(label))
        vals = [value(r[j]) if j < len(r) else "" for j in use]
        if pid:
            rows.append({"id": pid, "label": label, "row": ri, "v": vals})
        elif cfg.get("total_row") is not None and ri == cfg["total_row"]:
            total = {"label": label, "row": ri, "v": vals}
        elif label and any(v not in ("", "-") for v in vals) and not cfg.get("only_ids"):
            unmatched.append(label)
    # A table printed over two pages and stored as two records: "also" names the other half(s), whose rows
    # (same part, label column and column positions) join the first's. BOOK_TABLES is set by build_site.
    for ex in cfg.get("also", []):
        ot = BOOK_TABLES.get(ex["table"])
        if not ot:
            print(f"maplinks: {book['slug']}:{t['id']} also-table {ex['table']} not found")
            continue
        olab = ex.get("label_col", lab)
        ouse = ex.get("columns") or use   # a block printed beside the first: its own columns, in the same order
        for ri, r in enumerate(ot["parts"][ex.get("part", 0)]["rows"]):
            label = str(r[olab]).strip() if len(r) > olab else ""
            pid = ex.get("row_ids", {}).get(str(ri)) or match_place(label) or (
                match_place(re.split(r"\s*[—–]\s*", label)[0]) if re.search(r"[—–]", label) else None)
            vals = [value(r[j]) if j < len(r) else "" for j in ouse]
            if pid and not any(x["id"] == pid for x in rows):
                rows.append({"id": pid, "label": label, "row": ri, "table": ex["table"], "v": vals})
    # "1.396" among whole numbers in a count column: a thousands point as printed (1,396), not a decimal. Sent as
    # the printed text, which the map shows without colouring, rather than as 1.4.
    for k, j in enumerate(use):
        if meta.get(str(j), {}).get("kind", "count") not in ("count", "amount"):
            continue
        col = [x["v"][k] for x in rows]
        if sum(isinstance(v, int) for v in col) >= 0.8 * len(col):
            for x in rows:
                v = x["v"][k]
                if isinstance(v, float):
                    raw = "" if x.get("table") else str(part["rows"][x["row"]][j])   # rows of this part only
                    if re.fullmatch(r"\d{1,3}\.\d{3}", raw.strip()):
                        x["v"][k] = raw.strip()
    if cfg.get("total_row") is not None and total and cfg.get("check_total", True):
        for k in range(len(use)):
            nums = [x["v"][k] for x in rows]
            if all(isinstance(n, (int, float)) for n in nums) and isinstance(total["v"][k], (int, float)):
                s = round(sum(nums), 6)
                if abs(s - total["v"][k]) > 1e-6:
                    total.setdefault("mismatch", {})[str(k)] = s
    title_en = (tr or {}).get("t")
    p = {
        "v": 1,
        "src": {"url": f"{SITE}book/{book['slug']}/#{t['id']}", "path": f"book/{book['slug']}/#{t['id']}",
                "book": book["slug"], "table": t["id"]},
        "title": {"ja": t.get("title", ""), **({"en": title_en} if title_en else {})},
        "volume": {"title": book["title"], "year": cfg.get("volume_year") or book.get("_year"),
                   **({"en": book["subtitle"]} if book.get("subtitle") else {})},
        "date": cfg.get("date"),
        "period": cfg.get("period"),
        "part": part.get("label") or None,
        "units": "prefecture",
        "cols": [dict({"name": cols[j], **({"en": en_cols[str(j)]} if str(j) in en_cols else {})},
                      **{k: v for k, v in meta.get(str(j), {}).items()}) for j in use],
        "def": cfg.get("default", 0),
        "rows": rows,
        "total": total,
        "notes": cfg.get("notes") or [n for n in (t.get("footnotes") or [])][:3],
    }
    return p, unmatched


def apply_mult(p, cfg):
    """Columns printed in thousands (千圓, Unit: 1,000) or millions are sent as full numbers: the entry's "mult"
    {payload column index: factor} (decided per column, build/maplinks_units/) multiplies that column's figures, so
    the map shows 72,223,000 rather than 72,223 for a population printed in thousands. Printed text that is not a
    number (a thousands point kept as text, "-") is sent unchanged."""
    m = {int(k): v for k, v in (cfg.get("mult") or {}).items() if v and v != 1}
    if not m:
        return
    def scale(v, f):
        if isinstance(v, bool) or not isinstance(v, (int, float)) or f == 1:
            return v
        r = v * f
        return int(round(r)) if abs(r - round(r)) < 1e-6 else round(r, 6)
    for row in p.get("rows") or []:
        row["v"] = [scale(v, m.get(k, 1)) for k, v in enumerate(row["v"])]
    tot = p.get("total")
    if tot:
        tot["v"] = [scale(v, m.get(k, 1)) for k, v in enumerate(tot["v"])]
        if tot.get("mismatch"):
            tot["mismatch"] = {k: scale(v, m.get(int(k), 1)) for k, v in tot["mismatch"].items()}
    names = []
    for k, f in sorted(m.items()):
        if k < len(p["cols"]):
            p["cols"][k]["printed_x"] = f        # informational: the factor the printed figures were multiplied by
            names.append(p["cols"][k].get("en") or p["cols"][k].get("name") or str(k))
    word = {1000: "thousands", 10000: "ten thousands (萬)", 1000000: "millions"}
    fs = sorted(set(m.values()))
    unit = " and ".join(word.get(f, f"units of {f:,}") for f in fs)
    p["notes"] = [(f"Printed in {unit}; shown here as full numbers." if len(names) == len(p["cols"])
                   else f"The columns printed in {unit} are shown here as full numbers.")] + list(p.get("notes") or [])


def map_url(book, t, tr=None, cfg_all=None):
    cfg_all = cfg_all or load_config()
    for cfg in cfg_all.get("tables", []):
        if cfg.get("book") == book["slug"] and cfg.get("table") == t["id"]:
            try:
                p, unmatched = build_payload(book, t, tr, cfg)
            except ValueError as e:   # an entry that would draw the wrong figures: no link, and the build says why
                print(f"maplinks: NO LINK for {e}")
                return None
            apply_mult(p, cfg)
            if unmatched:
                print(f"maplinks: {book['slug']}:{t['id']} rows not matched to a place: {', '.join(unmatched[:12])}")
            view = VIEWS[view_for(book, cfg)]
            return f"{MAP}?where={view['where']}&layers={view['layers']}#t={encode(p)}"
    return None


def decode(url):
    """For testing: the payload back from a map URL."""
    frag = url.split("#t=", 1)[1]
    z = base64.urlsafe_b64decode(frag + "=" * (-len(frag) % 4))
    return json.loads(zlib.decompress(z, -15))


if __name__ == "__main__":
    import sys
    if "--list" in sys.argv:   # print the current map URL of every allow-listed table (from the built data/*.json)
        site = os.path.dirname(HERE)
        for c in load_config().get("tables", []):
            d = json.load(open(os.path.join(site, "data", c["book"] + ".json")))
            ts = d if isinstance(d, list) else d.get("tables", [])
            t = next((x for x in ts if x.get("id") == c["table"]), None)
            print(f"{c['book']}:{c['table']}\t{(t or {}).get('map') or '(no link: rebuild the site)'}")
    if "--audit" in sys.argv:
        # Row labels that look like prefecture names but do not match, in tables where >= 8 prefectures already match.
        # Run after adding books: add real variants to build/places/japan_prefectures.json, ignore totals and cities.
        import collections, glob
        only = [a for a in sys.argv[1:] if not a.startswith("--")]
        site = os.path.dirname(HERE); miss = collections.Counter(); where = {}
        for f in glob.glob(os.path.join(site, "data", "*.json")):
            slug = os.path.basename(f)[:-5]
            if slug.endswith(("-toc", "-directory", "-chronology")) or (only and slug not in only):
                continue
            try:
                d = json.load(open(f))
            except Exception:
                continue
            for t in (d if isinstance(d, list) else d.get("tables", [])):
                for p in (t.get("parts") or []) if isinstance(t, dict) else []:
                    labs = [str(r[0]).strip() for r in p.get("rows", []) if r]
                    if len({match_place(l) for l in labs} - {None}) < 8:
                        continue
                    for l in labs:
                        if l and not match_place(l) and "／" not in l and not re.search(r"郡部|市$|City|Total|計|總|合|Average|Circuit|不明|Others?$", l):
                            miss[l] += 1; where.setdefault(l, f"{slug}:{t.get('id')}")
        for l, c in miss.most_common(200):
            print(f"{c:5}  {l!r:40} {where[l]}")
