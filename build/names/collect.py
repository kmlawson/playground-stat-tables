"""Collect the draft place-name glossary (the "Places" page, places.html) into build/names/glossary.json.

DRAFT RULE (user, 2026-11-28): a cell holds only forms our books ALREADY use — printed labels from the tables, and the
English of our translated titles/descriptions. Nothing is converted or filled in to complete a row: computed pinyin
and Wade-Giles are used only to decide which column (and which name) an attested form belongs to.

Sources
  1. Population-finder claims: every printed row label matched to a gazetteer place (build/finders/population).
  2. build/finders/places/aliases.json "map": printed labels matched by hand ("<region>|<label>": place id).
  3. build/translations/*.json t/d/_chapters: a candidate form counts only when the entry's own table prints one of
     that place's CJK names (so "Andong" in a Korean book is not taken for the Manchurian city).
Places: the gazetteer (build/finders/places/places.json + aliases "new"). Labels the gazetteer does not know
(~13k "made" places, mostly counties) are not in this draft.
Coordinates: the Japanese Empire map's data/cities*.csv, for points (cities, settlements) only.
WHG links: build/names/whg.json (whg.py), when present.

Usage: nice -n 15 uv run --with pypinyin --with pykakasi python3 build/names/collect.py
"""
import csv, glob, itertools, json, os, re, sys, unicodedata
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
BUILD = os.path.dirname(HERE)
SITE = os.path.dirname(BUILD)
ROOT = os.path.dirname(SITE)
MAP = os.path.expanduser("~/shell/interactive-japan-map")
sys.path.insert(0, os.path.join(BUILD, "finders", "population"))
sys.path.insert(0, os.path.join(BUILD, "finders"))

from pypinyin import pinyin, Style  # noqa: E402
import pykakasi  # noqa: E402

_KKS = pykakasi.kakasi()


def ja_reading(cjk):
    """Japanese reading of a CJK name (pykakasi), folded: the Hepburn reference for Chinese places (大連 Dairen)."""
    c = CJK_SUFFIX.sub("", cjk) if len(CJK_SUFFIX.sub("", cjk)) >= 2 else cjk
    r = "".join(x["hepburn"] for x in _KKS.convert(c))
    return {fold(r), fold(r.replace("ou", "o").replace("uu", "u"))}

PLACES = os.path.join(BUILD, "finders", "places")
_GJ = json.load(open(os.path.join(PLACES, "places.json")))
G, GIX = _GJ["places"], _GJ["ix"]
AL = json.load(open(os.path.join(PLACES, "aliases.json")))
for k, v in AL.get("new", {}).items():
    G.setdefault(k, v)
SIMP = json.load(open(os.path.join(BUILD, "simplify", "tables.json")))
ZH_T2S, JA_O2N = SIMP["zh"], SIMP["ja"]
_V = json.load(open(os.path.join(HERE, "shinjitai.json")))     # OpenCC jp2t / s2t, character by character
def _not_big5(c):
    try:
        c.encode("big5")
        return False
    except UnicodeEncodeError:
        return True


ZH_SIMPLE_ONLY = {c for c in _V["sc"] if _not_big5(c)}         # simplified-only: has a traditional form, not in Big5
for _n, _o in {"戸": "戶", "彦": "彥", "姫": "姬", "呉": "吳", "横": "橫", "黒": "黑", "徳": "德", "児": "兒", "豊": "豐",
               "静": "靜", "浜": "濱", "県": "縣", "沢": "澤", "広": "廣", "鉄": "鐵", "駅": "驛", "区": "區", "竜": "龍",
               "亀": "龜", "斎": "齋", "関": "關", "栄": "榮", "桜": "櫻", "塩": "鹽", "温": "溫", "渓": "溪", "郷": "鄉",
               "隆": "隆", "瀬": "瀨", "恵": "惠", "徴": "徵", "黄": "黃", "満": "滿", "国": "國"}.items():
    if _n != _o:
        _V["new"].setdefault(_n, _o)
JA_NEW_ONLY = set(_V["new"])                                    # Japanese new forms with a distinct old form
JA_OLD = set(_V["new"].values())
ZH_TRAD = set(ZH_T2S)
CONV = json.load(open(os.path.join(BUILD, "romanisation", "conversions.json")))
FORMER = json.load(open(os.path.join(HERE, "former.json")))   # curated: other names of a place, with dates
DIRS = dict(re.findall(r'"slug":\s*"([^"]+)",\s*"dir":\s*"([^"]+)"', open(os.path.join(BUILD, "build_site.py")).read()))

# ------------------------------------------------------------------ regions
REGION_OF = {"japan": "Japan", "korea": "Korea", "taiwan": "Taiwan", "karafuto": "Karafuto", "kwantung": "Kwantung",
             "smr": "Manchuria", "manchuria": "Manchuria", "china": "China", "chinaproper": "China", "nanyo": "South Seas"}


def region(pid):
    seen = set()
    while pid and pid not in seen:
        seen.add(pid)
        if pid in REGION_OF:
            return REGION_OF[pid]
        pid = (G.get(pid) or {}).get("up")
    return "Other"


CHINESE_READ = {"China", "Manchuria", "Kwantung", "Taiwan"}     # places whose names have a Chinese reading

# ------------------------------------------------------------------ cleaning and folding
CJK = r"[㐀-鿿豈-﫿\U00020000-\U0002ffff々〆]"
KANA = re.compile(r"[぀-ヿ]")
GENERIC_EN = re.compile(r"\b(special municipality|special city|spec\. city|municipality|city|cities|province|prefecture|"
                        r"district|county|ward|town|village|urban district|leased territory|territory|proper|total|region|islands|island|isles|group)\b\.?", re.I)
SUFFIX_RX = re.compile(r"[-\s](fu|shi|ken|dō|do|to|tō|shō|sho|gun|chō|cho|shū|shu|sheng|shih|hsien|xian|men|ri|myŏn|myon|"
                       r"eup|up|ŭp|gu|ku)$", re.I)
CJK_SUFFIX = re.compile(r"(特別市|特別區|特別区|市|府|省|縣|県|廳|庁|郡|街|庄|區|区|町|村|面|邑)$")   # not 州 or 道: 全州, 北海道


STOP = {"chinese", "japanese", "estimate", "estimated", "capital", "w", "e", "n", "s", "se", "sw", "ne", "nw", "center",
        "centre", "central", "southern", "northern", "eastern", "western", "div", "division", "sub", "prov", "of", "and",
        "the", "south", "north", "east", "west", "in", "incl", "including", "excl", "other", "others", "part", "area",
        "zone", "rural", "urban", "special", "municipality", "city", "province", "prefecture", "district", "county", ""}


CJK_STOP = {"本國", "本国", "本土", "地方", "含", "除", "屬領", "属領", "租借地", "計", "合計", "總計", "其他", "其ノ他"}
STOP |= {"continental", "br", "mainland", "home", "dependencies", "colonies"}


def clean_parts(label):
    """A printed label -> the place names in it, as printed: footnote marks, counts and dot leaders removed, glosses
    split ('Keijo (京城)' -> Keijo, 京城; 'Liaoning 遼寧' -> Liaoning, 遼寧)."""
    s = unicodedata.normalize("NFC", str(label)).strip()
    s = re.sub(r"[.…·]{2,}.*$|…+$", "", s)
    s = re.sub(r"[*†‡§¶#]+", "", s)
    s = re.sub(r"[（(]\s*\d+\s*[)）]", "", s)
    s = re.sub(r"(?<=[A-Za-z])\[([a-z]+)\]", r"\1", s)          # 'Mit[o]': a letter the transcriber supplied
    s = re.sub(r"\s+", " ", s).strip(" .,:;-–")
    if not s or re.search(r"\d", s):
        return []
    parts = re.split(r"\s*[()（）\[\]]\s*|\s*/\s*|\s*,\s*", s)
    out = []
    for p in parts:
        # split a Latin part from a CJK part printed side by side
        for q in re.findall(rf"[゠-ヿ぀-ゟ{CJK[1:-1]}][{CJK[1:-1]}・ー゠-ヿ぀-ゟ]*|[가-힣]+(?: [가-힣]+)*|[A-Za-zÀ-ɏ'’ʻ\-. ]+", p):
            q = q.strip(" .,'-")
            if not q or len(q) < 2 and not re.match(CJK, q) and not re.match("[가-힣]", q):
                continue
            if re.fullmatch(r"[A-Za-zÀ-ɏ'’ʻ\-. ]+", q) and not GENERIC_EN.sub("", q).strip(" .-"):
                continue        # only a generic word ("City")
            if re.fullmatch(r"[A-Za-zÀ-ɏ'’ʻ\-. ]+", q) and (len(q.replace(" ", "")) < 3 or q == q.lower()):
                continue        # a fragment ("Fr") or a lowercase gloss ("new boundaries"): not a name
            if re.search(r"特別$", q):
                continue        # a cell cut short (新京特別)
            if q in CJK_STOP or re.search(r"屬領|属領|委任統治區域及|租借地$|^本國|^本国|^本土", q) and not re.search(r"南洋|帝國委任", q):
                continue        # context words printed beside a country (本國 home country, 屬領 dependencies, 含, 除)
            if re.match(r"(?i)(with|incl\.?|including|excl\.?|excluding|exclusive of|except)\b", q):
                continue
            if re.fullmatch(r"[A-Za-zÀ-ɏ'’ʻ\-. ]+", q) and all(w.lower().strip(".-") in STOP for w in re.split(r"[\s\-]+", q) if w):
                continue        # only directions or generic words ("Chinese Estimate", "W. center", "SE")
            out.append(q)
    return out


def is_cjk(s):
    """Chinese characters, or a Japanese kana name (マニラ市, ホノルル)."""
    return bool(re.search(CJK, s) or re.search(r"[゠-ヿ]{2,}", s))


def fold(s):
    """Latin form -> comparison key: lower case, no diacritics, apostrophes, hyphens or spaces, generic words off."""
    s = GENERIC_EN.sub("", s)
    s = SUFFIX_RX.sub("", s.strip())
    s = unicodedata.normalize("NFKD", s.lower())
    s = "".join(c for c in s if not unicodedata.combining(c))
    return re.sub(r"[^a-z]", "", s)


def core(s):
    """CJK form -> grouping key: old forms to new, simplified folded in, administrative suffix off (if 2+ chars stay)."""
    s = unicodedata.normalize("NFKC", s)
    s = "".join(JA_O2N.get(c, c) for c in s)
    t = CJK_SUFFIX.sub("", s)
    return t if len(t) >= 2 else s      # one suffix, and never down to one character (北區 stays); 萩 / 萩市 are merged per place


def to_simplified(s):
    return "".join(ZH_T2S.get(c, c) for c in s)


PY_SPECIAL = {"陝西": "Shaanxi", "陕西": "Shaanxi"}        # the official spelling that tells 陝西 from 山西


def readings(cjk, style):
    """All readings of a CJK name in a pinyin style (heteronyms combined; capped), folded."""
    c = CJK_SUFFIX.sub("", cjk) if len(CJK_SUFFIX.sub("", cjk)) >= 2 else cjk
    if style == Style.NORMAL and c in PY_SPECIAL:
        return {fold(PY_SPECIAL[c])}
    py = pinyin(to_simplified(c), style=style, heteronym=True, errors="ignore", v_to_u=True)
    if not py:
        return set()
    combos = itertools.islice(itertools.product(*[x[:3] for x in py]), 64)
    return {fold("".join(x)) for x in combos}


# ------------------------------------------------------------------ reference romanisations from the map
def strip_tone(s):
    return "".join(c for c in unicodedata.normalize("NFKD", s) if not unicodedata.combining(c))


def map_refs():
    """{place id: {'hep': set, 'mr': set, 'other': set}} from the map gazetteer (folded)."""
    refs = defaultdict(lambda: defaultdict(set))
    for f in glob.glob(os.path.join(MAP, "texts", "territories", "sub-units", "*.csv")):
        for r in csv.DictReader(open(f, encoding="utf-8")):
            key = r.get("key", "")
            ids = [i for i in G if i.split("-", 1)[-1] == key]
            if not ids:
                continue
            ja = re.findall(r"\(([^)]*)\)", r.get("ja", "") or "")
            ko = re.findall(r"\(([^)]*)\)", r.get("ko", "") or "")
            en = r.get("en", "") or ""
            head = re.sub(r"\s*\(.*$", "", en)
            par = re.findall(r"\(([^)]*)\)", en)
            for i in ids:
                for x in ja:
                    refs[i]["hep"].add(fold(x))
                for x in ko:
                    refs[i]["mr"].add(fold(x))
                if os.path.basename(f) in ("korea.csv", "japan.csv", "taiwan.csv", "karafuto.csv"):
                    refs[i]["hep"].add(fold(head))
                for p in par:
                    for x in re.split(r",\s*", p):
                        if re.search("[ŏŭ]", x):
                            refs[i]["mr"].add(fold(x))
    for fn in ("cities.csv", "cities-1930.csv", "cities-1942.csv"):
        p = os.path.join(MAP, "data", fn)
        if not os.path.exists(p):
            continue
        for r in csv.DictReader(open(p, encoding="utf-8")):
            pid = "c-" + r["id"]
            if pid not in G:
                continue
            en = r["name_en"]
            head = re.sub(r"\s*\(.*$", "", en)
            if region(pid) in ("Japan", "Korea", "Taiwan", "Karafuto", "South Seas"):
                refs[pid]["hep"].add(fold(head))
            for p_ in re.findall(r"\(([^)]*)\)", en):
                for x in re.split(r",\s*", p_):
                    if re.search("[ŏŭ]", x):
                        refs[pid]["mr"].add(fold(x))
    return refs


def coords():
    out = {}
    for fn in ("cities.csv", "cities-1930.csv", "cities-1942.csv"):
        p = os.path.join(MAP, "data", fn)
        if os.path.exists(p):
            for r in csv.DictReader(open(p, encoding="utf-8")):
                if r.get("lat") and r.get("lon"):
                    out.setdefault("c-" + r["id"], (float(r["lat"]), float(r["lon"])))
    return out


# ------------------------------------------------------------------ attested forms
_lang_cache = {}


def table_lang(slug, tid):
    """'zh' for the China books, 'ja' for Japanese, Korean, Taiwan and South Seas books; Manchukuo and other books by
    whether the table prints kana."""
    if slug.startswith("china-"):
        return "zh"
    if re.match(r"(japan|korea|taiwan|nanyo|gyosei)-", slug):
        return "ja"
    k = (slug, tid)
    if k not in _lang_cache:
        p = os.path.join(ROOT, DIRS.get(slug, "?"), "_work", "tables", tid + ".json")
        if not os.path.exists(p):
            hits = glob.glob(os.path.join(ROOT, DIRS.get(slug, "?"), "_work", "tables", "**", tid + ".json"), recursive=True)
            p = hits[0] if hits else None
        txt = open(p, encoding="utf-8").read() if p else ""
        _lang_cache[k] = "ja" if KANA.search(txt) else ("zh" if re.search(CJK, txt) else None)
    return _lang_cache[k]


CTX_REGION = {"japan": "Japan", "korea": "Korea", "taiwan": "Taiwan", "china": "China", "manchuria": "Manchuria",
              "kwantung": "Kwantung", "karafuto": "Karafuto", "nanyo": "South Seas", "world": "Other"}
GROUP = {"China": "cn", "Manchuria": "cn", "Kwantung": "cn", "Korea": "kr", "Japan": "jp", "Karafuto": "jp",
         "Taiwan": "tw", "South Seas": "ns", "Other": "ot"}


# world-level entries of the gazetteer that are East Asian places (Weihaiwei the leased territory, Manchukuo the state):
# for the same-name check they are in China, not "Other"
GROUP_OVERRIDE = {"w-weihaiwei": "cn", "w-manchukuo": "cn", "w-hongkong": "cn", "w-macao": "cn", "w-tibet": "cn",
                  "w-kwangchowan": "cn", "w-guangzhouwan": "cn", "kwantung-zone": "cn"}


def grp(pid):
    """The region group for the same-name check; a place under an overridden unit (Victoria under Hong Kong) follows it."""
    p, seen = pid, set()
    while p and p not in seen:
        if p in GROUP_OVERRIDE:
            return GROUP_OVERRIDE[p]
        seen.add(p)
        p = (G.get(p) or {}).get("up")
    return GROUP[region(pid)]


# ---------------------------------------------------------------- filter tags (places.html "Where")
# kr Korea, jp Japan, tw Taiwan, kf Karafuto, ns South Seas, mc Manchuria (with Kwantung and the Railway Zone),
# cx China without Manchuria, se Southeast Asia, rw rest of the world, em Japanese empire to 1936 (Japan, Korea, Taiwan,
# Karafuto, Kwantung, the South Seas Mandate and Manchukuo; not the conquests from 1937). "China with Manchuria" is
# cx or mc. A place that belonged to two of these at different times gets both (Rehe: China until 1933, then Manchukuo).
NE_CHINA = {"cn-Liaoning", "cn-Jilin", "cn-Heilongjiang", "n-roc-hingan-prov", "n-roc-hopkiang-prov", "n-roc-liaopei-prov",
            "n-roc-nunkiang-prov", "n-roc-shungkiang-prov"}
REHE = {"cn-Jehol", "w-jehol", "mk-JeHol"}
SE_ASIA = {"w-philippines", "w-indochina", "w-siam", "w-thailand", "w-malaya", "w-dei", "w-burma", "w-borneo_br",
           "w-northborneo", "w-sarawak", "w-timor_pt", "w-straits", "w-singapore"}
CHINA_OTHER = {"w-hongkong", "w-macau", "w-macao", "w-guangzhouwan", "w-kwangchowan", "w-weihaiwei", "w-tibet",
               "w-xinjiang", "w-chahar", "w-suiyuan", "kiaochow"}


def chain_of(pid):
    out, seen = [], set()
    while pid and pid not in seen:
        seen.add(pid)
        out.append(pid)
        pid = (G.get(pid) or {}).get("up")
    return out


def tags(pid, ll):
    ch = set(chain_of(pid))
    reg = region(pid)
    t = set()
    if reg == "Korea":
        t |= {"kr", "em"}
    elif reg == "Japan":
        t |= {"jp", "em"}
    elif reg == "Taiwan":
        t |= {"tw", "em"}
    elif reg == "Karafuto":
        t |= {"kf", "em"}
    elif reg == "South Seas":
        t |= {"ns", "em"}
    elif reg in ("Manchuria", "Kwantung"):
        t |= {"mc", "em"}
    elif reg == "China":
        manch = bool(ch & NE_CHINA)
        if ll and not manch:
            la, lo = ll
            manch = (lo >= 121.5 and la >= 38.7) or (lo >= 118.5 and la >= 40.5)
        t |= {"mc", "em"} if manch else {"cx"}
    else:
        if ch & SE_ASIA:
            t.add("se")
        elif ch & CHINA_OTHER:
            t.add("cx")
        else:
            t.add("rw")
    if ch & REHE or (ll and 116.5 <= ll[1] <= 121.0 and 40.3 <= ll[0] <= 45.0 and reg in ("China", "Manchuria")):
        t |= {"cx", "mc", "em"}              # Rehe/Jehol: China until 1933, Manchukuo from 1933
    if "w-mongolia" in ch:
        t |= {"cx", "rw"}                    # Outer Mongolia: claimed by China, independent in practice
    if "w-guam" in ch:
        t |= {"ns", "rw"}                    # Guam: American, in the Marianas
    if pid in ("empire",):
        t = {"em"}
    if pid == "kwantung-zone":
        t = {"mc", "em"}                     # Kwantung and the Railway Zone, printed as one unit
    if pid.startswith("n-roc-") and "mc" in t:
        t.discard("em")                      # the Republic's Northeast provinces of 1945-47: after the empire
    return sorted(t)


def book_region(slug):
    """The region a book is about, or None for books that cover the whole empire (or the world)."""
    for pre, r in (("china-", "China"), ("korea-", "Korea"), ("taiwan-", "Taiwan"), ("manchukuo-", "Manchuria"),
                   ("nanyo-", "South Seas"), ("gyosei-", "South Seas")):
        if slug.startswith(pre):
            return r
    return None


BOOKS = {}          # slug -> {"title", "year"}: filled by claims()
EVIDENCE = {}       # place id -> [[book, table id, label as printed], ...]: data/places-evidence.json


def years_of(prov):
    """First and last edition year of the books that print or translate a form (alias-file entries carry none)."""
    ys = [BOOKS.get(b, {}).get("year") for (kind, b, _t, _l) in prov if kind in ("table", "translation")]
    ys = [int(y) for y in ys if isinstance(y, int) or (isinstance(y, str) and y.isdigit())]
    return [min(ys), max(ys)] if ys else None


def claims():
    """Counter {(place, label as printed, book, table, region of the table or None): claims}. The table's region is
    the finder spec's "in" where it gives one, else the book's region."""
    import build_population as BP
    import finderlib as FL
    X = BP.X
    books = BP.MP.books()
    ed = {s: BP.edition_year(b) for s, b in books.items()}
    specs = X.load_specs()
    ctx = {}
    for key, sp in specs.items():
        for x in sp.get("x", []):
            k = (key, int(x.get("part", 0) or 0))
            r = CTX_REGION.get(FL.region_key(x.get("in")))
            ctx[k] = r if ctx.get(k, r) == r else None
    cl, made, _, _ = X.claims(specs, ed)
    for sl, b in books.items():
        BOOKS[sl] = {"title": b.get("title") or sl, "year": ed.get(sl)}
    out = Counter()
    for c in cl:
        slug, tid = c["src"].split(":", 1)
        out[(c["place"], c["label"], slug, tid, ctx.get((c["src"], c["part"])) or book_region(slug))] += 1
    return out


_NAMEIX = None


def other_place(part, pid):
    """True if a gloss in a label names a different gazetteer place ('Kyobashi (Tokyo)': Tokyo is not the ward)."""
    global _NAMEIX
    if _NAMEIX is None:
        _NAMEIX = defaultdict(set)
        for i, v in G.items():
            _NAMEIX[fold(strip_tone(re.split(r"\s*[,(]", v["en"])[0]))].add(i)
            if is_cjk(v.get("ja") or ""):
                _NAMEIX[core(v["ja"])].add(i)
        for ix in GIX.values():
            for k, i in ix.items():
                _NAMEIX[fold(k) if not is_cjk(k) else core(k)].add(i)
    key = core(part) if is_cjk(part) else fold(part)
    ids = _NAMEIX.get(key, set())
    return bool(ids) and pid not in ids


def parts_for(label, pid):
    ps = clean_parts(label)
    return ps[:1] + [q for q in ps[1:] if not other_place(q, pid)]


HANGUL = json.load(open(os.path.join(HERE, "hangul.json"), encoding="utf-8"))
CORR = json.load(open(os.path.join(HERE, "corrections.json"), encoding="utf-8"))
MERGE = CORR.get("merge", {})
DROP = {(d["place"], d["label"]): d["why"] for d in CORR.get("drop", [])}
MOVE = {(d["place"], d["label"]): d["to"] for d in CORR.get("move", [])}
HANGUL_RX = re.compile(r"[가-힣]")


TABLE_GROUPS = {}


def homonym_index():
    """CJK name (grouping key) -> gazetteer places that bear it."""
    hom = defaultdict(set)
    for pid, v in G.items():
        if is_cjk(v.get("ja") or ""):
            hom[core(v["ja"])].add(pid)
    for pid, h in HANGUL.items():
        if isinstance(h, dict) and pid in G:
            hom[core(h["hanja"])].add(pid)
    return hom


from pypinyin.constants import PHRASES_DICT  # noqa: E402

CHINESE_PY = {"China", "Manchuria", "Kwantung", "Taiwan"}


# Characters whose reading genuinely varies in Chinese place names (長子 Zhangzi but 長春 Changchun; 樂亭 Laoting, 樂清
# Yueqing, 樂山 Leshan; 六安 Lu'an; 蔚縣 Yu; 單縣 Shan; 洪洞 Hongtong; 東阿 Dong'e …). A name with one of them gets no
# added pinyin unless pypinyin's phrase dictionary knows the whole name. Every other character takes its common reading.
POLY = set("長长重朝樂乐六蔚單单莘費费解洞番句歙鉛铅濟济堡會会柏大廈厦沈華华葉叶阿宿都曲尉繁峙莎車车龜龟澄行蚌埔莞和汶氾洪"
           "盱眙亳涌圩參参率鬱郁弄調调識识給给傳传臭鹿斗倉仓藍蓝濮洮鄯喀什稷澠渑黽隆沔鄯盩厔校那般角朴召查折冠舍差石"
           "家仇區区秘藏茌枞樅蕃吐鉅巨嘉省女尾蒙卡迫畜炮祭厂廠鮮鲜琿珲渦涡濬浚曽曾見见")


def pinyin_unambiguous(cjk):
    """Plain pinyin of a Chinese place name (Changchun, Xi'an, Lüshun), or None if a character in it is read more
    than one way in place names (POLY) and pypinyin's phrase dictionary does not know the whole name."""
    name = CJK_SUFFIX.sub("", cjk) if len(CJK_SUFFIX.sub("", cjk)) >= 2 else cjk
    if len(cjk) > 5 or re.search(r"租界|設治|设治|附屬|附属|委任|統治|统治|及|特別|特别|區域|区域|地方|管理|公署|鐵道|鉄道|本部|民國|民国|第", cjk):
        return None                                        # a compound label (天津英租界), not a single place name
    name = "".join(_V["new"].get(c, c) for c in name)      # Japanese new forms back to old (竜 -> 龍) before reading
    simp = to_simplified(name)
    if name in PY_SPECIAL:
        return PY_SPECIAL[name]
    if (set(name) | set(simp)) & POLY:
        return None                                        # the phrase dictionary does not decide: 朝陽 is Chaoyang, not 'zhaoyang'
    syl = [x[0] for x in pinyin(simp, style=Style.NORMAL, v_to_u=True, errors=lambda x: [None] * len(x))]
    if not syl or len(syl) != len(simp) or not all(x and x.isalpha() for x in syl):
        return None
    out = syl[0] + "".join(("'" if s[0] in "aeo" else "") + s for s in syl[1:])
    return out[:1].upper() + out[1:]


def add_reference_forms(pid, g, reg, rows, refs, db_forms):
    """Forms not printed in our books, added on request (user, 2026-11-28) and marked as added: pinyin for Chinese
    place names whose reading is unambiguous; Hepburn for Japanese places (and the map's well-known Korean and Taiwanese
    places) from the gazetteer; McCune–Reischauer and Hangul for Korean places (hangul.json)."""
    def put(row, col, form, source):
        if not form:
            return
        latin = not is_cjk(form) and not re.search("[가-힣]", form) and col not in ("mns",)
        key = (lambda x: x) if not latin else (lambda x: x.lower())      # keep tone-marked pinyin beside plain pinyin
        have = {key(f) for f in row["cols"].get(col, [])} | {key(f) for f in row.get("added", {}).get(col, [])}
        if key(form) not in have and (not latin or fold(form) not in {fold(f) for f in row["cols"].get(col, [])} or source.startswith("Wikipedia")):
            row.setdefault("added", {}).setdefault(col, []).append(form)
            row.setdefault("asrc", {})[form] = source
            db_forms.append((pid, row["core"], form, col, {"books": set(), "src": {"added: " + source}, "prov": Counter()}))
    gja = pcore_of(g.get("ja") or "") if is_cjk(g.get("ja") or "") else None
    home = next((r for r in rows if r["core"] and r["core"] == gja), rows[0] if rows else None)
    if reg in CHINESE_PY and g.get("k") not in ("country", "region", "colony", "empire", "world"):
        for r in rows:
            printed = [f for k in ("tc", "jo", "jn", "sc") for f in r["cols"].get(k, [])]
            src = printed[0] if printed else r["core"]
            if src and is_cjk(src):
                put(r, "py", pinyin_unambiguous(src), "pinyin (unambiguous reading)")
    head = re.split(r"\s*[,(]", g["en"])[0].strip()
    curated = re.match(r"(c-|kr-|tw-|jp\d|n-jp-)", pid)
    if home and head and reg in ("Japan", "Karafuto", "Korea", "Taiwan") and curated and \
            re.fullmatch(r"[A-Za-zĀāĒēĪīŌōŪū'’\- ]+", head) and not re.search(r"\b(Village|Town|Island|Islands|Region|Prefecture|City)\b", head):
        if reg in ("Japan", "Karafuto") or (not pid.startswith("n-") and g.get("k") in ("city", "province", "prefecture", "colony")):
            put(home, "hep", head, "Hepburn (gazetteer)")
    wiki_forms(pid, reg, rows, put)
    hg = HANGUL.get(pid) if isinstance(HANGUL.get(pid), dict) else None
    if hg and hg.get("mr"):
        row = next((r for r in rows if r["core"] and r["core"] == core(hg["hanja"])), home)
        if row:
            put(row, "mr", hg["mr"], "McCune–Reischauer (" + (hg.get("mr_source") or "") + ")")


WIKI = json.load(open(os.path.join(HERE, "wiki.json"), encoding="utf-8")) if os.path.exists(os.path.join(HERE, "wiki.json")) else {}
PY_SUFFIX = re.compile(r"\s+(Shì|Shi|Shěng|Sheng|Xiàn|Xian|Qū|Qu|Zhèn|Zhen|Dìqū|Méng|Shìxiá|Zìzhìqū)$")


WIKI_LABELS = {"abbreviation", "official name", "hokkien", "taiwanese hokkien name", "name", "former name", "short name",
               "alternative name", "alternative names", "other names", "full name", "postal", "local name", "native name",
               "chinese name", "japanese name", "korean name", "literal meaning", "transcriptions", "romanization"}


def cjk_runs(v, single=False):
    """The pure CJK names in an infobox value ('桂林市· Gveilinz Si' -> 桂林市; '臺北市 or 台北市' -> both). Single
    characters only where asked (an abbreviation such as 閩): elsewhere they are fragments (兒 in 熱河兒)."""
    out = []
    for part in re.split(r"\s*(?:;|,|/|·|•|\bor\b|、)\s*|\s+", v):
        for run in re.findall(rf"{CJK}+", part):
            if (len(run) >= 2 or single) and run not in out:
                out.append(run)
    return out


def _s2t(x):
    return "".join(_V["sc"].get(c, c) for c in x)


def name_keys(c):
    """Every key a Wikipedia name can match a row by: simplified to traditional, one or two suffixes off (呉市 = 呉,
    四日市市 = 四日市, 東京都 = 東京, 哈尔滨市 = 哈爾濱)."""
    keys = set()
    for x in {c, _s2t(c)}:
        k = core(x)
        keys |= {k, CJK_SUFFIX.sub("", k) or k, re.sub(r"(都|州|道)$", "", k) or k}
        k2 = CJK_SUFFIX.sub("", k)
        if k2:
            keys.add(CJK_SUFFIX.sub("", k2) or k2)
    return {k for k in keys if k}


def latin_ok(v):
    return bool(re.fullmatch(r"[A-Za-zÀ-ɏ'’ʻ \-]+", v)) and len(v.replace(" ", "")) >= 3 and \
        v.strip().lower() not in WIKI_LABELS and v[:1].isupper() and \
        not re.search(r"\b(Prefecture|Commandery|County|District|Circuit)\b", v)   # 'Jin Prefecture Jinzhou' is a phrase


def wiki_ok(pid, rows):
    """An article found by coordinates is the place, unless it is a unit of another level (a city's coordinates can
    give the prefecture's article: Tokushima). One found through the map's link must also name the place with the
    same characters or Hangul (the map links a Taiwanese gun to its whole prefecture, Lungkiang 龍江 to Heilongjiang),
    and a province's article must not be a city's (Heihe city for Heiho province)."""
    w = WIKI.get(pid)
    if not w:
        return False
    g = G.get(pid) or {}
    kind = g.get("k")
    title = w.get("title", "")
    natives = [x for b in w.get("boxes", []) for x in cjk_runs(b["p"].get("native_name", ""))]
    if kind in ("city", "town", "settlement", "ward") and re.search(r"Prefecture|Province|County|League|Region\b", title):
        return False
    if kind in ("province", "prefecture") and any(n.endswith(("市", "区", "區")) for n in natives):
        return False
    if w.get("how") != "map's link":
        return True
    ours = {r["core"] for r in rows if r["core"] and is_cjk(r["core"])}
    if is_cjk(g.get("ja") or ""):
        ours.add(core(g["ja"]))
    hg = HANGUL.get(pid)
    if isinstance(hg, dict):
        ours.add(core(hg["hanja"]))
        ours.add(hg["hangul"].replace(" ", ""))
    theirs = set()
    for b in w.get("boxes", []):
        for k in ("t", "c", "kanji", "hanja", "native_name"):
            for v in cjk_runs(b["p"].get(k, "")):
                theirs.add(core(v))
        v = b["p"].get("hangul", "").replace(" ", "")
        if v:
            theirs.add(v)
    return bool(ours & theirs)


def wiki_forms(pid, reg, rows, put):
    """Forms from the lead infoboxes of the place's English Wikipedia article (wiki.py). Each block of names goes to
    the row with its characters. A name our books do not print becomes a sub-row: 'present-day name (Wikipedia)' if
    it is the article's own name (Wuhan, Kimchaek), else 'other name (Wikipedia)' (Kaesong's 松都), or
    'abbreviation (Wikipedia)' when the infobox calls it that (閩 for Fujian)."""
    w = WIKI.get(pid)
    if not w or not w.get("boxes") or not wiki_ok(pid, rows):
        return
    src = "Wikipedia: " + w["title"]
    tfold = fold(re.sub(r"\s*\(.*\)", "", w["title"]).split(",")[0])

    def split(v):
        v = re.sub(r"<!--.*$", "", v)
        return [x.strip(" ,;") for x in re.split(r"\s*[;,]\s*|\s+or\s+", v) if x.strip(" ,;")]

    def row_for(chars, latin, block, label=None):
        cs = [core(c) for c in chars if c and is_cjk(c)]
        keys = set().union(*[name_keys(c) for c in chars if c and is_cjk(c)]) if cs else set()
        for r in rows:
            if r["core"] and (r["core"] in keys or name_keys(r["core"]) & keys):
                return r
        if latin:
            for r in rows:
                if r["core"] and is_cjk(r["core"]) and reg in CHINESE_READ and fold(latin) in readings(r["core"], Style.NORMAL):
                    return r
        if not cs:
            return rows[0]
        if block == 1 and (not rows[0]["core"] or rows[0]["core"] == cs[0]):
            return rows[0]
        if label == "abbreviation":
            st, note = "abbreviation (Wikipedia)", "abbreviation given by Wikipedia"
        elif block == 1 and latin and fold(latin) == tfold:
            st, note = "present-day name (Wikipedia)", "the name of the Wikipedia article"
        else:
            st, note = "other name (Wikipedia)", "other name given by Wikipedia"
        nr = {"core": cs[0], "former": True, "note": note, "status": st, "cols": {}, "src": {}}
        rows.append(nr)
        return nr

    def latin_put(v, default):
        """A romanised name goes to the row whose characters it reads (Antung, Andong -> 安東): pinyin column if it is
        their pinyin, Wade-Giles if it has Wade-Giles' hyphens or apostrophes, else 'other' (postal: Antung, Peiping)."""
        if not latin_ok(v):
            return
        fv = fold(strip_tone(v))
        if reg in CHINESE_READ:
            for r in rows:
                if r["core"] and is_cjk(r["core"]):
                    if fv in readings(r["core"], Style.NORMAL):
                        return put(r, "py", v, src)
                    if fv in readings(r["core"], Style.WADEGILES):
                        return put(r, "wg" if re.search(r"[-'’ʻ]", v) else "oth", v, src)
        return put(default, "oth", v, src)

    def put_cjk(r, v, simplified_ok=True, single=False):
        for x in cjk_runs(v, single):
            if re.search(r"[゠-ヿ]", x) and not re.search(CJK, x):
                continue
            if set(x) & set(_V["sc"]) and simplified_ok:
                put(r, "sc", x, src)
            elif reg in ("Japan", "Karafuto"):
                put(r, "jn" if set(x) & JA_NEW_ONLY else "jo", x, src)
            else:
                put(r, "tc", x, src)

    for b in w["boxes"]:
        P = b["p"]
        t = b["t"].lower()
        if t == "infobox settlement":
            for v in cjk_runs(P.get("native_name", "")):
                put_cjk(row_for([v], tfold, 1), v)
            for v in split(P.get("native_name", "")):
                if re.search("[가-힣]", v):
                    put(rows[0], "ko", re.sub(r"[^가-힣 ]", "", v).strip(), src)
            for v in split(P.get("other_name", "")):
                latin_put(v, rows[0])
            continue
        for n in ("", "2", "3", "4"):
            chars = [P.get(k + n, "") for k in ("t", "c", "s", "kanji", "hanja", "hangul")]
            py = PY_SUFFIX.sub("", P.get("p" + n, "")).strip()
            if not any(chars) and not py:
                continue
            alt = (P.get("altname") or "").strip() if n == "2" else ""
            label = "abbreviation" if alt.lower() == "abbreviation" else None
            cc = [x for k in ("t", "c", "kanji", "hanja") for x in cjk_runs(P.get(k + n, ""), single=bool(label))]
            r = row_for(cc, strip_tone(py) or None, 1 if not n else 2, label)
            for k in ("t", "c"):
                put_cjk(r, P.get(k + n, ""), simplified_ok=True, single=bool(label))
            put_cjk(r, P.get("s" + n, ""), single=bool(label))
            put_cjk(r, P.get("kanji" + n, ""), simplified_ok=False)
            put_cjk(r, P.get("hanja" + n, ""), simplified_ok=False)
            if py and latin_ok(py):
                put(r, "py", py, src)
            wg = re.sub(r"[\d¹²³⁴⁵⁰]", "", P.get("w" + n, "")).replace("ʻ", "'").strip()
            if wg and latin_ok(wg):
                put(r, "wg" if re.search(r"[-'’]", wg) else "oth", wg, src)
            for v in split(P.get("psp" + n, "")):
                latin_put(re.sub(r"\s*\(.*?\)\s*", "", v).strip(), r)
            if re.search("[가-힣]", P.get("hangul" + n, "")):
                put(r, "ko", re.sub(r"[^가-힣 ]", "", P["hangul" + n]).strip(), src)
            for k, col in (("mr", "mr"), ("romaji", "hep"), ("hepburn", "hep"), ("revhep", "hep"), ("rr", "oth")):
                v = P.get(k + n, "")
                if latin_ok(v):
                    put(r, col, v, src)
            for k, col in (("mon", "mns"), ("mong", "mns"), ("monr", "mn")):
                for v in split(P.get(k + n, "")):
                    put(r, col, v, src)
            if alt and not label:
                latin_put(alt, r)


def pcore_of(f):
    return core(f)


def main():
    refs = map_refs()
    xy = coords()
    whg = json.load(open(os.path.join(HERE, "whg.json"))) if os.path.exists(os.path.join(HERE, "whg.json")) else {}
    keep = {fold(k): k for k in CONV.get("keep", {})}
    conv_to = {fold(c["from"]): c["to"] for c in CONV["conversions"]}
    HOM = homonym_index()
    # forms[pid][form] = {"books": set, "lang": Counter, "src": set, "prov": Counter{(kind, book, table, label): n}}
    forms = defaultdict(lambda: defaultdict(lambda: {"books": set(), "lang": Counter(), "src": set(), "prov": Counter()}))
    suspects = Counter()
    checks = Counter()          # (outcome, from place, to place or "", label, book, table, table region): claims

    def same_name_check(pid, label, ctxr, book, tid, n):
        """The place a label is attached to, after the same-name check, or None to leave it out. A label whose
        characters also name a place in another region (安東: Andong in Korea, Andong in Manchuria) stays with its place
        only if the table is about that place's region; it moves to the namesake if the table is about the namesake's
        region; it is left out if neither; and it is kept but logged if the table's region is unknown."""
        cores_here = {core(q) for q in clean_parts(label) if is_cjk(q)}
        homs = {h for c in cores_here for h in HOM.get(c, ()) if h != pid and grp(h) != grp(pid)}
        if not homs:
            return pid
        if ctxr is None:
            # the table's other rows can confirm a place, never move one (a city table of the whole empire lists
            # Korean cities among Japanese ones)
            tg = TABLE_GROUPS.get((book, tid))
            dom = tg.most_common(1)[0] if tg else None
            if dom and dom[0] == grp(pid) and dom[1] >= 0.6 * sum(tg.values()):
                checks[("kept (other rows of the table agree)", pid, "", label, book, tid, "")] += n
            else:
                checks[("kept (table region unknown)", pid, "", label, book, tid, "")] += n
            return pid
        if GROUP[ctxr] == grp(pid):
            checks[("kept (table region agrees)", pid, "", label, book, tid, ctxr)] += n
            return pid
        alt = sorted(h for h in homs if grp(h) == GROUP[ctxr])
        if len(alt) == 1:
            checks[("moved to the namesake in the table's region", pid, alt[0], label, book, tid, ctxr)] += n
            return alt[0]
        checks[("left out (table is about another region)", pid, "", label, book, tid, ctxr)] += n
        return None

    CL = claims()
    TABLE_GROUPS.clear()
    for (pid, label, slug, tid, ctxr), n in CL.items():
        if pid in G:
            TABLE_GROUPS.setdefault((slug, tid), Counter())[grp(pid)] += 1
    for (pid, label, slug, tid, ctxr), n in CL.items():
        pid = MERGE.get(pid, pid)
        if pid not in G:
            continue
        if (pid, label) in DROP:
            suspects[(pid, G[pid]["en"], label, slug + " (dropped: " + DROP[(pid, label)] + ")")] += n
            continue
        pid = MOVE.get((pid, label), pid)
        if slug.startswith("china-") and grp(pid) != "cn" and is_cjk(str(label)):
            # a Chinese county printed 'Tsingshui 清水' matched by its characters to Shimizu: the romanisation printed
            # beside the characters does not fit the place's own names
            lat = [q for q in clean_parts(label) if not is_cjk(q)]
            own = {fold(strip_tone(re.split(r"\s*[,(]", G[pid]["en"])[0]))} | refs.get(pid, {}).get("hep", set())
            if is_cjk(G[pid].get("ja") or ""):
                own |= ja_reading(G[pid]["ja"])
            if lat and fold(lat[0]) not in own:
                suspects[(pid, G[pid]["en"], label, slug)] += n
                continue
        pid2 = same_name_check(pid, label, ctxr, slug, tid, n)
        if pid2 is None:
            continue
        lang = table_lang(slug, tid)
        for f in parts_for(label, pid2):
            e = forms[pid2][f]
            e["books"].add(slug)
            e["lang"][lang] += n
            e["src"].add("table")
            e["prov"][("table", slug, tid, str(label))] += n
    for key, pid in AL.get("map", {}).items():
        pid = MERGE.get(pid, pid)
        if pid not in G:
            continue
        reg, label = key.split("|", 1)
        if (pid, label) in DROP:
            suspects[(pid, G[pid]["en"], label, "aliases.json (dropped: " + DROP[(pid, label)] + ")")] += 1
            continue
        pid = MOVE.get((pid, label), pid)
        if reg == "china" and grp(pid) != "cn":
            suspects[(pid, G[pid]["en"], label, "aliases.json")] += 1     # a Chinese label aliased to a place outside China
            continue
        pid2 = same_name_check(pid, label, CTX_REGION.get(reg), "aliases.json", key, 1)
        if pid2 is None:
            continue
        for f in parts_for(label, pid2):
            e = forms[pid2][f]
            e["lang"]["zh" if reg == "china" else "ja"] += 1
            e["src"].add("table")
            e["prov"][("alias", "aliases.json", key, label)] += 1
    for pid in HANGUL:
        if pid in G and pid not in MERGE:
            forms[pid]           # every Korean place with Hangul gets an entry
    # candidate Latin forms of each place for the translation scan
    cores_of = {pid: {core(f) for f in fs if is_cjk(f)} | ({core(G[pid]["ja"])} if is_cjk(G[pid].get("ja") or "") else set())
                for pid, fs in forms.items()}
    for pid, fm in FORMER.items():
        if pid in cores_of and isinstance(fm, dict):
            cores_of[pid] |= {core(x["cjk"]) for x in fm.get("former", []) if x.get("cjk")}
    cand = defaultdict(set)      # folded Latin form -> place ids
    for pid, fs in forms.items():
        names = [f for f in fs if not is_cjk(f) and not HANGUL_RX.search(f)] + [strip_tone(re.sub(r"\s*\(.*$", "", G[pid]["en"]))]
        if region(pid) in CHINESE_READ:
            for c in cores_of[pid]:
                for r in readings(c, Style.NORMAL):
                    names.append(r)
        for nm in names:
            if len(fold(nm)) >= 4:
                cand[fold(nm)].add(pid)
    trans_hits = 0
    word = re.compile(r"[A-Z][A-Za-zÀ-ɏ'’\-]+(?: [A-Z][A-Za-zÀ-ɏ'’\-]+)?")
    for tf in sorted(glob.glob(os.path.join(BUILD, "translations", "*.json"))):
        slug = os.path.basename(tf)[:-5]
        breg = book_region(slug)
        d = json.load(open(tf, encoding="utf-8"))
        for k, v in d.items():
            if k == "_chapters" or not isinstance(v, dict):
                continue
            text = " ".join(v.get(x, "") for x in ("t", "d") if isinstance(v.get(x), str))
            p = os.path.join(ROOT, DIRS.get(slug, "?"), "_work", "tables", k + ".json")
            if not os.path.exists(p):
                continue
            src = open(p, encoding="utf-8").read()
            for m in word.finditer(text):
                if re.match(r"(Datong|Kangde|Tatung|Kangte|Ta-tung)\b", m.group(0)) and re.match(r"\s*\d", text[m.end():]):
                    continue        # a Manchukuo era date (Datong 2, Kangde 5), not the place
                kind_word = (m.group(0).split(" ") + [""])[1].lower()
                want = {"prefecture": {"prefecture"}, "province": {"province", "prefecture"}, "city": {"city"},
                        "municipality": {"city"}, "county": {"county"}, "ward": {"ward"}, "district": {"district", "county"}}.get(kind_word)
                two = m.group(0).split(" ")
                head_word = two[0] if (want or (len(two) > 1 and not GENERIC_EN.sub("", two[1]).strip())) else m.group(0)
                for w in {head_word}:
                    ok = [pid for pid in cand.get(fold(w), ())
                          if any(c in src for c in cores_of[pid] if len(c) >= 2) or (G[pid].get("ja") and G[pid]["ja"] in src)]
                    if want:
                        ok = [x for x in ok if G[x].get("k") in want]
                    elif len(ok) > 1 and len({grp(x) for x in ok}) == 1 and len({G[x].get("k") for x in ok}) > 1:
                        checks[("translation left out (city or prefecture unclear)", ",".join(sorted(ok)), "", w, slug, k, breg or "")] += 1
                        ok = []
                    if len({grp(x) for x in ok}) > 1:
                        # the same name in two regions (Andong): only a book about one of them decides
                        inreg = [x for x in ok if breg and grp(x) == GROUP[breg]]
                        if len(inreg) == 1:
                            checks[("translation kept (book region)", inreg[0], "", w, slug, k, breg)] += 1
                        else:
                            checks[("translation left out (same name, region unclear)", ",".join(sorted(ok)), "", w, slug, k, breg or "")] += 1
                        ok = inreg if len(inreg) == 1 else []
                    for pid in ok:
                        e = forms[pid][w.strip()]
                        e["books"].add(slug)
                        e["src"].add("translation")
                        e["prov"][("translation", slug, k, w.strip())] += 1
                        trans_hits += 1
    # ------------------------------------------------ classify and build entries
    entries, db_forms = [], []
    for pid in sorted(forms, key=lambda p: (region(p), G[p]["en"])):
        g = G[pid]
        reg = region(pid)
        chinese = reg in CHINESE_READ
        en_head = re.split(r"\s*[,(]", g["en"])[0]
        main_core = None
        names = {}
        cj = [f for f in forms[pid] if is_cjk(f)]
        raw_cores = {core(f) for f in cj}
        merge = {}                       # within one place, 萩市 is 萩 and 四日市市 is 四日市 when the shorter form is printed too
        for c in raw_cores:
            for t in (CJK_SUFFIX.sub("", c), re.sub(r"(州|道)$", "", c)):
                if t != c and t in raw_cores:
                    merge[c] = t        # within one place only: 臺北州 and 臺北 are one province, 京畿道 and 京畿 one name
                    break
        pcore = lambda f: merge.get(core(f), core(f))  # noqa: E731
        cores = Counter()
        for f in cj:
            cores[pcore(f)] += sum(forms[pid][f]["lang"].values()) or 1
        fm = FORMER.get(pid) if isinstance(FORMER.get(pid), dict) else {}
        former_meta = {core(x["cjk"]): x for x in fm.get("former", []) if x.get("cjk")}
        mongol = {fold(x) for x in fm.get("mn", [])}
        hg = HANGUL.get(pid) if isinstance(HANGUL.get(pid), dict) else None
        for c in former_meta:
            cores.setdefault(c, 0)
        if fm.get("modern"):
            main_core = core(fm["modern"])
            cores.setdefault(main_core, 0)
        if main_core is None and chinese:
            for c in cores:
                if c not in former_meta and fold(strip_tone(en_head)) in readings(c, Style.NORMAL):
                    main_core = c
                    break
        if main_core is None and hg and core(hg["hanja"]) in cores:
            main_core = core(hg["hanja"])
        if main_core is None and is_cjk(g.get("ja") or "") and pcore(g["ja"]) in cores and pcore(g["ja"]) not in former_meta:
            main_core = pcore(g["ja"])
        if main_core is None and cores:
            main_core = next((c for c, _ in cores.most_common() if c not in former_meta), None)
        if main_core is None and hg:
            main_core = core(hg["hanja"])
        if main_core is None and is_cjk(g.get("ja") or ""):
            main_core = core(g["ja"])        # the gazetteer's name: sets the row's readings, is not shown as attested
        order = ([main_core] if main_core else [None]) + [c for c, _ in cores.most_common() if c != main_core]
        for c in order:
            names[c] = {"cols": defaultdict(Counter), "former": c != main_core, "added": defaultdict(list),
                        "note": (former_meta.get(c) or {}).get("note", ""),
                        "py": readings(c, Style.NORMAL) if (c and chinese) else set(),
                        "wg": readings(c, Style.WADEGILES) if (c and chinese) else set(),
                        "hep": ja_reading(c) if (c and chinese) else set()}
        books = set()
        placed = []                                  # (form, target core, column) for the database
        for f, e in forms[pid].items():
            books |= e["books"]
            w = len(e["books"]) or 1
            if HANGUL_RX.search(f):
                names[order[0]]["cols"]["ko"][f] += w
                placed.append((f, order[0], "ko"))
                continue
            if is_cjk(f):
                c = pcore(f)
                lang = e["lang"].most_common(1)[0][0] if e["lang"] else ("zh" if reg == "China" else "ja")
                if lang == "zh" or (lang is None and reg == "China"):
                    col = "sc" if set(f) & ZH_SIMPLE_ONLY else "tc"
                else:
                    col = "jn" if set(f) & JA_NEW_ONLY else "jo"
                names[c]["cols"][col][f] += w
                placed.append((f, c, col))
                continue
            fk = fold(f)
            if not fk:
                continue
            target, col = None, None
            taiwan_hep = reg == "Taiwan" and (fk in refs.get(pid, {}).get("hep", set()) or fk == fold(en_head)
                                              or any(fk in nm["hep"] for nm in names.values()))
            for c, nm in names.items():
                if taiwan_hep:
                    break       # Taiwan: a form that is both pinyin and Hepburn (Tainan) is the books' Hepburn
                if fk in nm["py"] and ("-" not in f and "'" not in f and "’" not in f or fk not in nm["wg"]):
                    target, col = c, "py"
                    break
                if fk in nm["wg"]:
                    target, col = c, ("wg" if re.search(r"[-'’ʻ]", f) else "oth")
                    break
            if col is None and re.search("[éÉ]", f):
                col = "oth"                      # Kobé, Iwaté: an older spelling, not Hepburn
            if col is None and fk in mongol:
                col = "mn"
            if col is None:
                for c, nm in names.items():
                    if fk in nm["hep"]:
                        target, col = c, "hep"
                        break
            if col is None:
                r = refs.get(pid, {})
                hep_par = {fold(x) for x in re.findall(r"\(([^)]*[ōūŌŪ][^)]*)\)", g["en"])}
                if not chinese and reg != "Other" and fk in hep_par:
                    col = "hep"
                elif reg == "South Seas" and fk == fold(en_head) and re.search(r"shima|jima|-tō|[ōū]", en_head):
                    col = "hep"
                elif fk in r.get("hep", set()) or (re.search("[ōūŌŪ]", f) and reg in ("Japan", "Korea", "Taiwan", "Karafuto", "South Seas")):
                    col = "hep"
                elif fk in r.get("mr", set()) or re.search("[ŏŭŎŬ]", f):
                    col = "mr"
                elif fk in keep:
                    col = "std"
                elif not chinese and fk == fold(strip_tone(en_head)):
                    col = "hep" if reg in ("Japan", "Korea", "Taiwan", "Karafuto") else "oth"
                else:
                    col = "oth"
                py = conv_to.get(fk)
                if py:
                    for c, nm in names.items():
                        if fold(py) in nm["py"]:
                            target = c
                            break
                if target is None and re.search("[ōūŌŪ]", f) and chinese:
                    col = "hep"
            if target is None and col == "hep" and is_cjk(g.get("ja") or "") and core(g["ja"]) in names:
                target = core(g["ja"])       # the map's Hepburn romanises the gazetteer's own name (Karenkō = 花蓮港)
            if target is None:
                target = main_core if main_core in names else order[0]
            names[target]["cols"][col][f] += w
            placed.append((f, target, col))
        # Hangul added for Korean places (hangul.json; reference data, not printed in our books)
        if hg:
            tc = core(hg["hanja"]) if core(hg["hanja"]) in names else order[0]
            if hg["hangul"] not in names[tc]["cols"].get("ko", {}):
                names[tc]["added"]["ko"].append(hg["hangul"])
        rows = []
        for c in order:
            nm = names[c]
            cols = {}
            for k_, v in nm["cols"].items():
                seen_l, lst = set(), []
                for f, _ in v.most_common():
                    if f.lower() not in seen_l:
                        seen_l.add(f.lower())
                        lst.append(f)
                if lst:
                    cols[k_] = lst
            if not cols and not nm["added"] and c != order[0]:
                continue
            st = ("present-day name" if fm.get("modern") else "main") if c == order[0] else ("former name" if nm["note"] else "other form")
            row = {"core": c or "", "former": nm["former"], "note": nm["note"], "status": st, "cols": cols}
            if nm["added"]:
                row["added"] = dict(nm["added"])
            # where each form comes from: t = printed in a table, x = only in our English translations
            row["src"] = {f: ("t" if forms[pid][f]["src"] & {"table"} else "x") for v in cols.values() for f in v}
            fy = {f: years_of(forms[pid][f]["prov"]) for v in cols.values() for f in v}
            fy = {f: y for f, y in fy.items() if y}
            if fy:
                row["fy"] = fy
                row["yrs"] = [min(y[0] for y in fy.values()), max(y[1] for y in fy.values())]
            rows.append(row)
        add_reference_forms(pid, g, reg, rows, refs, db_forms)
        ent = {"id": pid, "en": g["en"], "k": g.get("k", ""), "r": reg, "up": g.get("up") or "", "rows": rows, "nb": len(books)}
        if fm.get("modern") and rows and not any(k in rows[0]["cols"] for k in ("tc", "sc", "jo", "jn")):
            ent["today"] = fm["modern"]      # hand-made (former.json); shown as a label, not as an attested form
        if hg and hg.get("today"):
            ent["today_ko"] = hg["today"]
        if pid in xy and g.get("k") in ("city", "settlement", "town"):
            ent["ll"] = [round(xy[pid][0], 3), round(xy[pid][1], 3)]
        ent["t"] = tags(pid, xy.get(pid))
        if pid in whg and whg[pid].get("pid"):
            ent["whg"] = whg[pid]
        if pid in WIKI and wiki_ok(pid, rows):
            ent["wp"] = {"title": WIKI[pid]["title"], "qid": WIKI[pid].get("qid"), "how": WIKI[pid].get("how")}
        entries.append(ent)
        for f, c, col in placed:
            db_forms.append((pid, c or "", f, col, forms[pid][f]))
        ev = {}
        for f, c, col in placed:
            for (kind, b, t, label), n in forms[pid][f]["prov"].items():
                if kind == "table":
                    ev[(b, t, label)] = ev.get((b, t, label), 0) + n
        if ev:
            EVIDENCE[pid] = [[b, t, label] for (b, t, label) in sorted(ev, key=lambda k: (BOOKS.get(k[0], {}).get("year") or 0, k[0], k[1]))]
        if hg:
            db_forms.append((pid, core(hg["hanja"]) if core(hg["hanja"]) in names else (order[0] or ""), hg["hangul"], "ko",
                             {"books": set(), "src": {"added: " + hg["source"]}, "prov": Counter()}))
    # namesakes: the same characters in another region, listed on each entry
    by_core = defaultdict(set)
    E = {e["id"]: e for e in entries}
    for e in entries:
        for r in e["rows"]:
            if r["core"] and r["cols"]:          # only names our books print (not a name Wikipedia alone gives)
                by_core[r["core"]].add(e["id"])
    for c, ids in by_core.items():
        if len({grp(i) for i in ids}) > 1:
            for i in ids:
                E[i].setdefault("same", []).extend(
                    {"id": j, "en": E[j]["en"], "r": E[j]["r"], "cjk": c} for j in sorted(ids) if j != i and grp(j) != grp(i))
    with open(os.path.join(HERE, "suspects.tsv"), "w", encoding="utf-8") as o:
        o.write("place id\tplace\tlabel as printed\tbook\tclaims\n")
        for (pid, en, label, slug), n in sorted(suspects.items()):
            o.write(f"{pid}\t{en}\t{label}\t{slug}\t{n}\n")
    with open(os.path.join(HERE, "same_name_checks.tsv"), "w", encoding="utf-8") as o:
        o.write("outcome\tplace id\tmoved to\tlabel as printed\tbook\ttable\ttable region\tclaims\n")
        for k, n in sorted(checks.items()):
            o.write("\t".join(map(str, k)) + f"\t{n}\n")
    parents = {}
    for e in entries:
        p_ = e.get("up")
        while p_ and p_ not in parents and p_ in G:
            parents[p_] = {"en": G[p_]["en"], "up": G[p_].get("up") or ""}
            p_ = G[p_].get("up")
    used = {b for v in EVIDENCE.values() for b, _t, _l in v}
    json.dump({"_doc": "Every label as printed in a table, per place of places.html: [book, table id, label]. books: title and edition year.",
               "books": {b: [BOOKS.get(b, {}).get("title", b), BOOKS.get(b, {}).get("year")] for b in sorted(used)},
               "places": EVIDENCE}, open(os.path.join(SITE, "data", "places-evidence.json"), "w", encoding="utf-8"),
              ensure_ascii=False, separators=(",", ":"))
    out = {"_doc": __doc__.split("\n\n")[0], "n": len(entries), "translation_hits": trans_hits, "entries": entries,
           "parents": parents}
    json.dump(out, open(os.path.join(HERE, "glossary.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=0)
    import db
    db.write(entries, db_forms, checks, suspects, os.path.join(SITE, "data", "place-names.sqlite"), BOOKS)
    oc = Counter(k[0] for k in checks)
    print(len(entries), "places;", sum(len(e["rows"]) for e in entries), "name rows;",
          sum(1 for e in entries for r in e["rows"] if r["former"]), "other-name rows;", trans_hits, "translation hits;",
          sum(1 for e in entries if e.get("same")), "places with a namesake elsewhere")
    print("same-name checks:", dict(oc))


if __name__ == "__main__":
    main()
