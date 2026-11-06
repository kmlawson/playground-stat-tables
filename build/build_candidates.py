#!/usr/bin/env python3
"""Which tables in the Japan volumes of *Old Tables* could be drawn on this map.

Writes the "Map-link candidates" section of `support/candidates.html` in the tables site (served at
https://kmlawson.github.io/playground-stat-tables/support/). It
fills only the block between the two marker comments and leaves the rest of
the page alone, so sections added to that page by hand survive a rebuild.

    python3 build/build_candidates.py                   # this site, and the map at ~/shell/interactive-japan-map
    python3 build/build_candidates.py --map PATH        # the map repository somewhere else

**Where the tables come from.** The statistics site's own transcriptions,
`data/<slug>.json`, for every book whose slug begins `japan-`. Its
`build/maplinks.py` supplies the prefecture matcher, so "this matches 47
prefectures" here means what the site's "Show on map" link would accept.
Nothing in the site's repository is written.

**What the map can draw** comes from this repository: `texts/territories/`
for the countries, colonies and sub-units, `texts/city-names.csv` and
`data/cities-*.csv` for the cities, and the 1930 and 1942 station files for
the railway stations.

**The three kinds.**

1. *Prefecture map*: one part of a table names thirty or more of the 47
   prefectures down its first column, or across its headings. The site
   already knows how to send these.
2. *Cities*: six or more of the map's cities, at least three of them not also
   the name of a prefecture (Tokyo, Osaka and Kyoto are both), and cities make
   up at least half the rows.
3. *Other units the map draws*: Korean provinces, Taiwanese prefectures or
   districts, the provinces of Manchukuo or China, the South Seas groups, the
   colonies as whole rows, countries, railway stations, and the regional
   schemes. Only parts in a good or fair state are listed here, because the
   map has no matcher for these yet and a table worth writing one for is a
   table that reads cleanly. A set must name 40 per cent of the rows, except
   countries, where a trade table's Europe and America are rightly off the
   map. Stations count only where the table says it is of stations: their
   names are the names of towns, wards and police districts too.

Where several sets clear their bars, the one naming the largest share of the
rows wins.

**State.** `good`: at least 90 per cent of the figures in the matched rows
read as numbers and none is marked unreadable. `fair`: at least 60 per cent,
three or fewer unreadable. Anything else is `check`. A table carried over
onto the next page (`continued` in the data) is joined to the page before it
when the columns agree, since a prefecture table split at Kyōto matches
twenty-odd prefectures on each page and thirty on neither.

The thresholds are judgements, not facts. They are named at the top of the
code so that they can be argued with.
"""
import argparse
import ast
import csv
import glob
import html
import importlib.util
import json
import os
import re
import sys
import unicodedata
from collections import Counter, defaultdict
from datetime import datetime

HERE = os.path.dirname(os.path.abspath(__file__))
# the tables site (this repository) and the map whose place names say what can be drawn
DEFAULT_SITE = os.path.dirname(HERE)
OUT = os.path.join(DEFAULT_SITE, "support", "candidates.html")
ROOT = os.path.expanduser("~/shell/interactive-japan-map")
BOOK_URL = "https://kmlawson.github.io/playground-stat-tables/book/{slug}/#{id}"
BEGIN = "<!-- candidates:begin (written by support/build_candidates.py; edits inside are lost) -->"
END = "<!-- candidates:end -->"

MIN_PREFECTURES = 30
MIN_CITIES = 6
MIN_CITIES_NOT_PREF = 3
MIN_CITY_SHARE = 0.5
MIN_STATIONS_NOT_CITY = 15
MIN_STATION_SHARE = 0.6
MIN_OTHER_SHARE = 0.4               # of the rows, for every set but countries
GOOD_NUMERIC, FAIR_NUMERIC, FAIR_UNREADABLE = 0.9, 0.6, 3

# How many of a set's units a part must name, and how the set is described.
SETS = {
    "korea":     (9, "Korean provinces (道)"),
    "taiwan-shu": (5, "Taiwanese prefectures (州・廳)"),
    "taiwan-gun": (15, "Taiwanese cities and districts (市・郡)"),
    "manchukuo": (8, "Manchukuo provinces (省)"),
    "china":     (10, "Chinese provinces"),
    "mandate":   (4, "South Seas groups (南洋 支廳)"),
    "empire":    (3, "The colonies as whole rows"),
    "countries": (5, "Countries and territories"),
    "regions":   (6, "Regions of Japan"),
}

# Old forms the site's fold does not already cover, for names of cities,
# stations and provinces.
OLD = str.maketrans({
    "濱": "浜", "澤": "沢", "櫻": "桜", "龜": "亀", "豐": "豊", "戶": "戸", "瀨": "瀬", "姬": "姫",
    "吳": "呉", "國": "国", "會": "会", "嶋": "島", "邊": "辺", "藏": "蔵", "黑": "黒", "龍": "竜",
    "濟": "済", "營": "営", "對": "対", "佛": "仏", "滿": "満", "樂": "楽", "萬": "万", "寶": "宝",
    "鐵": "鉄", "與": "与", "來": "来", "兩": "両", "壽": "寿", "榮": "栄", "莊": "荘", "惠": "恵",
    "衞": "衛", "傳": "伝", "實": "実", "鹽": "塩", "驛": "駅", "舊": "旧", "淺": "浅", "峯": "峰",
    "髙": "高", "﨑": "崎", "嵜": "崎", "邉": "辺", "澁": "渋", "澀": "渋", "籠": "篭", "肅": "粛",
    "陜": "陝", "雲": "雲", "藝": "芸", "條": "条", "險": "険", "檜": "桧", "蠣": "蛎", "與": "与",
})
CITY_SUFFIX = re.compile(r"(市|區|区|府|町|驛|駅|[-\s]?(?:shi|city|machi|fu)|\s*station)$", re.I)
PROV_SUFFIX = re.compile(r"(省|州|廳|庁|道|[-\s]?(?:sho|shō|shu|shū|cho|chō|do|dō|province))$", re.I)
REGION_SUFFIX = re.compile(r"(地方|區|区|支部|部|道|[-\s]?(?:region|district|ku|chiho|chihō|do|dō))$", re.I)
EMPIRE_IDS = {"japan", "ryukyu", "ogasawara", "chishima", "chosen", "formosa", "karafuto", "kwantung",
              "nanyo", "mandate_jp"}


def load_module(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def books_of(site):
    """BOOKS from the site's build_site.py, read as a literal, not run."""
    src = open(os.path.join(site, "build", "build_site.py"), encoding="utf-8").read()
    for node in ast.parse(src).body:
        if isinstance(node, ast.Assign) and any(getattr(t, "id", "") == "BOOKS" for t in node.targets):
            out = []
            for el in node.value.elts:
                b = {}
                for k, v in zip(el.keys, el.values):
                    try:
                        b[ast.literal_eval(k)] = ast.literal_eval(v)
                    except ValueError:
                        pass            # a path worked out at run time; not needed here
                out.append(b)
            return out
    raise SystemExit("BOOKS not found in build_site.py")


class Folder:
    def __init__(self, M):
        self.M = M

    def base(self, s):
        s = unicodedata.normalize("NFKC", str(s)).translate(OLD)
        return self.M._fold(s)

    def city(self, s):
        f = self.base(s)
        for _ in range(2):
            f = CITY_SUFFIX.sub("", f).strip(" -")
        return f

    def prov(self, s):
        f = self.base(s)
        for _ in range(2):
            f = PROV_SUFFIX.sub("", f).strip(" -")
        return f

    def region(self, s):
        f = self.base(s)
        for _ in range(2):
            f = REGION_SUFFIX.sub("", f).strip(" -")
        return f


def alternatives(*fields):
    """Every name a cell of these may be: '保定 (Hotei)' is 保定 and Hotei."""
    out = []
    for v in fields:
        for a in re.split(r"[()（）/,、;]|\s+or\s+", v or ""):
            a = a.strip(" ·・")
            if a and not a.startswith(("In ", "The ")):
                out.append(a)
    return out


def index(rows, fold, fields, key="key", min_len=2):
    ix = {}
    for r in rows:
        for a in alternatives(*[r.get(f, "") for f in fields]):
            f = fold(a)
            if len(f) >= min_len and f not in ix:
                ix[f] = r[key]
    return ix


def read_csv(path):
    with open(path, encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


def build_indexes(F, M):
    T = os.path.join(ROOT, "texts", "territories")
    sub = lambda n: read_csv(os.path.join(T, "sub-units", n + ".csv"))
    ix = {}
    ix["korea"] = index(sub("korea"), F.prov, ["en", "local", "ja", "zh", "ko"])
    tw = sub("taiwan")
    shu = [r for r in tw if re.search(r"[州廳]\s*\(", r.get("ja", ""))]
    gun = [r for r in tw if re.search(r"[市郡]\s*\(", r.get("ja", ""))]
    ix["taiwan-shu"] = index(shu, F.prov, ["en", "local", "ja", "zh"])
    ix["taiwan-gun"] = index(gun, F.city, ["en", "local", "ja", "zh"])
    ix["manchukuo"] = index(sub("manchukuo"), F.prov, ["en", "local", "ja", "zh"])
    ix["china"] = index(sub("china"), F.prov, ["en", "local", "ja", "zh"])
    ix["mandate"] = index(sub("mandate-groups"), F.prov, ["en", "local", "ja", "zh"])
    # The colonies the site's spec already carries, by its own matcher.
    ix["empire"] = None
    terr = {}
    for y in ("1930", "1942"):
        for r in read_csv(os.path.join(T, y + ".csv")):
            # the empire is its own set, by the site's ids, so a table of
            # Taiwan, Chōsen and Karafuto is not mistaken for one of countries
            if r["id"] in ("other", "contested") or r["id"] in EMPIRE_IDS or r.get("cat") == "metropole":
                continue
            terr.setdefault(r["id"], r)
    ix["countries"] = index(list(terr.values()), F.prov, ["en", "label", "ja", "orig", "zh"], key="id")
    regions = {
        "hokkaido": ["北海道", "Hokkaido"], "tohoku": ["東北", "Tohoku", "Ou", "奥羽"],
        "kanto": ["關東", "関東", "Kanto"], "hokuriku": ["北陸", "Hokuriku"],
        "tosan": ["東山", "Tosan"], "tokai": ["東海", "Tokai"],
        "kinki": ["近畿", "Kinki"], "kansai": ["關西", "関西", "Kansai"],
        "chugoku": ["中國", "中国", "Chugoku"], "shikoku": ["四國", "四国", "Shikoku"],
        "kyushu": ["九州", "Kyushu"], "chubu": ["中部", "Chubu"],
        # The old circuits, which some English year books still use.
        "kinai": ["畿内", "畿內", "Kinai"], "sanyo": ["山陽", "Sanyo", "San-yo"],
        "sanin": ["山陰", "Sanin", "San-in"], "nankai": ["南海", "Nankai"],
        "saikai": ["西海", "Saikai"],
    }
    ix["regions"] = {F.region(n): k for k, ns in regions.items() for n in ns}

    cities = {}
    for r in read_csv(os.path.join(ROOT, "texts", "city-names.csv")):
        for a in alternatives(r.get("en"), r.get("ja"), r.get("ja_kyu"), r.get("zh"), r.get("local")):
            cities.setdefault(F.city(a), r["id"])
    polity = {}
    for n in ("cities-1930.csv", "cities-1942.csv", "cities.csv"):
        for r in read_csv(os.path.join(ROOT, "data", n)):
            polity.setdefault(r["id"], r.get("polity") or r.get("polity_1940") or "")
            for a in alternatives(r.get("name_en"), r.get("name_local")):
                cities.setdefault(F.city(a), r["id"])
    cities = {k: v for k, v in cities.items() if len(k) >= 2}
    ix["cities"] = cities

    stations = set()
    for y in ("1930", "1942"):
        g = json.load(open(os.path.join(ROOT, "data", "jp-rails", "japan-railway-stations-%s.geojson" % y)))
        for f in g["features"]:
            n = f["properties"].get("駅名")
            if n:
                stations.add(F.city(n))
    ix["stations"] = {s for s in stations if len(s) >= 2}
    return ix, polity


def is_pref(M, label):
    pid = M.match_place(label)
    return pid if pid and pid.isdigit() else None


def colony(M, label):
    pid = M.match_place(label)
    return pid if pid and not pid.isdigit() else None


def chains(tables):
    """Join a table carried onto the next page to the one before it, where the columns agree."""
    out = []
    for t in tables:
        if out and t.get("continued") and out[-1]["parts"] and t.get("parts"):
            head = out[-1]
            if all(len(a.get("columns", [])) == len(b.get("columns", []))
                   for a, b in zip(head["parts"], t["parts"])) and len(head["parts"]) == len(t["parts"]):
                head["parts"] = [dict(a, rows=a["rows"] + b["rows"]) for a, b in zip(head["parts"], t["parts"])]
                head["_more"].append(t["id"])
                head["_pages"] += t.get("printed_pages") or []
                continue
        out.append(dict(t, _more=[], _pages=list(t.get("printed_pages") or [])))
    return out


CIRCUITS = {"kinai", "sanyo", "sanin", "nankai", "saikai"}
TW_SHU = re.compile(r"(州|廳|[-\s](?:sh[uū]|ch[oō])|\bprefecture)$", re.I)
STATION_WORDS = re.compile(r"驛|駅|停車場|\bstations?\b", re.I)
# A rank or a mark before the name: "1 大阪市", "× 8 福岡市", "B 3 大阪市".
LEAD = re.compile(r"^(?:[A-Z]\s?(?=\d))?[\s\d×*＊○◎●△▲.、]+(?=\D)")
# A qualifier after it: "若松市(福岡)", "札幌*".
TAIL = re.compile(r"\s*(?:[(（][^)）]*[)）]|[*＊※])$")


def clean(label):
    s = LEAD.sub("", str(label)).strip()
    s = re.sub(r"(?<=[一-鿿])\s+(?=[一-鿿])", "", s)
    if re.search(r"[一-鿿]", s):     # English labels keep "(Formosa)" and the like
        s = TAIL.sub("", s)
    return s


def classify(labels, M, F, ix, stations_said=False):
    """What the labels of one axis are, or None. Returns (kind, set, matched, flags)."""
    labs = [clean(l) for l in labels if clean(l)]
    if not labs:
        return None
    prefs = {is_pref(M, l) for l in labs} - {None}
    cols = {colony(M, l) for l in labs} - {None}
    flags = []
    if len(prefs) >= MIN_PREFECTURES:
        if cols:
            flags.append("colonies: " + ", ".join(sorted(cols)))
        reg = {ix["regions"].get(F.region(l)) for l in labs
               if re.search(r"(區|地方|支部)$", str(l)) or re.search(r"\b(region|district)\b", str(l), re.I)} - {None}
        if len(reg) >= 3:
            flags.append("regional subtotals")
        return ("pref", "prefectures", len(prefs), flags)

    # Everything below competes: each set that clears its bar is scored by the
    # share of rows it names, and the best share wins. Tested in a fixed order
    # first, a list of 120 cities with four colonial capitals in it came out
    # as a table of colonies.
    n = len(labs)
    found = []

    # Regions of Japan: a scheme, named where it can be told apart.
    reg_hits = [l for l in labs if F.region(l) in ix["regions"]]
    reg = {ix["regions"][F.region(l)] for l in reg_hits}
    if len(reg) >= SETS["regions"][0] and len(reg_hits) >= 0.5 * n:
        if reg & CIRCUITS:
            fl = "五畿七道 circuits: old provinces, which prefectures cross"
        elif any("支部" in l for l in labs) or "kansai" in reg:
            fl = "NHK 支部 (1926–34): 靜岡, 岡山, 鳥取 split between branches"
        elif "tosan" in reg:
            fl = "Statistics Bureau ten regions: a clean partition"
        else:
            fl = "scheme not stated: membership needs settling"
        found.append((len(reg_hits) / n, ("other", "regions", len(reg), [fl])))

    suffixed = sum(1 for l in labs if TW_SHU.search(l))
    for name in ("korea", "taiwan-shu", "taiwan-gun", "manchukuo", "china", "mandate", "countries"):
        fold = F.city if name == "taiwan-gun" else F.prov
        rows_hit = [l for l in labs if ix[name].get(fold(l))]
        hit = {ix[name][fold(l)] for l in rows_hit}
        if len(hit) < SETS[name][0]:
            continue
        # 臺北 is a city and a prefecture: without the suffix it is the city.
        if name == "taiwan-shu" and suffixed < 3:
            continue
        fl = []
        if name == "countries":
            fl.append("%d of %d rows are on the map" % (len(rows_hit), n))
        elif len(rows_hit) < MIN_OTHER_SHARE * n:
            continue
        found.append((len(rows_hit) / n, ("other", name, len(hit), fl)))

    col_rows = [l for l in labs if colony(M, l)]
    if len(cols) >= SETS["empire"][0] and len(col_rows) >= MIN_OTHER_SHARE * n:
        found.append((len(col_rows) / n, ("other", "empire", len(cols), [])))

    city_ids = {}
    for l in labs:
        c = ix["cities"].get(F.city(l))
        if c:
            city_ids[c] = l
    not_pref = [c for c, l in city_ids.items() if not is_pref(M, l)]
    shi = [l for l in labs if re.search(r"市$", l)]
    city_rows = {l for l in labs if F.city(l) in ix["cities"]} | set(shi)
    if (len(city_ids) >= MIN_CITIES and len(not_pref) >= MIN_CITIES_NOT_PREF
            and len(city_rows) >= MIN_CITY_SHARE * n) or len(shi) >= 10:
        fl = ["%d of %d on the map's gazetteer" % (len(city_ids), len({F.city(l) for l in city_rows}))]
        if len(prefs) >= 5:
            fl.append("%d prefectures among them" % len(prefs))
        found.append((len(city_rows) / n, ("city", "cities", len(city_ids), fl)))

    # Station names are also the names of towns, wards and police districts,
    # so a table counts as one of stations only when it says so.
    if stations_said:
        st_rows = [l for l in labs if F.city(l) in ix["stations"]]
        st_only = {F.city(l) for l in st_rows if F.city(l) not in ix["cities"]}
        if len(st_only) >= MIN_STATIONS_NOT_CITY and len(st_rows) >= MIN_STATION_SHARE * n:
            found.append((len(st_rows) / n, ("other", "stations", len({F.city(l) for l in st_rows}), [])))

    if not found:
        return None
    return max(found, key=lambda x: x[0])[1]


def state(part, axis, M, F):
    """Share of numeric figures, and the count unreadable, in the part's data cells."""
    num = cells = unread = 0
    # The first column is the labels either way; across, the places are the
    # headings and every row below them is figures.
    for r in (r[1:] for r in part.get("rows", []) if r):
        for c in r:
            v = M.value(c)
            if v in ("", "-"):
                continue
            cells += 1
            if v == "?":
                unread += 1
            elif isinstance(v, (int, float)):
                num += 1
    share = num / cells if cells else 0
    if share >= GOOD_NUMERIC and unread == 0:
        g = "good"
    elif share >= FAIR_NUMERIC and unread <= FAIR_UNREADABLE:
        g = "fair"
    else:
        g = "check"
    return g, share, unread, cells


def survey(site, M, F, ix):
    books = [b for b in books_of(site) if b["slug"].startswith("japan-")]
    linked = {(c["book"], c["table"]) for c in M.load_config().get("tables", [])}
    found = []
    seen_books = []
    for b in books:
        path = os.path.join(site, "data", b["slug"] + ".json")
        if not os.path.exists(path):
            continue
        tables = json.load(open(path, encoding="utf-8"))
        tf = os.path.join(site, "build", "translations", b["slug"] + ".json")
        tr = json.load(open(tf, encoding="utf-8")) if os.path.exists(tf) else {}
        seen_books.append((b, len(tables)))
        for t in chains(tables):
            hits = []
            for pi, part in enumerate(t.get("parts") or []):
                rows = part.get("rows") or []
                said = bool(STATION_WORDS.search(" ".join([t.get("title") or "", part.get("label") or ""]
                                                         + [str(c) for c in part.get("columns") or []])))
                down = classify([r[0] for r in rows if r], M, F, ix, said)
                across = classify((part.get("columns") or [])[1:], M, F, ix, said)
                for axis, c in (("rows", down), ("columns", across)):
                    if c:
                        g, share, unread, n = state(part, axis, M, F)
                        hits.append(dict(part=pi, axis=axis, kind=c[0], set=c[1], matched=c[2], flags=c[3],
                                         grade=g, share=share, unread=unread, cells=n,
                                         label=part.get("label"), nrows=len(rows),
                                         ncols=len(part.get("columns") or [])))
                        break
            if not hits:
                continue
            en = (tr.get(t["id"]) or {}).get("t") if isinstance(tr.get(t["id"]), dict) else None
            for kind in ("pref", "city", "other"):
                hs = [h for h in hits if h["kind"] == kind]
                if not hs:
                    continue
                if kind == "other":
                    hs = [h for h in hs if h["grade"] != "check"]
                    if not hs:
                        continue
                found.append(dict(book=b, table=t, en=en, kind=kind, hits=hs,
                                  linked=(b["slug"], t["id"]) in linked))
    return found, seen_books


# ------------------------------------------------------------------ the page

def esc(s):
    return html.escape(str(s or ""), quote=True)


def year_of(b):
    m = re.search(r"(1[89]\d\d)", b["slug"])
    return m.group(1) if m else ""


def row_html(c):
    t, b = c["table"], c["book"]
    url = BOOK_URL.format(slug=b["slug"], id=t["id"])
    pages = t.get("_pages") or []
    where = "p. %s" % "–".join(str(p) for p in (pages[:1] + pages[-1:] if len(pages) > 1 else pages)) if pages else ""
    more = (" + %d page%s" % (len(t["_more"]), "s" if len(t["_more"]) > 1 else "")) if t["_more"] else ""
    no = ("No. %s" % t["table_no"]) if t.get("table_no") not in (None, "") else ""
    best = max(c["hits"], key=lambda h: (h["grade"] == "good", h["matched"]))
    grades = sorted({h["grade"] for h in c["hits"]}, key=["good", "fair", "check"].index)
    sets = sorted({SETS[h["set"]][1] if h["set"] in SETS else h["set"].capitalize() for h in c["hits"]})
    parts = "; ".join(
        "%s%s %d%s%s" % ("part %d " % (h["part"] + 1) if len(t["parts"]) > 1 else "",
                         "across" if h["axis"] == "columns" else "down",
                         h["matched"],
                         "/47" if h["set"] == "prefectures" else "",
                         (" · " + " · ".join(h["flags"])) if h["flags"] else "")
        for h in c["hits"])
    title = esc(t.get("title"))
    en = ('<div class="en">%s</div>' % esc(c["en"])) if c["en"] else ""
    badge = ' <span class="linked" title="Already linked from the tables site">linked</span>' if c["linked"] else ""
    text = " ".join([b["slug"], t["id"], t.get("title") or "", c["en"] or "", " ".join(sets), parts]).lower()
    return (
        '<tr data-grade="%s" data-text="%s">'
        '<td class="id"><a href="%s">%s</a>%s<div class="sub">%s</div></td>'
        '<td><div lang="ja">%s</div>%s</td>'
        '<td>%s<div class="sub">%s</div></td>'
        '<td class="num">%d × %d</td>'
        '<td><span class="g g-%s">%s</span><div class="sub">%d%% figures%s</div></td>'
        "</tr>"
    ) % (best["grade"], esc(text), esc(url), esc(t["id"]), badge,
         esc(" · ".join(x for x in (no, where + more) if x)),
         title, en, esc(", ".join(sets)), esc(parts),
         best["nrows"], best["ncols"],
         best["grade"], esc("/".join(grades)), round(100 * best["share"]),
         (", %d unreadable" % best["unread"]) if best["unread"] else "")


KINDS = [
    ("pref", "prefectures", "1. Prefecture map",
     "Thirty or more of the 47 prefectures down the first column or across the headings. "
     "These are what the tables site's <em>Show on map</em> link already sends."),
    ("city", "cities", "2. Data attached to cities",
     "Six or more of the map's cities, at least three of them not also a prefecture's name, "
     "or ten rows ending in 市. The map has no city link yet."),
    ("other", "other", "3. Other units the map draws",
     "Provinces, colonies, countries, stations and regions, in a good or fair state only. "
     "None of these can be sent yet."),
]


def section(found, seen_books, site):
    by_kind = defaultdict(list)
    for c in found:
        by_kind[c["kind"]].append(c)
    out = []
    total_tables = sum(n for _, n in seen_books)
    out.append('<section id="map-candidates" data-section="Map-link candidates">')
    out.append("<h2>Map-link candidates</h2>")
    out.append('<p class="lede">Tables in the %d Japan volumes of <em>Old Tables</em> (%s tables) '
               "whose rows or headings name places this map can draw. Built %s from the tables site at "
               "<code>%s</code>.</p>"
               % (len(seen_books), f"{total_tables:,}", datetime.now().strftime("%-d %B %Y, %H:%M"),
                  esc(site.replace(os.path.expanduser("~"), "~", 1))))
    out.append('<ul class="counts">')
    for kind, slug, head, _ in KINDS:
        L = by_kind[kind]
        g = Counter(max((h["grade"] for h in c["hits"]), key=["check", "fair", "good"].index) for c in L)
        out.append('<li><a href="#cand-%s">%s</a>: %d tables (%d good, %d fair, %d to check)</li>'
                   % (slug, esc(head), len(L), g["good"], g["fair"], g["check"]))
    out.append("</ul>")
    out.append('<div class="filters"><label>Filter <input type="search" class="q" placeholder="title, table id, set…"></label>'
               ' <label><input type="checkbox" class="goodonly"> good only</label></div>')

    for kind, slug, head, blurb in KINDS:
        L = by_kind[kind]
        out.append('<section id="cand-%s" class="kind">' % slug)
        out.append("<h3>%s <span class=\"n\">%d</span></h3>" % (esc(head), len(L)))
        out.append("<p>%s</p>" % blurb)
        if kind == "other":
            sets = Counter(h["set"] for c in L for h in c["hits"][:1])
            out.append('<ul class="sets">' + "".join(
                "<li>%s: %d</li>" % (esc(SETS[s][1] if s in SETS else s.capitalize()), n)
                for s, n in sorted(sets.items(), key=lambda x: -x[1])) + "</ul>")
        groups = defaultdict(list)
        for c in L:
            groups[c["book"]["slug"]].append(c)
        order = [b for b, _ in seen_books if b["slug"] in groups]
        for b in order:
            rows = groups[b["slug"]]
            out.append('<details class="book"><summary><span class="bt" lang="ja">%s</span>'
                       ' <span class="slug">%s</span> <span class="n">%d</span></summary>'
                       % (esc(b.get("title")), esc(b["slug"]), len(rows)))
            out.append('<table><thead><tr><th>Table</th><th>Title</th><th>Matched</th>'
                       '<th>Rows × cols</th><th>State</th></tr></thead><tbody>')
            out.extend(row_html(c) for c in rows)
            out.append("</tbody></table></details>")
        out.append("</section>")
    out.append('<p class="foot">Matched counts are distinct places, not rows. A table can sit in more than '
               "one kind when its parts differ. <code>check</code> means fewer than 60 per cent of the "
               "figures read as numbers or more than three are unreadable; often it is a table of names "
               "or ranges, not a bad transcription.</p>")
    out.append("</section>")
    return "\n".join(out)


TEMPLATE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Map Support Notes</title>
<style>
:root { --bg: #fbfaf7; --ink: #1f2328; --mute: #636c76; --rule: #d8d4cc; --card: #ffffff;
  --link: #1f5b8f; --good: #2d6a3e; --fair: #8a6d1a; --check: #9b3b2e; --chip: #e8eef5; }
@media (prefers-color-scheme: dark) { :root:not([data-theme="light"]) { --bg: #16181b; --ink: #e6e3dd;
  --mute: #9aa1a9; --rule: #33373c; --card: #1d2024; --link: #8fb4d4; --good: #7cc48f; --fair: #d9b95c;
  --check: #e3907f; --chip: #263445; } }
:root[data-theme="dark"] { --bg: #16181b; --ink: #e6e3dd; --mute: #9aa1a9; --rule: #33373c; --card: #1d2024;
  --link: #8fb4d4; --good: #7cc48f; --fair: #d9b95c; --check: #e3907f; --chip: #263445; }
* { box-sizing: border-box; }
body { margin: 0; background: var(--bg); color: var(--ink);
  font: 15px/1.5 -apple-system, "Segoe UI", "Hiragino Sans", "Noto Sans JP", sans-serif; }
header, main { max-width: 1100px; margin: 0 auto; padding: 0 16px; }
header { padding-top: 28px; }
h1 { font-size: 24px; margin: 0 0 4px; }
h2 { font-size: 20px; margin: 36px 0 8px; border-bottom: 1px solid var(--rule); padding-bottom: 4px; }
h3 { font-size: 17px; margin: 28px 0 4px; }
a { color: var(--link); }
nav.toc { margin: 12px 0 0; font-size: 14px; }
nav.toc a { margin-right: 14px; }
.lede, .foot, .sub, .slug, .counts { color: var(--mute); }
code { overflow-wrap: anywhere; }
.foot { font-size: 13px; margin-top: 24px; }
.n { font-size: 12px; background: var(--chip); border-radius: 9px; padding: 1px 7px; color: var(--ink); }
.filters { position: sticky; top: 0; background: var(--bg); padding: 8px 0; z-index: 1;
  border-bottom: 1px solid var(--rule); }
.filters input[type=search] { width: min(320px, 70vw); padding: 4px 6px; font: inherit;
  background: var(--card); color: var(--ink); border: 1px solid var(--rule); border-radius: 4px; }
details.book { background: var(--card); border: 1px solid var(--rule); border-radius: 6px; margin: 6px 0; }
details.book > summary { cursor: pointer; padding: 6px 10px; }
.wrap, details.book { overflow-x: auto; }
table { border-collapse: collapse; width: 100%; font-size: 13.5px; }
th, td { text-align: left; vertical-align: top; padding: 5px 8px; border-top: 1px solid var(--rule); }
th { font-weight: 600; color: var(--mute); }
td.num { white-space: nowrap; font-variant-numeric: tabular-nums; }
td.id { white-space: nowrap; }
.sub { font-size: 12px; }
.en { color: var(--mute); }
.g { font-weight: 600; } .g-good { color: var(--good); } .g-fair { color: var(--fair); } .g-check { color: var(--check); }
.linked { font-size: 11px; border: 1px solid var(--good); color: var(--good); border-radius: 8px; padding: 0 5px; }
tr.hide { display: none; }
@media (max-width: 640px) { th:nth-child(4), td:nth-child(4) { display: none; } }
</style>
</head>
<body>
<header>
<h1>Map Support Notes</h1>
<p class="lede">Working notes for linking Old Tables to the Japanese Empire map.</p>
<nav class="toc"></nav>
</header>
<main>
""" + BEGIN + "\n" + END + """

<!-- Further sections go here, each as <section id="…" data-section="Its name">…</section>;
     the list at the top finds them on its own. -->
</main>
<script>
(function () {
  var toc = document.querySelector('nav.toc');
  document.querySelectorAll('main > section[data-section]').forEach(function (s) {
    var a = document.createElement('a');
    a.href = '#' + s.id; a.textContent = s.getAttribute('data-section');
    toc.appendChild(a);
  });
  document.querySelectorAll('.filters').forEach(function (f) {
    var sec = f.closest('section'), q = f.querySelector('.q'), good = f.querySelector('.goodonly');
    function run() {
      var words = q.value.toLowerCase().split(/\\s+/).filter(Boolean);
      sec.querySelectorAll('details.book').forEach(function (d) {
        var shown = 0;
        d.querySelectorAll('tbody tr').forEach(function (tr) {
          var t = tr.getAttribute('data-text');
          var ok = words.every(function (w) { return t.indexOf(w) >= 0; }) &&
            (!good.checked || tr.getAttribute('data-grade') === 'good');
          tr.classList.toggle('hide', !ok);
          if (ok) shown++;
        });
        d.style.display = shown ? '' : 'none';
        if (words.length && shown) d.open = true;
      });
    }
    q.addEventListener('input', run); good.addEventListener('change', run);
  });
})();
</script>
</body>
</html>
"""


def write(block):
    page = open(OUT, encoding="utf-8").read() if os.path.exists(OUT) else TEMPLATE
    if BEGIN not in page or END not in page:
        raise SystemExit("%s has lost its marker comments; put them back before rebuilding" % OUT)
    a = page.index(BEGIN) + len(BEGIN)
    z = page.index(END)
    page = page[:a] + "\n" + block + "\n" + page[z:]
    with open(OUT, "w", encoding="utf-8") as fh:
        fh.write(page)


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--site", default=DEFAULT_SITE, help="a checkout of the tables site")
    ap.add_argument("--map", default=ROOT, help="a checkout of the Japanese Empire map (its texts/ and data/)")
    a = ap.parse_args()
    globals()["ROOT"] = a.map
    M = load_module(os.path.join(a.site, "build", "maplinks.py"), "maplinks")
    F = Folder(M)
    ix, _ = build_indexes(F, M)
    found, seen = survey(a.site, M, F, ix)
    write(section(found, seen, a.site))
    k = Counter(c["kind"] for c in found)
    print("%d volumes, %d tables: %d prefecture, %d city, %d other -> %s"
          % (len(seen), sum(n for _, n in seen), k["pref"], k["city"], k["other"], os.path.relpath(OUT, DEFAULT_SITE)))


if __name__ == "__main__":
    main()
