"""Read alternative names and romanisations from English Wikipedia for the glossary's places -> build/names/wiki.json.

Gentle by design (user's rules for Wikimedia): titles batched 50 to a request, one request at a time with PAUSE seconds
between them, maxlag=5, a descriptive user-agent that identifies no person, every response cached on disk
(~/.cache/stat-tables-names/wikipedia/) and never fetched again, and a stop (not a retry loop) on HTTP 429, a maxlag
error or any other API error.

Only the right place: a town or city's article is accepted only if its coordinates lie within MAX_KM of ours; a
province or colony's article only if the Japanese Empire map's gazetteer links it. Places that cannot be checked
(counties without coordinates) are not looked up.

What is read: the name infoboxes of the accepted article (Infobox Chinese, Infobox Korean name, Infobox Japanese ...,
and the native/other names of Infobox settlement), kept raw in wiki.json for collect.py to sort into columns.
Usage: python3 build/names/wiki.py
"""
import csv, glob, hashlib, json, math, os, re, sys, time, unicodedata, urllib.error, urllib.parse, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
BUILD = os.path.dirname(HERE)
CACHE = os.path.expanduser("~/.cache/stat-tables-names/wikipedia")
MAP = os.path.expanduser("~/shell/interactive-japan-map")
API = "https://en.wikipedia.org/w/api.php"
UA = "old-tables-place-glossary/0.1 (gazetteer reconciliation; batched, cached, one request at a time)"
PAUSE, MAX_KM, BATCH = 5.0, 25, 50
REGIONS = {"China", "Manchuria", "Kwantung", "Taiwan", "Korea", "Japan", "Karafuto"}
_last = [0.0]
NREQ = [0]


def api(params):
    params = dict(params, format="json", formatversion="2", maxlag="5")
    q = urllib.parse.urlencode(sorted(params.items()))
    os.makedirs(CACHE, exist_ok=True)
    p = os.path.join(CACHE, hashlib.sha1(q.encode()).hexdigest() + ".json")
    if os.path.exists(p):
        return json.load(open(p))
    wait = PAUSE - (time.time() - _last[0])
    if wait > 0:
        time.sleep(wait)
    req = urllib.request.Request(API, data=q.encode(), headers={"User-Agent": UA, "Accept": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            d = json.load(r)
    except urllib.error.HTTPError as e:
        print(f"STOP: HTTP {e.code}; cached responses are kept, run again later")
        sys.exit(2)
    finally:
        _last[0] = time.time()
        NREQ[0] += 1
    if "error" in d:
        print("STOP: API error", d["error"].get("code"), d["error"].get("info", "")[:200])
        sys.exit(2)
    json.dump(d, open(p, "w"))
    return d


def plain(s):
    s = unicodedata.normalize("NFKD", s)
    return "".join(c for c in s if not unicodedata.combining(c)).replace("’", "'")


def km(a, b):
    (la1, lo1), (la2, lo2) = a, b
    x = math.sin(math.radians(la1)) * math.sin(math.radians(la2)) + \
        math.cos(math.radians(la1)) * math.cos(math.radians(la2)) * math.cos(math.radians(lo2 - lo1))
    return 6371 * math.acos(max(-1, min(1, x)))


def map_wiki():
    """{place id: en.wikipedia title} from the map's gazetteer (provinces, colonies)."""
    G = json.load(open(os.path.join(BUILD, "finders", "places", "places.json")))["places"]
    out = {}
    files = glob.glob(os.path.join(MAP, "texts", "territories", "sub-units", "*.csv")) + \
        [os.path.join(MAP, "texts", "territories", f) for f in ("1930.csv", "1942.csv")]
    for f in files:
        for r in csv.DictReader(open(f, encoding="utf-8")):
            w = r.get("wiki") or ""
            m = re.match(r"https?://en\.wikipedia\.org/wiki/(.+)", w.split(",")[0] if "wiki/" in w.split(",")[0] else w)
            if not m:
                continue
            title = urllib.parse.unquote(m.group(1)).replace("_", " ")
            key = r.get("key") or r.get("id") or ""
            for i in G:
                if i == key or i.split("-", 1)[-1] == key:
                    out.setdefault(i, title)
    return out


def candidates(e):
    """Article titles to try for a town or city, best first."""
    out = []
    head = re.split(r"\s*[,(]", e["en"])[0]
    out.append(plain(head))
    for r in e["rows"][:1]:
        for col in ("py", "hep", "mr", "std"):
            out += [plain(f) for f in r["cols"].get(col, []) + r.get("added", {}).get(col, [])]
    for r in e["rows"][1:]:
        out += [plain(f) for f in r["cols"].get("py", []) + r.get("added", {}).get("py", [])]
    seen, res = set(), []
    for t in out:
        t = re.sub(r"\s+(City|Special City|Special Municipality|Province|Prefecture)$", "", t).strip(" -")
        if t and t.lower() not in seen and re.fullmatch(r"[A-Za-z' \-]+", t):
            seen.add(t.lower())
            res.append(t)
    return res[:4]


def resolve(titles):
    """{requested title: {'title', 'qid', 'coord' or None, 'disamb'}} for up to 50 titles in one request."""
    d = api({"action": "query", "titles": "|".join(titles), "redirects": "1", "prop": "coordinates|pageprops",
             "ppprop": "wikibase_item|disambiguation", "coprimary": "primary", "colimit": "max"})
    q = d.get("query", {})
    alias = {}
    for n in q.get("normalized", []):
        alias[n["from"]] = n["to"]
    redir = {r["from"]: r["to"] for r in q.get("redirects", [])}
    pages = {p["title"]: p for p in q.get("pages", [])}
    out = {}
    for t in titles:
        t1 = alias.get(t, t)
        t2 = redir.get(t1, t1)
        p = pages.get(t2)
        if not p or p.get("missing") or p.get("invalid"):
            continue
        co = (p.get("coordinates") or [None])[0]
        out[t] = {"title": p["title"], "qid": (p.get("pageprops") or {}).get("wikibase_item"),
                  "coord": [co["lat"], co["lon"]] if co else None,
                  "disamb": "disambiguation" in (p.get("pageprops") or {})}
    return out


# ------------------------------------------------------------------ infobox reading
def templates(text, names):
    """The parameter dicts of the templates in `names` found in wikitext (brace-matched)."""
    out = []
    for m in re.finditer(r"\{\{\s*(" + "|".join(names) + r")\s*(?=[|\n}])", text, re.I):
        i, depth, j = m.start(), 0, m.start()
        while j < len(text):
            if text.startswith("{{", j):
                depth += 1
                j += 2
            elif text.startswith("}}", j):
                depth -= 1
                j += 2
                if depth == 0:
                    break
            else:
                j += 1
        body = text[m.end():j - 2]
        out.append((m.group(1).strip(), params(body)))
    return out


SETTLEMENT = ["Infobox settlement", "Infobox prefecture-level city", "Infobox province of China", "Infobox city Japan",
              "Infobox province of Korea"]


def cut(text, names):
    """The text with the named templates (brace-matched) removed."""
    out, pos = [], 0
    for m in re.finditer(r"\{\{\s*(" + "|".join(names) + r")\s*(?=[|\n}])", text, re.I):
        if m.start() < pos:
            continue
        depth, j = 0, m.start()
        while j < len(text):
            if text.startswith("{{", j):
                depth += 1
                j += 2
            elif text.startswith("}}", j):
                depth -= 1
                j += 2
                if depth == 0:
                    break
            else:
                j += 1
        out.append(text[pos:m.start()])
        pos = j
    out.append(text[pos:])
    return "".join(out)


def params(body):
    parts, depth, cur = [], 0, ""
    k = 0
    while k < len(body):
        if body.startswith("{{", k) or body.startswith("[[", k):
            depth += 1
            cur += body[k:k + 2]
            k += 2
            continue
        if body.startswith("}}", k) or body.startswith("]]", k):
            depth -= 1
            cur += body[k:k + 2]
            k += 2
            continue
        if body[k] == "|" and depth == 0:
            parts.append(cur)
            cur = ""
        else:
            cur += body[k]
        k += 1
    parts.append(cur)
    out = {}
    for p in parts:
        if "=" in p:
            a, b = p.split("=", 1)
            v = clean(b)
            if v:
                out[a.strip().lower()] = v
    return out


LISTS = {"unbulleted list", "ubl", "plainlist", "flatlist", "hlist", "plain list", "flat list"}
APOS = {"'", "okina", "`", "ayin", "hamza", "wg-apos", "apos"}
KEEP_LAST = ("lang", "transl", "nihongo", "nobold", "nowrap", "small", "zh", "korean", "ko-", "ill", "native name", "big",
             "resize", "smaller", "noitalic", "script", "abbr", "tone superscript", "sup", "nobr")


def _template(m):
    """One innermost template: a list -> 'a; b'; an apostrophe template -> '; linktext -> its parts joined;
    a language/format wrapper -> its last plain argument; anything else -> nothing."""
    parts = [x.strip() for x in m.group(1).split("|")]
    name = parts[0].lower()
    args = [a for a in parts[1:] if "=" not in a]
    if name in APOS:
        return "'"
    if name in LISTS:
        return "; ".join(a.lstrip("* ") for a in args)
    if name == "linktext":
        return "".join(args)
    if name.startswith(KEEP_LAST):
        return args[-1] if args else ""
    return ""


def clean(v):
    v = re.sub(r"<!--.*?(-->|$)", "", v, flags=re.S)
    v = re.sub(r"--(>|&gt;)", "", v)
    v = re.sub(r"<ref[^>]*/>|<ref[^>]*>.*?(</ref>|$)", "", v, flags=re.S)
    for _ in range(6):
        v2 = re.sub(r"\{\{([^{}]*)\}\}", _template, v)
        if v2 == v:
            break
        v = v2
    v = re.sub(r"\{\{.*$", "", v, flags=re.S)                      # an unclosed template: drop the rest
    v = re.sub(r"\[\[(?:[^\]|]*\|)?([^\]]*)\]\]", r"\1", v)
    v = re.sub(r"<br\s*/?>", " ", v)
    v = re.sub(r"<[^>]+>", "", v).replace("'''", "").replace("''", "")
    return re.sub(r"\s+", " ", v).strip(" ;,")


INFOBOXES = ["Infobox Chinese", "Infobox Chinese/Chinese", "Chinese", "Infobox Korean name", "Korean", "Infobox Japanese",
             "Infobox Chinese/Korean", "Infobox Chinese/Japanese", "Infobox name module", "Infobox settlement",
             "Infobox prefecture-level city", "Infobox province of China", "Infobox city Japan", "Infobox province of Korea"]


def main():
    G = json.load(open(os.path.join(HERE, "glossary.json"), encoding="utf-8"))["entries"]
    out_p = os.path.join(HERE, "wiki.json")
    out = json.load(open(out_p)) if os.path.exists(out_p) else {}
    mw = map_wiki()
    # 1. provinces and colonies: the map's own link
    areal = [e for e in G if e["r"] in REGIONS and e["id"] in mw and not e.get("ll")]
    todo = [e for e in areal if e["id"] not in out]
    for i in range(0, len(todo), BATCH):
        chunk = todo[i:i + BATCH]
        res = resolve([mw[e["id"]] for e in chunk])
        for e in chunk:
            r = res.get(mw[e["id"]])
            if r and not r["disamb"]:
                out[e["id"]] = {"title": r["title"], "qid": r["qid"], "how": "map's link"}
    # 2. towns and cities: candidates until one lies within MAX_KM
    pts = [e for e in G if e["r"] in REGIONS and e.get("ll") and e["id"] not in out]
    cands = {e["id"]: candidates(e) for e in pts}
    for rnd in range(4):
        left = [e for e in pts if e["id"] not in out and len(cands[e["id"]]) > rnd]
        for i in range(0, len(left), BATCH):
            chunk = left[i:i + BATCH]
            res = resolve([cands[e["id"]][rnd] for e in chunk])
            for e in chunk:
                r = res.get(cands[e["id"]][rnd])
                if r and r["coord"] and not r["disamb"]:
                    d = km(e["ll"], r["coord"])
                    if d <= MAX_KM:
                        out[e["id"]] = {"title": r["title"], "qid": r["qid"], "how": f"{d:.1f} km from our point"}
        print(f"round {rnd + 1}: {sum(1 for e in pts if e['id'] in out)}/{len(pts)} towns matched; {NREQ[0]} requests so far", flush=True)
    json.dump(out, open(out_p, "w"), ensure_ascii=False, indent=1)
    # 3. the infoboxes of the accepted articles
    need = sorted({v["title"] for v in out.values()})       # cached after the first run
    texts = {}
    for i in range(0, len(need), BATCH):
        d = api({"action": "query", "titles": "|".join(need[i:i + BATCH]), "prop": "revisions", "rvprop": "content",
                 "rvslots": "main"})
        for p in d.get("query", {}).get("pages", []):
            revs = p.get("revisions") or []
            if revs:
                texts[p["title"]] = revs[0]["slots"]["main"]["content"]
    for pid, v in out.items():
        if v["title"] not in texts:
            continue
        # only the lead (before the first section heading), and only the first template of each kind: the body's
        # inline {{Korean|...}} name other things (Shenyang's article names its dishes)
        lead = re.split(r"\n==[^=]", texts[v["title"]], maxsplit=1)[0]
        seen, boxes = set(), []
        # the settlement infobox gives only its own name fields; templates nested inside it (a mayor's name in
        # {{Korean|hangul=...}}) are not names of the place, so the box is cut out before the name templates are read
        for n, ps in templates(lead, SETTLEMENT):
            if n.lower() not in seen:
                seen.add(n.lower())
                boxes.append({"t": "Infobox settlement", "p": {k: x for k, x in ps.items()
                                                              if k in ("name", "native_name", "other_name", "official_name")}})
        lead = cut(lead, SETTLEMENT)
        for n, ps in templates(lead, [x for x in INFOBOXES if x not in SETTLEMENT]):
            if n.lower() in seen:
                continue
            seen.add(n.lower())
            boxes.append({"t": n, "p": {k: x for k, x in ps.items() if len(x) < 200}})
        v["boxes"] = boxes
    json.dump(out, open(out_p, "w"), ensure_ascii=False, indent=1)
    print(f"finished: {len(out)} places with an article; {NREQ[0]} requests to Wikipedia")


if __name__ == "__main__":
    main()
