"""Write listings/<series>--<topic>.txt (one line per table in each topic) for the table-matching sub-agents."""
import json, os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from chapters import SERIES
D = os.path.join(HERE, "..", "..", "data")


def slug(s): return re.sub(r'[^a-z0-9]+', '-', s.lower()).strip('-')
def cut(s, n): s = re.sub(r'\s+', ' ', str(s or '')); return s if len(s) <= n else s[:n - 1] + '…'


os.makedirs(os.path.join(HERE, "listings"), exist_ok=True)
for s, S in SERIES.items():
    data = {b: json.load(open(os.path.join(D, b + ".json"), encoding="utf-8")) for b in S["books"]}
    for top, m in S["topics"].items():
        L = [f"# Series: {S['name']} — topic: {top}", "# Editions: " + ", ".join(b for b in S['books'] if b in m),
             "# Format: slug | id | chapter | pp. | title | caption | columns | first-column row labels", ""]
        for b in S["books"]:
            if b not in m:
                continue
            L.append(f"## {b}")
            for t in data[b]:
                if t.get("chapter") not in m[b]:
                    continue
                parts = t.get("parts") or []
                cols = [c for p in parts[:1] for c in p.get("columns", [])]
                stubs = [r[0] for p in parts[:1] for r in p.get("rows", []) if r and r[0] and r[0] != '"'][:8]
                L.append(" | ".join([b, t["id"], cut(t.get("chapter"), 30), ",".join(t.get("printed_pages") or []),
                                     cut((f"Table {t['table_no']}. " if t.get('table_no') else "") + (t.get("title") or ""), 110),
                                     cut(t.get("caption_extra"), 80), cut("; ".join(cols), 160), cut("; ".join(stubs), 120)]))
        with open(os.path.join(HERE, "listings", f"{s}--{slug(top)}.txt"), "w", encoding="utf-8") as fh:
            fh.write("\n".join(L) + "\n")
