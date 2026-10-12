#!/usr/bin/env python3
"""Write the Pagefind indexes used by search.html:

  pagefind/          every table (title, headings, cells, notes), directory entry and chronology event
  pagefind-titles/   the same records, but indexed on table titles, entry names and chronology dates/headings only

Records come from the committed data/*.json, so any machine can rebuild the indexes. Each record carries filters
for kind (t = table, w = Who's Who, d = other directory, c = chronology), region and every year its edition covers.

Search text is prepared the way search.html prepares a query: Chinese/Japanese characters are separated by spaces
(Pagefind would otherwise treat a whole run of characters as one word), lines are joined with " ¶ ", and when folding variant forms
(fold.js: kyūjitai/shinjitai, traditional/simplified) or stripping accents changes a line, the folded line is added
as well, so a search finds 國 and 国, 臺灣 and 台湾, Kōbe and Kobe alike.

Run after build_site.py:  uv run --with "pagefind[extended]" build/build_search.py
"""
import asyncio, json, os, re, shutil, unicodedata
from urllib.parse import quote
from pagefind.index import PagefindIndex, IndexConfig
import build_site as bs
import inspect, textwrap
import pagefind.service as _svc

# pagefind's Python service sleeps 0.1 s before reading each response, which caps indexing at ten records a second;
# use the same reader without the sleep.
_src = textwrap.dedent(inspect.getsource(_svc.PagefindService._wait_for_responses)).replace("await asyncio.sleep(0.1)", "pass")
assert "pass" in _src
_ns = {}
exec(_src, _svc.__dict__, _ns)
_svc.PagefindService._wait_for_responses = _ns["_wait_for_responses"]

ROOT = bs.HERE
WHO = re.compile(r"who.?s who|contemporary worthies", re.I)
CJK = r"々〆぀-ヿ㐀-䶿一-鿿豈-﫿\U00020000-\U0002fa1f"
CJK_RE = re.compile(f"([{CJK}])")


def load_fold():
    src = open(os.path.join(ROOT, "fold.js"), encoding="utf-8").read()
    groups = re.search(r'const FOLD_GROUPS="([^"]*)"', src).group(1).split("|")
    return {c: g[0] for g in groups for c in g}


FOLD = load_fold()


def fold(s):
    """search.html's norm(): drop accents, lower-case, fold variant characters."""
    s = "".join(c for c in unicodedata.normalize("NFD", s) if not unicodedata.combining(c)).lower()
    return "".join(FOLD.get(c, c) for c in s)


def space(s):
    return re.sub(r"\s+", " ", CJK_RE.sub(r" \1 ", s)).strip()


def prep(lines):
    """Index text for a list of lines: each line spaced, plus its folded form when that differs."""
    out, extra = [], []
    for ln in lines:
        ln = str(ln or "").strip()
        if not ln:
            continue
        out.append(space(ln))
        f = fold(ln)
        if f != ln.lower():
            extra.append(space(f))
    # Pagefind keeps the text but not line breaks: lines are joined with " ¶ " and the folded copies follow " ¶¶ ",
    # so search.html can show the matching original lines (table rows) as the snippet.
    return " ¶ ".join(out) + (" ¶¶ " + " ¶ ".join(extra) if extra else "")


def hide(s):
    """Pagefind searches metadata too. Values that must not be found by a search (printed page numbers, the leaf part
    of a scan link) are stored as Private Use Area characters, which no one types; search.html shifts them back."""
    return "".join(chr(0xF0000 + ord(c)) for c in str(s or ""))


def scan_leaf(b, url):
    """The part of a scan link that varies within a book (search.html rebuilds the link from the book's template)."""
    tpl = b.get("scan") or ""
    if not url or not tpl:
        return None
    if "{leaf}" not in tpl:
        return "" if url == tpl else None
    pre, suf = tpl.split("{leaf}", 1)
    if url.startswith(pre) and url.endswith(suf):
        return url[len(pre):len(url) - len(suf)]
    return None


def years(b):
    y1, y2 = bs.years_of(b)
    return [str(y) for y in range(y1, y2 + 1)] if y1 else []


def table_records(b, t):
    lab = (f'Table {t["table_no"]}. ' if t.get("table_no") else "") + (t.get("title") or "")
    en = (t.get("en") or {}).get("t") or ""
    rows = [" | ".join(map(str, r)) for p in t.get("parts") or [] for r in p.get("rows") or []]
    heads = [x for p in t.get("parts") or [] for x in [p.get("label")] + list(p.get("columns") or [])]
    full = [lab, en, t.get("chapter"), t.get("caption_extra"), t.get("context")] + heads + rows + list(t.get("footnotes") or [])
    scan = next((s.get("url") for s in t.get("scans") or [] if s.get("url")), "")
    meta = {"title": lab or "(untitled table)", "c": t.get("chapter") or "", "p": hide(", ".join(t.get("printed_pages") or []))}
    leaf = scan_leaf(b, scan)
    if leaf is not None:
        meta["n"] = hide(leaf)
    if en:
        meta["e"] = en
    return f'book/{b["slug"]}/#{quote(t["id"])}', meta, prep(full), prep([lab, en])


def entry_records(b, e, page, i, kind):
    meta = {"title": e.get("n") or "", "t": e.get("t") or "", "a": e.get("a") or "", "x": e.get("s") or "", "p": hide(e.get("p"))}
    leaf = scan_leaf(b, e.get("u"))
    if leaf is not None:
        meta["n"] = hide(leaf)
    full = [e.get("n"), e.get("t"), e.get("a"), e.get("s")]
    titles = [e.get("n")] + ([e.get("a")] if kind == "c" else [])
    q = {"q": e.get("n") or ""}
    url = f'book/{b["slug"]}/{page}#' + "&".join(f"{k}={quote(v)}" for k, v in q.items()) + f"&e={i}"
    return url, meta, prep(full), prep(titles)


def title_meta(m):
    """Pagefind also searches metadata, so the titles index keeps only fields that are titles or names, or that hold
    no searchable words (printed page, scan leaf): a names-only search must not match an entry's text, place or
    chapter, so results from this index are shown without those."""
    return {k: v for k, v in m.items() if k in ("title", "e", "p", "n")}


def records():
    for b in bs.BOOKS:
        f = {"region": [bs.group_of(b)], "year": years(b)}
        path = os.path.join(ROOT, "data", b["slug"] + ".json")
        if not os.path.exists(path):
            continue
        for t in json.load(open(path, encoding="utf-8")):
            yield (*table_records(b, t), {**f, "kind": ["t"]})
        for kind_file, page in (("directory", "directory.html"), ("chronology", "chronology.html")):
            p = os.path.join(ROOT, "data", f'{b["slug"]}-{kind_file}.json')
            if not os.path.exists(p):
                continue
            for i, e in enumerate(json.load(open(p, encoding="utf-8"))):
                kind = "c" if kind_file == "chronology" else ("w" if WHO.search(e.get("a") or "") else "d")
                yield (*entry_records(b, e, page, i, kind), {**f, "kind": [kind]})


async def main():
    recs = list(records())
    for name, col in (("pagefind", 2), ("pagefind-titles", 3)):
        out = os.path.join(ROOT, name)
        if os.path.isdir(out):
            shutil.rmtree(out)
        async with PagefindIndex(config=IndexConfig(force_language="en", output_path=out)) as idx:
            todo = [r for r in recs if r[col]]
            for k in range(0, len(todo), 2000):  # one request at a time is latency-bound; send them in batches
                await asyncio.gather(*(idx.add_custom_record(url=r[0], meta=r[1] if col == 2 else title_meta(r[1]), content=r[col], language="en",
                                                             filters={f: v for f, v in r[4].items() if v}) for r in todo[k:k + 2000]))
        # Pagefind's own UI bundles are not used by search.html
        for f in os.listdir(out):
            if f.startswith(("pagefind-ui", "pagefind-modular-ui", "pagefind-component-ui")):
                os.remove(os.path.join(out, f))
        n = sum(len(fs) for _, _, fs in os.walk(out))
        size = sum(os.path.getsize(os.path.join(d, x)) for d, _, fs in os.walk(out) for x in fs)
        print(f"{name}: {len(recs):,} records, {n:,} files, {size / 1e6:.1f} MB")


if __name__ == "__main__":
    asyncio.run(main())
