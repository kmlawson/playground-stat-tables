#!/usr/bin/env python3
"""Build the pages for the books added on the far-east-1941 branch.

Unlike build_site.py, this touches only its own books: for each book in BOOKS it reads
<src>/_work/{tables,directory,chronology}/*.json and writes <slug>/index.html,
<slug>/directory.html, <slug>/chronology.html and data/<slug>*.json. It then inserts one card
per book into the landing page (index.html) between the EXTRA-BOOKS markers, leaving the other
cards alone.
"""
import json, glob, os, re, html

import build_site
from build_site import TEMPLATE
from dir_template import DIRTEMPLATE

HERE = os.path.dirname(os.path.abspath(__file__))
FAR_EAST = os.path.dirname(HERE)

BOOKS = [
    {"slug": "far-east-1941", "src": FAR_EAST, "title": "The Far East Year Book 1941",
     "publisher": "Japan-Manchoukuo Year Book Co., Tokyo, 1941",
     "blurb": "Japan, its colonies (Chosen, Taiwan, Karafuto, the South Sea Islands), Manchoukuo and occupied China, with shorter sections on the Philippines, French Indo-China, Thailand, British Malaya, the Netherlands East Indies and British Borneo.",
     "source": "LLM-transcribed from 581 photographs of the printed volume (two-page spreads).",
     "in_progress": True, "scan": None, "item": None},
]

CARD_START, CARD_END = "<!-- EXTRA-BOOKS -->", "<!-- /EXTRA-BOOKS -->"


def num_key(name):
    m = re.search(r"(\d+)(?:_(\d+))?\.json$", name)
    return (int(m.group(1)), int(m.group(2) or 0)) if m else (0, 0)


def read_dir(book, sub):
    out = []
    for f in sorted(glob.glob(os.path.join(book["src"], "_work", sub, "*.json")), key=num_key):
        with open(f, encoding="utf-8") as fh:
            d = json.load(fh)
        d["file"] = os.path.basename(f)
        d["id"] = d["file"][:-5]
        out.append(d)
    return out


def scan_link(book, leaf):
    m = re.match(r"p(\d+)$", leaf or "")
    if book["scan"] and m:
        return {"label": f"scan page {int(m.group(1))}", "url": book["scan"].format(leaf=int(m.group(1)))}
    return {"label": ("photo " if leaf.startswith("IMG") else "page image ") + leaf, "url": None}


def write_list_page(book, entries, kind, count):
    """Directory or chronology page, both rendered with the directory template."""
    data = json.dumps(entries, ensure_ascii=False).replace("</", "<\\/")
    doc = (DIRTEMPLATE.replace("__DATA__", data).replace("__COUNT__", f"{count:,}")
           .replace("__BOOK__", html.escape(book["title"])).replace("__SLUG__", book["slug"])
           .replace("__PROG__", " · <i>transcription in progress</i>" if book.get("in_progress") else ""))
    if kind == "chronology":
        doc = (doc.replace("· Directories", "· Chronologies").replace("-directory.json", "-chronology.json")
               .replace(" entries", " events").replace("Filter names, places, firms, words…", "Filter dates, names, places, words…")
               .replace("> names only<", "> dates only<").replace("These entries were", "These events were"))
    name = "directory.html" if kind == "directory" else "chronology.html"
    with open(os.path.join(HERE, book["slug"], name), "w", encoding="utf-8") as fh:
        fh.write(doc)
    with open(os.path.join(HERE, "data", f"{book['slug']}-{kind}.json"), "w", encoding="utf-8") as fh:
        json.dump(entries, fh, ensure_ascii=False, indent=1)


def build(book):
    os.makedirs(os.path.join(HERE, book["slug"]), exist_ok=True)
    tables = read_dir(book, "tables")
    for t in tables:
        t["scans"] = [scan_link(book, im) for im in (t.get("images") or [t.get("image")])]
    dirs, chrons = read_dir(book, "directory"), read_dir(book, "chronology")

    dentries = []
    for d in dirs:
        leaf = d.get("leaf") or d["id"]
        s = scan_link(book, leaf)
        for e in d.get("entries", []):
            sec = e.get("section") or ""
            dentries.append({"a": d.get("appendix") or "", "s": sec.title() if sec.isupper() else sec,
                             "n": (e.get("name") or "").rstrip(" ,."), "t": e.get("text") or "",
                             "p": e.get("page") or ", ".join(d.get("printed_pages") or []),
                             "l": s["label"], "u": s["url"]})
    cevents = []
    for c in chrons:
        s = scan_link(book, c.get("image") or c["id"])
        head = " — ".join(x for x in (c.get("chapter"), c.get("title")) if x)
        for e in c.get("events", []):
            cevents.append({"a": head, "s": "", "n": e.get("date") or "", "t": e.get("text") or "",
                            "p": e.get("page") or ", ".join(c.get("printed_pages") or []),
                            "l": s["label"], "u": s["url"]})

    links = []
    if dentries:
        write_list_page(book, dentries, "directory", len(dentries))
        links.append('<a href="directory.html" style="color:inherit">Directories</a>')
    if cevents:
        write_list_page(book, cevents, "chronology", len(cevents))
        links.append('<a href="chronology.html" style="color:inherit">Chronologies</a>')

    n, c = len(tables), build_site.cells(tables)
    if tables:
        clean = [{k: v for k, v in t.items() if k != "file"} for t in tables]
        with open(os.path.join(HERE, "data", book["slug"] + ".json"), "w", encoding="utf-8") as fh:
            json.dump(clean, fh, ensure_ascii=False, indent=1)
        data = json.dumps(clean, ensure_ascii=False).replace("</", "<\\/")
        doc = (TEMPLATE.replace("__DATA__", data).replace("__COUNT__", str(n)).replace("__CELLS__", f"{c:,}")
               .replace("__BOOK__", html.escape(book["title"])).replace("__SLUG__", book["slug"])
               .replace("__SOURCE__", html.escape(book["source"])))
        if links:
            doc = doc.replace('style="color:inherit">JSON</a>', 'style="color:inherit">JSON</a> · ' + " · ".join(links), 1)
        with open(os.path.join(HERE, book["slug"], "index.html"), "w", encoding="utf-8") as fh:
            fh.write(doc)
    print(f"{book['slug']}: {n} tables, {c:,} cells, {len(dentries)} directory entries, {len(cevents)} chronology events")
    return n, c, len({t.get("chapter") for t in tables}), len(dentries), len(cevents)


def card(book, n, c, ch, nd, nc):
    stat = f"<b>{n}</b> tables · <b>{c:,}</b> cells · {ch} chapters" if n else "<i>transcription in progress</i>"
    if nd:
        stat += f" · <b>{nd:,}</b> directory entries"
    if nc:
        stat += f" · <b>{nc:,}</b> chronology events"
    if n and book.get("in_progress"):
        stat += " · <i>transcription in progress</i>"
    link = f'<a class="go" href="{book["slug"]}/">Browse tables →</a>' if n else ""
    if nd:
        link += f' <a class="go" href="{book["slug"]}/directory.html" style="margin-left:14px">Directories →</a>'
    if nc:
        link += f' <a class="go" href="{book["slug"]}/chronology.html" style="margin-left:14px">Chronologies →</a>'
    item = f' · <a href="{book["item"]}">original scan</a>' if book.get("item") else ""
    gaps = f'<div class="src">{html.escape(book["gaps"])}</div>' if book.get("gaps") and n else ""
    return (f'<article><h2>{html.escape(book["title"])}</h2><div class="pub">{html.escape(book["publisher"])}</div>\n'
            f'<p>{html.escape(book["blurb"])}</p><div class="stat">{stat}</div>'
            f'<div class="src">{html.escape(book["source"])}{item}</div>{gaps}{link}</article>')


def main():
    os.makedirs(os.path.join(HERE, "data"), exist_ok=True)
    cards = [card(b, *build(b)) for b in BOOKS]
    p = os.path.join(HERE, "index.html")
    with open(p, encoding="utf-8") as fh:
        page = fh.read()
    block = CARD_START + "\n" + "\n".join(cards) + "\n" + CARD_END
    if CARD_START in page:
        page = re.sub(re.escape(CARD_START) + ".*?" + re.escape(CARD_END), lambda m: block, page, flags=re.S)
    else:
        page = page.replace('</div>\n<div class="llmwarn"', block + '\n</div>\n<div class="llmwarn"', 1)
    with open(p, "w", encoding="utf-8") as fh:
        fh.write(page)


if __name__ == "__main__":
    main()
