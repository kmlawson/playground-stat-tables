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
VIEWS = {"japan": {"where": "125.41,21.53,147.92,48.77", "layers": "2w"}}   # named map views (query parameters)
SUFFIX = re.compile(r"(府|縣|県|廳|庁|道|都|\s*prefecture|[-\s](?:fu|ken|cho|chō|do|dō))$", re.I)
VARCH = str.maketrans({"縣": "県", "廣": "広", "靜": "静", "德": "徳", "兒": "児", "繩": "縄", "臺": "台", "灣": "湾",
                       "關": "関", "廳": "庁", "櫔": "栃", "杤": "栃"})


MARKS = re.compile(r"[*＊※†‡]|\s*[(（]\s*\d+\s*[)）]\s*$|[.。]+$")


def _fold(s):
    s = unicodedata.normalize("NFKC", str(s)).strip()
    s = "".join(c for c in unicodedata.normalize("NFKD", s) if not unicodedata.combining(c))   # Tōkyō -> Tokyo
    s = MARKS.sub("", MARKS.sub("", s)).strip().translate(VARCH).lower()
    for _ in range(2):
        s = SUFFIX.sub("", s).strip()
    return re.sub(r"\s+", "", s)


_INDEX = None


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


def build_payload(book, t, tr, cfg):
    """The v1 payload for one table and its maplinks.json entry (see MAPLINK_SPEC.md)."""
    part = t["parts"][cfg.get("part", 0)]
    cols = part["columns"]
    lab = cfg.get("label_col", 0)
    use = cfg.get("columns") or [j for j in range(len(cols)) if j != lab]
    en_cols = cfg.get("en_columns", {})
    meta = cfg.get("col_meta", {})
    rows, total, unmatched = [], None, []
    for ri, r in enumerate(part["rows"]):
        label = str(r[lab]).strip()
        pid = cfg.get("row_ids", {}).get(str(ri)) or match_place(label)
        vals = [value(r[j]) if j < len(r) else "" for j in use]
        if pid:
            rows.append({"id": pid, "label": label, "row": ri, "v": vals})
        elif cfg.get("total_row") is not None and ri == cfg["total_row"]:
            total = {"label": label, "row": ri, "v": vals}
        elif label and any(v not in ("", "-") for v in vals):
            unmatched.append(label)
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


def map_url(book, t, tr=None, cfg_all=None):
    cfg_all = cfg_all or load_config()
    for cfg in cfg_all.get("tables", []):
        if cfg.get("book") == book["slug"] and cfg.get("table") == t["id"]:
            p, unmatched = build_payload(book, t, tr, cfg)
            if unmatched:
                print(f"maplinks: {book['slug']}:{t['id']} rows not matched to a place: {', '.join(unmatched[:12])}")
            view = VIEWS[cfg.get("view", "japan")]
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
