"""Compact previews of a finder's candidate tables, in batches, for the spec-writing agents (TASK.md).

python3 build/finders/population/make_previews.py [--only <slug>]  ->  work/batches/<agent or new-slug>/bNN.txt
"""
import ast, collections, glob, json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
SITE = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
CFG = json.load(open(os.path.join(HERE, "config.json")))
WORK = os.path.join(HERE, "work")


def books():
    src = open(os.path.join(SITE, "build", "build_site.py"), encoding="utf-8").read()
    for node in ast.parse(src).body:
        if isinstance(node, ast.Assign) and any(getattr(t, "id", "") == "BOOKS" for t in node.targets):
            out = {}
            for el in node.value.elts:
                b = {}
                for k, v in zip(el.keys, el.values):
                    try:
                        b[ast.literal_eval(k)] = ast.literal_eval(v)
                    except ValueError:
                        pass
                if "slug" in b:
                    out[b["slug"]] = b
            return out


CORE = set(CFG["tags"])
KT = re.compile(CFG["title_words"], re.I)
KC = re.compile(CFG["col_words"], re.I)


def wanted(k, t, A):
    """Controlled tags first (build/tags); else a title word in a table of the listed topics (or none); else a column
    word in a table with the listed tags or topics (config.json)."""
    v = A.get(k, {"tags": [], "topics": []})
    if CORE & set(v["tags"]):
        return True
    title = t.get("title") or ""
    if KT.search(title) and (set(v["topics"]) & set(CFG["title_topics"]) or not v["topics"]):
        return True
    cols = " ".join(" ".join(map(str, p.get("columns") or [])) for p in t["parts"])
    return bool(KC.search(cols) and (set(CFG["col_tags"]) & set(v["tags"]) or set(CFG["col_topics"]) & set(v["topics"])))


def cell(v, n=28):
    s = re.sub(r"\s+", " ", str(v if v is not None else "")).strip()
    return s if len(s) <= n else s[:n - 1] + "…"


def preview(slug, b, t, tr):
    yr = re.search(r"\d{4}", b.get("title", "")) if b else None
    out = [f"### {slug}:{t['id']} | {b.get('title', slug) if b else slug} | ch: {cell(t.get('chapter'), 40)} | p.{','.join(t.get('printed_pages') or [])}"]
    out.append("T: " + cell(t.get("title"), 160))
    if tr and tr.get("t") and tr["t"] != t.get("title"):
        out.append("EN: " + cell(tr["t"], 140))
    if t.get("caption_extra"):
        out.append("CAP: " + cell(t["caption_extra"], 160))
    for pi, p in enumerate(t.get("parts") or []):
        rows = p.get("rows") or []
        cols = p.get("columns") or []
        out.append(f"part {pi}{(' [' + cell(p.get('label'), 50) + ']') if p.get('label') else ''} ({len(rows)} rows) cols: "
                   + " | ".join(f"[{i}]{cell(c, 36)}" for i, c in enumerate(cols)))
        full = set(range(min(2, len(rows)))) | ({len(rows) - 1} if rows else set())
        for ri, r in enumerate(rows):
            if ri in full:
                out.append(f" r{ri}: " + " | ".join(cell(x, 18) for x in r))
            elif ri < 70:
                out.append(f" r{ri}: {cell(r[0] if r else '', 26)}")
            elif ri == 70:
                out.append(f" … r70–r{len(rows) - 2}: " + ", ".join(cell(x[0] if x else '', 12) for x in rows[70:-1][:30]) + (" …" if len(rows) > 101 else ""))
    for fn in (t.get("footnotes") or [])[:3]:
        out.append("FN: " + cell(fn, 140))
    return "\n".join(out)


def candidates():
    """[(slug, "slug:id", preview text)] for every table this finder wants (config.json)."""
    B = books()
    A = json.load(open(os.path.join(SITE, "build/tags/published/assignments.json")))["assignments"]
    items = []
    for f in sorted(glob.glob(os.path.join(SITE, "data", "*.json"))):
        slug = os.path.basename(f)[:-5]
        if slug.endswith("-toc") or slug not in B:
            continue
        d = json.load(open(f))
        if not isinstance(d, list):
            continue
        trp = os.path.join(SITE, "build/translations", slug + ".json")
        TR = json.load(open(trp)) if os.path.exists(trp) else {}
        for t in d:
            if "id" not in t or "parts" not in t:
                continue
            k = f"{slug}:{t['id']}"
            if wanted(k, t, A):
                items.append((slug, k, preview(slug, B[slug], t, TR.get(t["id"]))))
    return items


def write_batches(d, previews, size=40):
    """Previews in files of `size` tables for one agent each: d/b01.txt, b02.txt …"""
    os.makedirs(d, exist_ok=True)
    for i in range(0, len(previews), size):
        open(os.path.join(d, "b%02d.txt" % (i // size + 1)), "w").write("\n\n".join(previews[i:i + size]) + "\n")
    return (len(previews) + size - 1) // size


def main():
    items = candidates()
    os.makedirs(WORK, exist_ok=True)
    if len(sys.argv) > 2 and sys.argv[1] == "--only":
        # one new book: build/population/work/batches/new-<slug>/bNN.txt, for one agent (specs go to specs/new-<slug>/)
        slug = sys.argv[2]
        d = os.path.join(WORK, "batches", "new-" + slug)
        os.makedirs(d, exist_ok=True)
        ps = [p for s_, k, p in items if s_ == slug]
        for i in range(0, len(ps), 40):
            open(os.path.join(d, "b%02d.txt" % (i // 40 + 1)), "w").write("\n\n".join(ps[i:i + 40]) + "\n")
        print(len(ps), "candidate tables ->", d)
        return
    json.dump([k for _, k, _ in items], open(os.path.join(WORK, "cands.json"), "w"))
    # six agents, whole books kept together, balanced by preview size
    by = collections.OrderedDict()
    for slug, k, p in items:
        by.setdefault(slug, []).append(p)
    n_ag = int(sys.argv[1]) if len(sys.argv) > 1 and sys.argv[1].isdigit() else 6
    load = [0] * n_ag
    assign = [[] for _ in range(n_ag)]
    for slug, ps in sorted(by.items(), key=lambda x: -sum(map(len, x[1]))):
        i = load.index(min(load))
        assign[i].append(slug)
        load[i] += sum(map(len, ps))
    for i, slugs in enumerate(assign):
        d = os.path.join(WORK, "batches", "A%d" % (i + 1))
        os.makedirs(d, exist_ok=True)
        ps = [p for s in sorted(slugs) for p in by[s]]
        cur, bn, size = [], 1, 0
        for p in ps:
            cur.append(p)
            size += len(p)
            if size > 45000:
                open(os.path.join(d, "b%02d.txt" % bn), "w").write("\n\n".join(cur) + "\n")
                cur, bn, size = [], bn + 1, 0
        if cur:
            open(os.path.join(d, "b%02d.txt" % bn), "w").write("\n\n".join(cur) + "\n")
        print("A%d" % (i + 1), len(ps), "tables", load[i] // 1000, "KB", bn, "batches")
    print(len(items), "candidates")


if __name__ == "__main__":
    main()
