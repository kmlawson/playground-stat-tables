"""topicmap_prep.py <series> <name> <slug> [<slug> ...]: write topicmap_input/<series>.md for a chapter-mapping agent:
the series' existing topics (with the chapters each existing edition maps to them) and every chapter of the new
editions with its table count and a few table titles."""
import json, os, sys, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); import chapters
H = os.path.dirname(os.path.abspath(__file__)); D = os.path.join(H, "..", "..", "data")
ser, name, new = sys.argv[1], sys.argv[2], sys.argv[3:]
S = chapters.SERIES.get(ser, {"books": [], "topics": {}})
L = [f"# Series {ser}: {name}", f"Existing editions: {', '.join(S['books']) or '(none: new series)'}", f"New editions: {', '.join(new)}", "", "## Existing topics (chapters each existing edition maps to it)"]
for t, m in S["topics"].items():
    L.append(f"- {t}: " + " | ".join(f"{b}: {', '.join(c)}" for b, c in list(m.items())[:4]))
for b in new:
    T = json.load(open(os.path.join(D, b + ".json"), encoding="utf-8"))
    tr = {}
    f = os.path.join(H, "..", "translations", b + ".json")
    if os.path.exists(f): tr = json.load(open(f, encoding="utf-8"))
    by = collections.OrderedDict()
    for t in T: by.setdefault(t.get("chapter"), []).append(t)
    L += ["", f"## {b}: chapters (table count; sample titles)"]
    for c, ts in by.items():
        en = (tr.get("_chapters") or {}).get(c, "")
        L.append(f"- {c!r}{' [EN: '+en+']' if en else ''} ({len(ts)}): " + "; ".join(str(x.get('title'))[:50] for x in ts[:4]))
os.makedirs(os.path.join(H, "topicmap_input"), exist_ok=True)
open(os.path.join(H, "topicmap_input", ser + ".md"), "w").write("\n".join(L) + "\n"); print(ser, len(L), "lines")
