"""merge_1922_ids.py (run once, 2026-11-25): the five 1922 part books korea-tokanfu-1922-{2,3-1,4,5,7} became one book
korea-tokanfu-1922 (../_pipeline/merge_1922.py). Rewrite table references "korea-tokanfu-1922-4/p0018_1" or
"korea-tokanfu-1922-4:p0018_1" to "korea-tokanfu-1922/p4-0018_1" in the live data files, and merge the translations."""
import json, re, os, glob
H = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = {"2": 2, "3-1": 3, "4": 4, "5": 5, "7": 7}
RX = re.compile(r"korea-tokanfu-1922-(3-1|2|4|5|7)([/:])p(\d+)_(\d+)")
sub = lambda s: RX.sub(lambda m: f"korea-tokanfu-1922{m.group(2)}p{P[m.group(1)]}-{int(m.group(3)):04d}_{m.group(4)}", s)
files = [os.path.join(H, "tags/published/assignments.json")] + glob.glob(os.path.join(H, "crosslinks/families/*.json")) \
    + glob.glob(os.path.join(H, "finders/*/specs/**/*.json"), recursive=True) + glob.glob(os.path.join(H, "finders/*/spec_fixes.json"))
for f in files:
    s = open(f, encoding="utf-8").read()
    n = s
    n = sub(n)
    if n != s:
        open(f, "w", encoding="utf-8").write(n)
        print("rewrote", os.path.relpath(f, H), len(RX.findall(s)))
    left = re.findall(r"korea-tokanfu-1922-(?:3-1|2|4|5|7)", n)
    if left: print("  LEFT", len(left), os.path.relpath(f, H))
# finder links: {slug: {id: ...}}
for f in glob.glob(os.path.join(H, "finders/*/table_links.json")):
    d = json.load(open(f, encoding="utf-8")); ch = False
    for old, p in P.items():
        o = d.pop(f"korea-tokanfu-1922-{old}", None)
        if o:
            ch = True
            for k, v in o.items():
                m = re.fullmatch(r"p(\d+)_(\d+)", k)
                d.setdefault("korea-tokanfu-1922", {})[f"p{p}-{int(m.group(1)):04d}_{m.group(2)}"] = v
    if ch:
        json.dump(d, open(f, "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))
        print("rewrote", os.path.relpath(f, H))
# added dates
f = os.path.join(H, "added_dates.json"); d = json.load(open(f, encoding="utf-8"))
ds = [d.pop(f"korea-tokanfu-1922-{o}") for o in P if f"korea-tokanfu-1922-{o}" in d]
if ds:
    d["korea-tokanfu-1922"] = min(ds)
    json.dump(d, open(f, "w", encoding="utf-8"), ensure_ascii=False, indent=1); print("added_dates merged")
# translations
out = {"_chapters": {}}
for old, p in P.items():
    f = os.path.join(H, "translations", f"korea-tokanfu-1922-{old}.json")
    if not os.path.exists(f): continue
    for k, v in json.load(open(f, encoding="utf-8")).items():
        if k == "_chapters": out["_chapters"].update(v); continue
        m = re.fullmatch(r"p(\d+)_(\d+)", k)
        out[f"p{p}-{int(m.group(1)):04d}_{m.group(2)}" if m else k] = v
if len(out) > 1:
    json.dump(out, open(os.path.join(H, "translations", "korea-tokanfu-1922.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("translations merged:", len(out) - 1, "entries")
