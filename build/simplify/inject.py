"""Add the "Simplified characters" script (simp.js, built by make_simp_table.py) to every page of the site.

Run at the end of build_site.py (and safe to run on its own: `python3 build/simplify/inject.py`). Idempotent.
Pages of Chinese books (book/china-*/, inspect/books/china-*) get data-cjk="zh" on <html> so simp.js uses the
Chinese simplified table there; elsewhere it uses the Japanese new-forms table, or the table of the book a row links to.
"""
import os, re, json, glob

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SKIP_DIRS = {"pagefind", "pagefind-titles", "_search.noindex", "build", "docs", "node_modules", ".git", "__pycache__", "downloads", "data"}
ZH = re.compile(r"(?:^|/)(?:book|inspect/books)/china-")


HAN = re.compile(r"[\u3400-\u9fff\uf900-\ufaff\U00020000-\U0003134f]")


def write_js(root=ROOT):
    """simp.js = simp_template.js + the tables cut down to the characters the site actually shows."""
    used = set()
    files = glob.glob(os.path.join(root, "data", "**", "*.json"), recursive=True)
    for dp, dns, fns in os.walk(root):
        rel = os.path.relpath(dp, root)
        if rel != "." and rel.split(os.sep)[0] in SKIP_DIRS:
            dns[:] = []
            continue
        files += [os.path.join(dp, f) for f in fns if f.endswith(".html")]
    for f in files:
        with open(f, encoding="utf-8", errors="ignore") as fh:
            used.update(HAN.findall(fh.read()))
    here = os.path.dirname(os.path.abspath(__file__))
    tables = json.load(open(os.path.join(here, "tables.json"), encoding="utf-8"))
    parts, counts = [], {}
    for mode in ("zh", "ja"):
        m = {k: v for k, v in sorted(tables[mode].items()) if k in used}
        counts[mode] = len(m)
        parts.append(f'{mode}:[{json.dumps("".join(m), ensure_ascii=False)},{json.dumps("".join(m.values()), ensure_ascii=False)}]')
    js = open(os.path.join(here, "simp_template.js"), encoding="utf-8").read().replace("__TABLES__", "{" + ",".join(parts) + "}")
    with open(os.path.join(root, "simp.js"), "w", encoding="utf-8") as fh:
        fh.write(js)
    return counts


def inject(root=ROOT):
    n = 0
    for dp, dns, fns in os.walk(root):
        rel_dir = os.path.relpath(dp, root)
        if rel_dir != "." and rel_dir.split(os.sep)[0] in SKIP_DIRS:
            dns[:] = []
            continue
        for fn in fns:
            if not fn.endswith(".html"):
                continue
            path = os.path.join(dp, fn)
            rel = os.path.relpath(path, root).replace(os.sep, "/")
            with open(path, encoding="utf-8") as fh:
                doc = fh.read()
            if "</head>" not in doc:
                continue
            new = doc
            if "simp.js" not in new:
                up = "../" * rel.count("/")
                new = new.replace("</head>", f'<script src="{up}simp.js"></script></head>', 1)
            if ZH.search(rel) and "data-cjk=" not in new[:400]:
                new = re.sub(r"<html\b", '<html data-cjk="zh"', new, count=1)
            if new != doc:
                with open(path, "w", encoding="utf-8") as fh:
                    fh.write(new)
                n += 1
    return n


if __name__ == "__main__":
    print(f"simp.js tables: {write_js()}; script added to {inject()} pages")
