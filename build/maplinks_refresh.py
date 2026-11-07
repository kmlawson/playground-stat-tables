#!/usr/bin/env python3
"""maplinks_refresh.py: bring the city map links up to date after the map's gazetteer or our matcher changes.

    python3 build/maplinks_refresh.py                 # dry run: what would change
    python3 build/maplinks_refresh.py --write         # change build/maplinks.json
    python3 build/maplinks_refresh.py --new           # also list unlinked tables that qualify as tables of cities

1. Existing city entries (units "city", not split_col): a row (or, across, a heading) that is not in `ids` and now
   matches a map city not already named in the entry gets that id (build_candidates.match_city; CITY_UNTIL in
   maplinks_add for cities that ceased, e.g. 伏見 after 1931). Ids already in an entry are never changed.
2. With --new: list every table not yet in maplinks.json whose rows or headings build_candidates.classify calls
   cities and for which maplinks_add.entry would build an entry. Listed only, never written: which tables get a
   link is the author's choice (the chosen tables and their similar tables; support/candidates.html). Add the
   chosen ones with maplinks_add.py.

**Only ids the live map knows.** The gazetteer is read from the map's working tree, which may hold cities that are
built but not pushed. An id not in the map's `origin/main` data/cities*.csv is not written (the count is printed):
a link carrying an id the deployed map lacks would draw nothing. `--allow-unpublished` overrides that.
"""
import io, contextlib, csv, json, os, subprocess, sys
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
SITE = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import maplinks as M          # noqa: E402
import maplinks_add as A      # noqa: E402

WRITE, NEW, UNPUB = "--write" in sys.argv, "--new" in sys.argv, "--allow-unpublished" in sys.argv
F, _c, clean, bc, ix = A.city_index()


def published_ids():
    """City ids in the map's origin/main (what the deployed map can draw)."""
    out = set()
    for f in ("data/cities.csv", "data/cities-1930.csv", "data/cities-1942.csv"):
        r = subprocess.run(["git", "-C", bc.ROOT, "show", "origin/main:" + f], capture_output=True, text=True)
        if r.returncode == 0:
            out |= {row["id"] for row in csv.DictReader(io.StringIO(r.stdout))}
    return out


PUB = None if UNPUB else published_ids()
held = Counter()


def ok(cid):
    if PUB is None or cid in PUB:
        return True
    held[cid] += 1
    return False


def table(book, tid, _c={}):
    if book not in _c:
        p = os.path.join(SITE, "data", book + ".json")
        d = json.load(open(p, encoding="utf-8")) if os.path.exists(p) else []
        _c[book] = {t["id"]: t for t in (d if isinstance(d, list) else d.get("tables", []))}
    return _c[book].get(tid)


f = os.path.join(HERE, "maplinks.json")
cfg = json.load(open(f, encoding="utf-8"))
filled, gained = Counter(), Counter()
for e in cfg["tables"]:
    if e.get("units") != "city" or e.get("split_col") is not None:
        continue
    t = table(e["book"], e["table"])
    if not t:
        continue
    p = t["parts"][e.get("part", 0)]
    lc = e.get("label_col", 0)
    y = str(e.get("date") or "")[:4]
    labs = list(enumerate(p["columns"])) if e.get("across") else [(ri, r[lc] if len(r) > lc else "") for ri, r in enumerate(p["rows"])]
    named, skip, add = set(e["ids"].values()), {e.get("total_row"), e.get("total_col")}, {}
    for k, lab in labs:
        if str(k) in e["ids"] or k in skip or (e.get("across") and k == lc):
            continue
        c = bc.match_city(str(lab), M, F, ix)
        if not c or c in named or c in add.values():
            continue
        if c in A.CITY_UNTIL and y.isdigit() and int(y) > A.CITY_UNTIL[c]:
            continue
        if ok(c):
            add[str(k)] = c
    if add:
        e["ids"].update(add)
        e["ids"] = dict(sorted(e["ids"].items(), key=lambda kv: int(kv[0])))
        filled[f"{e['book']}/{e['table']}"] = len(add)
        gained.update(add.values())
print(f"existing city links: {sum(filled.values())} rows matched in {len(filled)} entries")

added = []
if NEW:
    have = {(e["book"], e["table"]) for e in cfg["tables"]}
    for b in bc.books_of(SITE):
        p = os.path.join(SITE, "data", b["slug"] + ".json")
        if not os.path.exists(p):
            continue
        d = json.load(open(p, encoding="utf-8"))
        for t in (d if isinstance(d, list) else d.get("tables", [])):
            if (b["slug"], t["id"]) in have:
                continue
            hit = False
            for part in t.get("parts") or []:
                for labs in ([r[0] for r in part.get("rows") or [] if r], (part.get("columns") or [])[1:]):
                    c = bc.classify(labs, M, F, ix)
                    hit = hit or bool(c and c[1] == "cities")
            if not hit:
                continue
            with contextlib.redirect_stdout(io.StringIO()):
                e, why = A.entry(b["slug"], t["id"])
            if not e:
                continue
            if e.get("ids") and e.get("units") == "city":
                e["ids"] = {k: v for k, v in e["ids"].items() if ok(v)}
                if len(set(e["ids"].values())) < 6:      # what is left once unpublished ids are held back
                    continue
            added.append(e)
    print(f"unlinked tables that would qualify (not added; the author chooses): {len(added)} "
          f"({Counter(e.get('units', 'prefecture') for e in added)})")
    for e in added[:15]:
        print(f"   {e['book']}/{e['table']}")
if held:
    print(f"held back, not yet on the published map: {sum(held.values())} matches of {len(held)} ids "
          f"({', '.join(k for k, _ in held.most_common(12))}{' …' if len(held) > 12 else ''})")
if gained:
    print("ids gained in existing links:", ", ".join(f"{k} {n}" for k, n in gained.most_common(15)))
if WRITE and filled:
    open(f, "w", encoding="utf-8").write(json.dumps(cfg, ensure_ascii=False, indent=1) + "\n")
    print("written: build/maplinks.json")
elif not WRITE:
    print("(dry run: nothing written)")
