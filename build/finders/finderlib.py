"""Shared code of the finder pages (build/finders/<name>/): reading figures and dates out of transcribed cells,
matching printed place names to the gazetteer (build/finders/places/), loading tables and specs.

Population was the first finder; its own extraction (claims) is in build/finders/population/extract.py.
Original notes:
Population claims from the transcribed tables, read by the specs in build/population/specs/*.json (POP_TASK.md).

Every figure comes from a cell of a table in data/<slug>.json, exactly as transcribed: nothing is read again, filled,
smoothed or corrected. A cell that is empty, "[?]", a dash, a ditto mark or not a plain number gives no claim.

claims(): list of dicts {place (id), label, date, year, approx, m, g, b, n, v, src (slug:id), part, row, col}
and the places made up on the way (labels the gazetteer does not know), and the labels that were not placed.
"""
import glob, json, os, re, sys, unicodedata
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))      # build/finders
BUILD = os.path.dirname(HERE)
PLACES = os.path.join(HERE, "places")
SITE = os.path.dirname(BUILD)
sys.path.insert(0, BUILD)
import maplinks as M  # noqa: E402
import build_candidates as BC  # noqa: E402

F = BC.Folder(M)
G = json.load(open(os.path.join(PLACES, "places.json")))
PL, IX = G["places"], G["ix"]
# Hand-made matches (ALIAS_TASK.md): {"map": {"<region>|<label as printed>": place id}, "new": {id: place}}
_AL = json.load(open(os.path.join(PLACES, "aliases.json"))) if os.path.exists(os.path.join(PLACES, "aliases.json")) else {}
ALIASES = _AL.get("map", {})
for _k, _v in _AL.get("new", {}).items():
    PL.setdefault(_k, _v)

# ---------------------------------------------------------------- numbers
KD = {"〇": 0, "零": 0, "○": 0, "一": 1, "二": 2, "三": 3, "四": 4, "五": 5, "六": 6, "七": 7, "八": 8, "九": 9}
KU = {"十": 10, "百": 100, "千": 1000}


def kanji_num(s):
    if not s or any(c not in KD and c not in KU and c not in "萬万億" for c in s):
        return None
    if not any(c in KU or c in "萬万億" for c in s):
        return int("".join(str(KD[c]) for c in s))
    total, sect, cur = 0, 0, 0
    for c in s:
        if c in KD:
            cur = KD[c] if cur == 0 else cur * 10 + KD[c]
        elif c in KU:
            sect += (cur or 1) * KU[c]
            cur = 0
        elif c in "萬万":
            total += (sect + cur) * 10000
            sect = cur = 0
        elif c == "億":
            total += (sect + cur) * 100000000
            sect = cur = 0
    return total + sect + cur


NUMRX = re.compile(r"^\d{1,3}(?:[,，]\d{3})+(?:\.\d+)?$|^\d+(?:\.\d+)?$")


def number(cell, mult=1):
    """The figure in a cell, or None. Footnote marks around it are allowed; anything doubtful is not."""
    if cell is None:
        return None
    s = unicodedata.normalize("NFKC", str(cell)).strip()
    if not s or "[?]" in s or "?" in s:
        return None
    s = re.sub(r"^[*†‡§¶#a-d()（）\s]+(?=\d)|(?<=\d)[*†‡§¶#()（）\s]+[a-d]?$", "", s)
    s = re.sub(r"(?<=\d)\s+(?=\d{3}\b)", ",", s)          # "56 312 256"
    s = s.replace("，", ",").replace("·", ".")
    if mult == 1 and "." in s and re.match(r"^\d{1,3}(?:[.,]\d{3})+$", s):
        s = s.replace(".", ",")          # "65.687": a point printed for the comma; people are not counted in fractions
    if NUMRX.match(s):
        v = float(s.replace(",", "")) * mult
    else:
        k = kanji_num(s.replace(",", "").replace("、", ""))
        if k is None:
            return None
        v = k * mult
    if v <= 0:
        return None
    return int(round(v))


# ---------------------------------------------------------------- dates
ERA = {"明治": 1867, "大正": 1911, "昭和": 1925, "民國": 1911, "民国": 1911, "中華民國": 1911, "康德": 1933, "大同": 1931,
       "光緒": 1874, "宣統": 1908, "M": 1867, "T": 1911, "S": 1925, "Meiji": 1867, "Taisho": 1911, "Taishō": 1911, "Showa": 1925, "Shōwa": 1925}
DITTO = re.compile(r"^\s*(,,|〃|″|同|同上|”|\"|do\.?|ditto|''|仝)\s*$", re.I)


def date_of(label, prev=None):
    """(date string, year, approx) from a row label, or None."""
    if label is None:
        return None
    s = unicodedata.normalize("NFKC", str(label)).strip()
    if DITTO.match(s) or s == "":
        return prev if s else None
    approx = s.startswith("~")
    s = s.lstrip("~").strip()
    m = re.match(r"^(?:A\.?D\.?\s*)?(1[5-9]\d\d|20[0-4]\d)(?:[-/.](\d{1,2})(?:[-/.](\d{1,2}))?)?", s)
    if m:
        y = int(m.group(1))
        d = m.group(1) + (f"-{int(m.group(2)):02d}" if m.group(2) and 1 <= int(m.group(2)) <= 12 else "") + (
            f"-{int(m.group(3)):02d}" if m.group(2) and m.group(3) and 1 <= int(m.group(2)) <= 12 and 1 <= int(m.group(3)) <= 31 else "")
        if not m.group(2):
            if re.search(r"末|end|Dec\.?\s*31|31\s*Dec", s, re.I):
                d = f"{y}-12-31"
            elif re.search(r"Oct\.?\s*1\b|1\s*Oct|10月1日", s):
                d = f"{y}-10-01"
        return d, y, approx
    for era, base in sorted(ERA.items(), key=lambda x: -len(x[0])):
        m = re.match(r"^" + re.escape(era) + r"\.?\s*([0-9]+|[〇一二三四五六七八九十元]+)\s*年?", s)
        if m:
            n = m.group(1)
            n = 1 if n == "元" else (int(n) if n.isdigit() else kanji_num(n))
            if not n:
                return None
            y = base + n
            d = f"{y}-12-31" if re.search(r"末|年末|end", s[m.end():]) else str(y)
            return d, y, approx
    return None


def norm_date(d, edition_year):
    """A spec date ("1930", "1930-10-01", "~1935", "1930-31") -> (date, year, approx)."""
    if not d:
        return (f"~{edition_year}" if edition_year else None, edition_year, True)
    r = date_of(str(d))
    if r:
        return r
    m = re.search(r"(1[6-9]\d\d)", str(d))
    if m:
        return str(d), int(m.group(1)), True
    return None


# ---------------------------------------------------------------- places
TOTALRX = re.compile(r"^(總計|総計|合計|計|共計|累計|總數|総数|總數計|全計|統計|總|総|Total|Totals|Grand total|Grand Total|Sum|All|Total population|全國計|全國|全道|全島|全州|全鮮|全滿|Whole country)\.?$", re.I)
CTX = {"japan": "japan", "japan proper": "japan", "korea": "korea", "chosen": "korea", "taiwan": "taiwan", "formosa": "taiwan",
       "karafuto": "karafuto", "kwantung": "kwantung", "south seas": "nanyo", "nanyo": "nanyo", "manchuria": "manchuria",
       "manchukuo": "manchuria", "china": "china", "world": "world"}


def ctx_id(within):
    if not within:
        return None
    w = str(within).strip().lower()
    if w in CTX:
        return CTX[w]
    return resolve(within, None, None)[0]


QUAL = re.compile(r"zone|proper|area|settlement|concession|includ|incl\.|excl|exclusive|total|\bcity\b|town|district|suburb|county|walled|native|foreign|\bold\b|\bnew\b|part|ward|special|railway|S\.M\.R|附屬|附属|城内|城外|市内|市外|租界|商埠|部", re.I)
CJK = re.compile(r"[\u3040-\u30ff\u3400-\u9fff]")


def forms(label):
    """The label, and the forms in a bilingual label ('京城 (Keijō)', 'Keijo (京城)'); not 'X (Y, etc.)'."""
    out = [label]
    m = re.match(r"^(.*?)\s*[(（](.*?)[)）]\s*$", label)
    if m:
        a, b = m.group(1).strip(), m.group(2).strip()
        if not QUAL.search(b):        # 'Mukden (S.M.R. Zone)' and 'Hsinking (city proper)' are not Mukden or Hsinking
            out.append(a)
            if bool(CJK.search(a)) != bool(CJK.search(b)) and "etc" not in b:
                out.append(b)
    for a in re.split(r"\s*/\s*", label):
        if a not in out and len(re.split(r"\s*/\s*", label)) == 2:
            out.append(a)
    return out


def look(ixname, label, fold, bilingual=True):
    ix = IX.get(ixname) or {}
    for a in (forms(label) if bilingual else [label, re.split(r"\s*[(（]", label)[0]]):
        f = fold(a)
        if f in ix:
            return ix[f]
    return None


TOPLEVEL = {"empire", "japan", "korea", "taiwan", "karafuto", "kwantung", "nanyo", "manchuria", "china", "chinaproper", "world", "smr"}
REGION_OK = {"japan": {"japan"}, "korea": {"korea"}, "taiwan": {"taiwan"}, "karafuto": {"karafuto"}, "kwantung": {"kwantung", "manchuria"},
             "nanyo": {"nanyo"}, "manchuria": {"manchuria", "kwantung", "china"}, "china": {"china", "manchuria", "kwantung"}}


def bucket(pid):
    seen = set()
    while pid and pid in PL and pid not in seen:
        seen.add(pid)
        if pid in TOPLEVEL and pid not in ("empire", "chinaproper", "smr"):
            return pid
        pid = PL[pid]["up"]
    return "chinaproper" if pid == "chinaproper" else (pid or "world")


def region_key(within):
    """The region a table's places are in, as the alias file names it: korea, taiwan, china, … or * if unknown."""
    if not within:
        return "*"
    c = CTX.get(str(within).strip().lower())
    if c:
        return c
    w = _resolve(within, None, None)[0]
    return bucket(w) if w else "*"


def resolve(label, pt, within):
    """(place id or None, how): the place the label names, inside the region the table is about (a Korean town
    printed 'Koshū' is 公州, not Hangzhou; one the gazetteer lacks becomes a place of its own under that region)."""
    if ALIASES and label is not None:
        s = re.sub(r"\s+", " ", unicodedata.normalize("NFKC", str(label))).strip(" .:*†‡")
        rk = region_key(within)
        a = ALIASES.get(f"{rk}|{s}") or ALIASES.get(f"*|{s}")
        if a == "-":
            return "-", "drop"
        if a in PL:
            return a, "alias"
    pid, how = _resolve(label, pt, within)
    if pid and within and pid not in TOPLEVEL and not pid.startswith("w-"):
        c = CTX.get(str(within).strip().lower())
        if c in REGION_OK:
            ok = REGION_OK[c]
        elif c is None:
            w = _resolve(within, None, None)[0]
            ok = REGION_OK.get(bucket(w), {bucket(w)}) if w else None
        else:
            ok = None
        if ok and bucket(pid) not in ok:
            return None, None
    return pid, how


def _resolve(label, pt, within):
    """Tries the index for the stated kind of place first, then the others in an order that suits where the table is."""
    if label is None:
        return None, None
    s = re.sub(r"\s+", " ", unicodedata.normalize("NFKC", str(label))).strip(" .:*†‡")
    if not s:
        return None, None
    key = (s, pt or "", (within or "").lower())
    c = CTX.get((within or "").lower()) or (within or "").lower()
    PROV = {"korea": ["korea"], "taiwan": ["taiwan-shu"], "manchuria": ["manchukuo", "china"], "china": ["china", "manchukuo"],
            "nanyo": ["mandate", "islands"]}.get(c, ["korea", "manchukuo", "china", "taiwan-shu", "mandate", "islands"])
    TOWN = (["mandate", "islands"] if c == "nanyo" else []) + ["cities", "cities-ja"] + (["taiwan-gun"] if c == "taiwan" else [])
    if pt == "district" and c == "taiwan":
        # Taiwan's 州/廳 are often called districts; a bare name (新竹) is the 州, 新竹郡 the gun, 新竹街/市 the town
        order = (["taiwan-shu"] if not re.search(r"[郡街庄市]$|gun$|-shi$", s) else []) + ["taiwan-gun", "cities", "cities-ja"]
    elif pt == "district":
        # a county (縣) is not the town of the same name: unmatched districts become places of their own
        order = ["mandate"] if c == "nanyo" else []
    elif pt in ("city", "town", "ward"):
        # a town is only ever matched to a town: "Akita" in a table of cities is Akita city, not the prefecture
        order = TOWN
    elif pt == "prefecture":
        order = (["taiwan-shu"] if c == "taiwan" else []) + ["pref"] + PROV + ["top"]
    elif pt in ("province", "island"):
        order = PROV + ["pref", "top"]
    elif pt == "region":
        order = ["regions", "top"] + PROV + ["pref"]
    elif pt in ("country", "colony"):
        order = ["top", "countries", "pref"] + PROV
    else:
        order = (["mandate", "islands"] if c == "nanyo" else []) + ["top", "pref", "countries"] + PROV + ["cities", "cities-ja", "regions", "taiwan-gun", "islands"]
    for ixn in order:
        fold = {"cities": F.city, "taiwan-gun": F.city, "regions": F.region, "pref": F.base, "top": F.prov,
                "cities-ja": lambda a: re.sub(r"(市|府)$", "", unicodedata.normalize("NFKC", a).strip()).translate(BC.OLD)}.get(ixn, F.prov)
        if ixn == "pref":
            pid = M.match_place(s)
            if pid:
                return (("jp" + pid) if pid.isdigit() else {"karafuto": "karafuto", "taiwan": "taiwan", "chosen": "korea", "kwantung": "kwantung", "nanyo": "nanyo"}.get(pid, pid)), ixn
            continue
        pid = look(ixn, s, fold, pt not in ("ward", "district", "town"))
        if pid:
            # a prefecture-type index should not pull a Chinese province into a Japan table and so on
            if ixn in ("korea", "manchukuo", "china", "taiwan-shu", "mandate") and c in ("japan",) and pt == "prefecture":
                continue
            return pid, ixn
    # a row naming the very unit the table is about ("Chekiang" in a table of Chekiang's districts)
    w = ctx_id(within) if within and str(within).strip().lower() not in CTX else None
    if w and w in PL and F.prov(s) in (F.prov(PL[w]["en"]), F.prov(PL[w]["ja"] or "~")):
        return w, "within"
    if within and str(within).strip().lower() not in CTX:
        r = _resolve(within, None, None)[0]
        if r and F.prov(s) == F.prov(str(within)):
            return r, "within"
    return None, None


# ---------------------------------------------------------------- reading specs
def load_specs(fdir):
    """{"slug:id": spec} from <finder>/specs/*/b*.json, then <finder>/spec_fixes.json (replaces a table's spec).
    A spec whose table has changed since it was written (fingerprint "fp", see fingerprint()) is left out and
    reported in STALE: the table needs a new spec (build/finders/status.py)."""
    out = {}
    files = sorted(glob.glob(os.path.join(fdir, "specs", "*", "b*.json")))
    files += [f for f in [os.path.join(fdir, "spec_fixes.json")] if os.path.exists(f)]
    for f in files:
        try:
            L = json.load(open(f))
        except ValueError:
            print("finders: unreadable spec file", f)
            continue
        for s in L:
            if isinstance(s, dict) and s.get("t"):
                out[s["t"]] = s
    STALE.clear()
    for k, s in list(out.items()):
        t = table(*k.split(":", 1))
        if t is None or (s.get("fp") and s["fp"] != fingerprint(t)):
            STALE.append(k)
            del out[k]
    return out


STALE = []


def fingerprint(t):
    """A short hash of a table's shape and headings: it changes when the table is re-transcribed or rebuilt."""
    import hashlib
    sig = json.dumps([[len(p.get("rows") or []), p.get("columns") or [], [str((r or [""])[0]) for r in (p.get("rows") or [])]]
                      for p in (t.get("parts") or [])], ensure_ascii=False)
    return hashlib.sha1(sig.encode("utf-8")).hexdigest()[:10]


_DATA = {}


def table(slug, tid):
    if slug not in _DATA:
        p = os.path.join(SITE, "data", slug + ".json")
        _DATA[slug] = {t["id"]: t for t in json.load(open(p)) if isinstance(t, dict) and "id" in t} if os.path.exists(p) else {}
    return _DATA[slug].get(tid)


def custom_place(label, pt, within_id, made):
    """A place the gazetteer lacks (a district, ward, town or unknown unit), kept as printed under its region."""
    up = within_id or "world"
    m = re.match(r"^(.*?)\s*[(（]([^()（）]+)[)）]\s*$", str(label).strip())
    if m and pt in ("ward", "district", "town") and not QUAL.search(m.group(2)):
        p2 = _resolve(m.group(2), "city", None)[0] or _resolve(m.group(2), None, None)[0]
        if p2:
            up, label = p2, m.group(1)
    elif m and QUAL.search(m.group(2)):
        # 'Mukden (S.M.R. Zone)': a part of Mukden, listed under it
        p2 = _resolve(m.group(1), "city", None)[0] or _resolve(m.group(1), pt, None)[0]
        if p2:
            up = p2
    f = F.base(label)
    pid = "x-" + up + "-" + re.sub(r"[^\w]+", "", f)[:40]
    if pid not in made:
        made[pid] = {"en": str(label).strip(), "ja": "", "k": pt or "other", "up": up}
    return pid


