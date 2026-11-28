"""Match the glossary's places to World Historical Gazetteer records -> build/names/whg.json.

Gentle by design: one request at a time, a pause of PAUSE seconds between network requests, every response cached in
~/.cache/stat-tables-names/whg/ and never fetched again, a descriptive non-identifying user-agent, and a stop (not a
retry loop) on HTTP 429 or 5xx. Uses WHG's legacy name search (GET /api/index/?name=), which needs no token; it is
deprecated in favour of the token-based Reconciliation API.

Matching (no guessing):
  - towns and cities with coordinates: the nearest WHG record within MAX_KM of our point;
  - provinces, prefectures and other areas: a record whose title equals the query, with an administrative or
    regional feature class (A/L) and the expected country code; skipped if several such records disagree.
Usage: python3 build/names/whg.py [--limit N]
"""
import hashlib, json, math, os, re, sys, time, unicodedata, urllib.parse, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.expanduser("~/.cache/stat-tables-names/whg")
UA = "old-tables-names-glossary/0.1 (gazetteer link draft)"
PAUSE, MAX_KM, MAX_Q = 3.0, 25, 4
CC = {"China": {"CN"}, "Manchuria": {"CN"}, "Kwantung": {"CN"}, "Korea": {"KR", "KP"}, "Taiwan": {"TW", "CN"},
      "Japan": {"JP"}, "Karafuto": {"RU"}, "South Seas": {"MP", "FM", "PW", "MH"}}
AREAL = {"province", "prefecture", "colony", "region", "district", "island", "country"}
_last = [0.0]
NREQ = [0]


def fold(s):
    s = unicodedata.normalize("NFKD", s.lower())
    return re.sub(r"[^a-z]", "", "".join(c for c in s if not unicodedata.combining(c)))


def fetch(q):
    os.makedirs(CACHE, exist_ok=True)
    p = os.path.join(CACHE, hashlib.sha1(q.encode()).hexdigest() + ".json")
    if os.path.exists(p):
        return json.load(open(p))
    NREQ[0] += 1
    wait = PAUSE - (time.time() - _last[0])
    if wait > 0:
        time.sleep(wait)
    url = "https://whgazetteer.org/api/index/?name=" + urllib.parse.quote(q)
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            d = json.load(r)
    except urllib.error.HTTPError as e:
        if e.code == 429 or e.code >= 500:
            print(f"STOP: HTTP {e.code} for {q!r}; run again later (cached queries are kept)")
            sys.exit(2)
        d = {"features": [], "error": e.code}
    finally:
        _last[0] = time.time()
    json.dump(d, open(p, "w"))
    return d


def points(g):
    if not g:
        return []
    if g.get("type") == "GeometryCollection":
        return [p for x in g.get("geometries", []) for p in points(x)]
    c = g.get("coordinates")
    if not c:
        return []

    def flat(c):
        return [c] if isinstance(c[0], (int, float)) else [p for x in c for p in flat(x)]
    return flat(c)


def km(la, lo, x, y):
    a = math.sin(math.radians(la)) * math.sin(math.radians(y)) + \
        math.cos(math.radians(la)) * math.cos(math.radians(y)) * math.cos(math.radians(x - lo))
    return 6371 * math.acos(max(-1, min(1, a)))


QUERY_OVERRIDE = {"cn-Shaanxi": "Shaanxi"}       # 陝西: the toneless heading would be Shanxi (山西)


def our_names(e):
    """Folded names of the place in our glossary (all rows, all romanised columns) and its heading."""
    out = {fold(re.split(r"\s*[,(]", e["en"])[0])}
    for r in e["rows"]:
        for col, v in list(r["cols"].items()) + list(r.get("added", {}).items()):
            if col not in ("tc", "sc", "jo", "jn", "ko", "mns"):
                out |= {fold(x) for x in v}
    return {x for x in out if x}


def queries(e):
    head = QUERY_OVERRIDE.get(e["id"]) or re.split(r"\s*[,(]", e["en"])[0]
    head = re.sub(r"-(shū|chō|shō|dō|ken|fu|shi|ku|gun)$", "", head)
    qs = [fold_keep(head)]
    for col in ("py", "std", "hep", "mr", "wg", "oth"):
        for r in e["rows"]:
            qs += [fold_keep(x) for x in r["cols"].get(col, [])]
    out = []
    for q in qs:
        if q and len(q) >= 3 and q.lower() not in [x.lower() for x in out]:
            out.append(q)
    return out[:MAX_Q]


def fold_keep(s):
    s = unicodedata.normalize("NFKD", s)
    s = "".join(c for c in s if not unicodedata.combining(c)).replace("’", "'")
    s = re.sub(r"\b(City|Special City|Special Municipality|Municipality|Province|Prefecture)\b", "", s)
    return re.sub(r"\s+", " ", s).strip(" -")


def match(e):
    cc = CC.get(e["r"])
    for q in queries(e):
        feats = fetch(q).get("features", [])
        if e.get("ll"):
            la, lo = e["ll"]
            best = None
            names = our_names(e)
            for f in feats:
                ps = points(f.get("geometry"))
                if not ps:
                    continue
                d = min(km(la, lo, p[0], p[1]) for p in ps)
                pr = f["properties"]
                # a populated place (class P), titled with one of our names for the place, within MAX_KM: Xianyang
                # (20 km from Xi'an), the district Xiaoxita (listing Yichang among its variants) and the island group
                # Pescadores (for the town of Makung) are not the place
                if pr.get("fclasses") and "P" not in pr["fclasses"]:
                    continue
                same = fold(pr["title"]) in names
                if d <= MAX_KM and same and (best is None or d < best[0]):
                    best = (d, f, same)
            if best:
                p = best[1]["properties"]
                return {"pid": p["place_id"], "title": p["title"], "how": f"{best[0]:.1f} km from our point", "q": q}
        elif e["k"] in AREAL:
            hits = [f for f in feats if fold(f["properties"]["title"]) == fold(q)
                    and set(f["properties"].get("fclasses") or []) & {"A", "L"}
                    and (not cc or set(f["properties"].get("ccodes") or []) & cc)]
            if len({f["properties"]["place_id"] for f in hits}) == 1:
                p = hits[0]["properties"]
                return {"pid": p["place_id"], "title": p["title"], "how": "name, class and country", "q": q}
    return None


def main():
    lim = int(sys.argv[sys.argv.index("--limit") + 1]) if "--limit" in sys.argv else None
    G = json.load(open(os.path.join(HERE, "glossary.json"), encoding="utf-8"))["entries"]
    out_p = os.path.join(HERE, "whg.json")
    out = json.load(open(out_p)) if os.path.exists(out_p) else {}
    todo = [e for e in G if e["r"] != "Other" and (e.get("ll") or e["k"] in AREAL)]
    if lim:
        todo = todo[:lim]
    n = 0
    for i, e in enumerate(todo):
        m = match(e)                 # every place is matched again; earlier queries come from the cache
        out[e["id"]] = m or {}
        n += bool(m)
        if i % 25 == 0:
            json.dump(out, open(out_p, "w"), ensure_ascii=False, indent=0)
            print(f"{i + 1}/{len(todo)} done, {sum(1 for v in out.values() if v)} matched", flush=True)
    # one WHG record for one place: when two places claim it, the one named like the record keeps it
    by = {}
    for pid, v in out.items():
        if v.get("pid"):
            by.setdefault(v["pid"], []).append(pid)
    E = {e["id"]: e for e in G}
    for rec, pids in by.items():
        if len(pids) > 1:
            keep = [p for p in pids if p in E and fold(out[p]["title"]) in {fold(re.split(r"\s*[,(]", E[p]["en"])[0])}]
            for p in pids:
                if p not in keep[:1]:
                    out[p] = {"dropped": f"record {rec} also matched {', '.join(x for x in pids if x != p)}"}
    json.dump(out, open(out_p, "w"), ensure_ascii=False, indent=0)
    print(f"finished: {len(todo)} places, {sum(1 for v in out.values() if v.get('pid'))} matched; {NREQ[0]} new requests")


if __name__ == "__main__":
    main()
