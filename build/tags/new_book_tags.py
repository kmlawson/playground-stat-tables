"""Controlled tags for a newly published book (user, 2026-10-27).

  python3 build/tags/new_book_tags.py prepare <slug> [--prior slug,slug,...] [--size 40]
      Writes build/tags/runs/new-<slug>/batches/bNN.json: one compact record per table of data/<slug>.json
      (title, English title/description, chapter, part labels, columns, row labels, footnotes, caption) plus
      `prior`: the saved assignment of a table with the same normalised title in an earlier edition, if any.
  python3 build/tags/new_book_tags.py apply <slug>
      Reads build/tags/runs/new-<slug>/results/bNN.json ([{"key", "topics", "tags", "flags"}]), checks every key,
      ID and limit against vocabulary.json, and saves the records in published/assignments.json
      (stage "new-book-full-content"). Run build_tags.py (or build_site.py) afterwards.

Classification agents follow README.md (rules) and CLASSIFICATION.md (later decisions): 0-2 topics, 0-3 detailed
tags, `text-tables` only for textual tables; only IDs from vocabulary.json; empty when no term fits.
"""
import json, re, sys, unicodedata
from pathlib import Path

SITE = Path(__file__).resolve().parents[2]
TAGS = SITE / "build" / "tags"
ASSIGN = TAGS / "published" / "assignments.json"


def read(p):
    return json.loads(Path(p).read_text(encoding="utf-8"))


def write(p, data):
    Path(p).parent.mkdir(parents=True, exist_ok=True)
    Path(p).write_text(json.dumps(data, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")


def norm(title):
    t = unicodedata.normalize("NFKC", str(title or ""))
    return re.sub(r"[\s・、，,()（）\[\]［］]", "", t)


def compact(t, en):
    parts = []
    for p in t.get("parts", []):
        rows = p.get("rows", [])
        labels = [r[0] for r in rows if r]
        parts.append({"label": p.get("label"), "columns": p.get("columns", []),
                      "row_labels": labels[:40] + (["…"] if len(labels) > 40 else []), "rows": len(rows)})
    return {"table_no": t.get("table_no"), "title": t.get("title"), "en": en, "chapter": t.get("chapter"),
            "caption_extra": t.get("caption_extra", ""), "parts": parts, "footnotes": (t.get("footnotes") or [])[:6]}


def prepare(slug, prior, size):
    tables = read(SITE / "data" / f"{slug}.json")
    tr_path = SITE / "build" / "translations" / f"{slug}.json"
    tr = read(tr_path) if tr_path.exists() else {}
    rows = read(ASSIGN)["assignments"]
    by_title = {}
    for ps in prior:
        for t in read(SITE / "data" / f"{ps}.json"):
            a = rows.get(f"{ps}:{t['id']}")
            if a and (a.get("topics") or a.get("tags")):
                by_title.setdefault(norm(t.get("title")), {"key": f"{ps}:{t['id']}", "topics": a.get("topics", []),
                                                           "tags": a.get("tags", []), "flags": a.get("flags", [])})
    recs = []
    for t in tables:
        r = {"key": f"{slug}:{t['id']}", **compact(t, tr.get(t["id"]) or t.get("en"))}
        if norm(t.get("title")) in by_title:
            r["prior"] = by_title[norm(t.get("title"))]
        recs.append(r)
    out = TAGS / "runs" / f"new-{slug}"
    for i in range(0, len(recs), size):
        write(out / "batches" / f"b{i // size + 1:02d}.json", recs[i:i + size])
    print(f"{slug}: {len(recs)} tables, {sum('prior' in r for r in recs)} with a prior-edition match, "
          f"{(len(recs) + size - 1) // size} batches in {out}/batches")


def apply(slug):
    voc = read(TAGS / "vocabulary.json")
    T, D, F = ({x["id"] for x in voc[k]} if isinstance(voc[k], list) else set(voc[k]) for k in ("topics", "tags", "flags"))
    keys = {f"{slug}:{t['id']}" for t in read(SITE / "data" / f"{slug}.json")}
    out = TAGS / "runs" / f"new-{slug}"
    got, bad = {}, []
    for f in sorted((out / "results").glob("b*.json")):
        for r in read(f):
            k = r.get("key")
            tp, tg, fl = r.get("topics") or [], r.get("tags") or [], r.get("flags") or []
            errs = [x for x in tp if x not in T] + [x for x in tg if x not in D] + [x for x in fl if x not in F]
            if k not in keys: errs.append("unknown key")
            if len(tp) > 2 or len(tg) > 3 or len(set(tp)) < len(tp) or len(set(tg)) < len(tg): errs.append("limits")
            if errs: bad.append((f.name, k, errs)); continue
            got[k] = {"topics": tp, "tags": tg, "flags": fl, "stage": "new-book-full-content", "flag_status": "reviewed"}
    for b in bad: print("REJECTED", *b)
    missing = sorted(keys - set(got))
    if missing: print("no result for", len(missing), missing[:10])
    if bad or missing:
        sys.exit("fix the results first; nothing saved")
    data = read(ASSIGN)
    data["assignments"] = {k: v for k, v in data["assignments"].items() if not k.startswith(slug + ":")} | got
    ASSIGN.write_text(json.dumps(data, ensure_ascii=False, separators=(",", ":")) + "\n", encoding="utf-8")
    n = sum(1 for v in got.values() if v["topics"])
    print(f"{slug}: saved {len(got)} records ({n} with a topic, {sum(1 for v in got.values() if v['tags'])} with detailed tags)")


if __name__ == "__main__":
    cmd, slug = sys.argv[1], sys.argv[2]
    args = sys.argv[3:]
    prior = args[args.index("--prior") + 1].split(",") if "--prior" in args else []
    size = int(args[args.index("--size") + 1]) if "--size" in args else 40
    prepare(slug, prior, size) if cmd == "prepare" else apply(slug)
