#!/usr/bin/env python3
"""Build the stat-tables site: a landing page plus one table browser per book.

For each book in BOOKS, reads <book dir>/_work/tables/*.json and writes
<slug>/index.html (self-contained) and data/<slug>.json. Books without tables yet are listed
as "in progress" on the landing page. Scan links point to the online scan where one exists.
"""
import json, glob, os, re, html

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

BOOKS = [
    {"slug": "japan-1930", "dir": "Japan_Year_Book_1930", "title": "The Japan Year Book 1930",
     "publisher": "The Japan Year Book Office, Tokyo, 1930",
     "blurb": "Comprehensive English-language reference on the Japanese Empire in 1930, covering geography, population, government, defence, education, labour, justice, communications, railways, shipping, banking, finance, agriculture, industry, trade, the six premier cities and the colonies.",
     "source": "LLM-transcribed from the Internet Archive scan.",
     "gaps": "Advertisements and the Index contain no tables. The Who's Who, Business Directory and Learned & Social Institutions (Appendices A–C) are transcribed as entries on the Who's Who & Directories page. The shop and restaurant lists in Appendix D are included; the physicians' lists are not. On p. 439 the right edge of the scan cuts off the 1927 export figures, so those cells are blank.",
     "scan": "https://archive.org/details/japan-year-book-1930/page/n{leaf}/mode/1up",
     "item": "https://archive.org/details/japan-year-book-1930", "dir_in_progress": True},
    {"slug": "japan-1939-40", "dir": "Japan_Year_Book_1939-40", "title": "The Japan Year Book 1939-40",
     "publisher": "The Foreign Affairs Association of Japan, Tokyo, 1939",
     "blurb": "The wartime edition of the standard English-language reference on the Japanese Empire.",
     "source": "LLM-transcribed from the Internet Archive scan.",
     "in_progress": True,
     "scan": "https://archive.org/details/japan-year-book-1939-1940/page/n{leaf}/mode/1up",
     "item": "https://archive.org/details/japan-year-book-1939-1940", "dir_label": "Clubs & Societies Directory", "dir_in_progress": True},
    {"slug": "korea-1929-30", "dir": "Korea_Annual_Report_1929-30",
     "title": "Annual Report on Administration of Chosen 1929-30",
     "publisher": "Government-General of Chosen, Keijo, 1931",
     "blurb": "The Government-General's English-language annual report on colonial Korea: population, finance, banking, trade, education, industry, communications, police, public health and local administration.",
     "source": "LLM-transcribed from the Internet Archive scan.",
     "gaps": "The Internet Archive scan is missing the text page beside each photo plate (printed pp. 66, 74, 82, 92, 96, 100, 104, 140, 152 and 172), as well as the appendix tables of weights and measures and of governors. On p. 13 the Total column is in a different typeface from the rest of the table, which may mean the scan was retouched.",
     "scan": "https://archive.org/details/annualreportonreformsandprogressinchosenkorea192930/page/n{leaf}/mode/1up",
     "item": "https://archive.org/details/annualreportonreformsandprogressinchosenkorea192930"},
    {"slug": "manchoukuo-1942", "dir": ".", "title": "The Manchoukuo Year Book 1942",
     "publisher": "Manchoukuo Year Book Co., Hsinking, 1942",
     "blurb": "Official English-language yearbook of Manchukuo: geography, population, finance, banking, trade, agriculture, mining, industry, transport, labour, education and more.",
     "source": "LLM-transcribed from 498 photographs of the printed volume (two-page spreads).",
     "gaps": "Pages 502–503 (Mining) and 966–967 (Index) were not photographed. Gaps in table numbering (e.g. Agriculture Tables 2–3 and 11–17) are in the printed book itself.",
     "scan": None, "dir_in_progress": True, "hide_images": True},
    {"slug": "far-east-1941", "root": os.path.join(os.path.dirname(ROOT), "The Far East Year Book 1941"),
     "title": "The Far East Year Book 1941",
     "publisher": "Japan-Manchoukuo Year Book Co., Tokyo, 1941",
     "blurb": "Japan, its colonies (Chosen, Taiwan, Karafuto, the South Sea Islands), Manchoukuo and occupied China, with shorter sections on the Philippines, French Indo-China, Thailand, British Malaya, the Netherlands East Indies and British Borneo.",
     "source": "LLM-transcribed from 581 photographs of the printed volume (two-page spreads).",
     "in_progress": True, "dir_in_progress": True, "hide_images": True, "scan": None},
]


def dl(slug, suffix):
    """Relative path of a download written by build_downloads.py, or None if it hasn't been built."""
    f = f"downloads/{slug}-{suffix}"
    return f if os.path.exists(os.path.join(HERE, f)) else None


def book_dir(book):
    """Books live beside this repo's parent folder, or at an explicit absolute path ("root")."""
    return book.get("root") or os.path.join(ROOT, book["dir"])


def page_key(t):
    m = re.search(r"(\d+)", t["file"])
    img = int(m.group(1)) if m else 0
    n = int(re.search(r"_(\d+)\.json$", t["file"]).group(1))
    return (img, n)


def load(book):
    tables = []
    for f in sorted(glob.glob(os.path.join(book_dir(book), "_work", "tables", "*.json"))):
        try:  # agents may be writing or merging files while we build
            with open(f, encoding="utf-8") as fh:
                t = json.load(fh)
        except (FileNotFoundError, json.JSONDecodeError):
            print("skipped", f)
            continue
        t["file"] = os.path.basename(f)
        t["id"] = t["file"][:-5]
        tables.append(t)
    tables.sort(key=page_key)
    return tables


def scan_links(book, t):
    ims = t.get("images") or [t.get("image")]
    out = []
    for im in ims:
        m = re.match(r"p(\d+)$", im or "")
        if book["scan"] and m:
            out.append({"label": f"scan leaf {int(m.group(1))}", "url": book["scan"].format(leaf=int(m.group(1)))})
        else:
            out.append({"label": "" if book.get("hide_images") else f"photo {im}", "url": None})
    return out


def cells(tables):
    return sum(len(r) for t in tables for p in t.get("parts", []) for r in p.get("rows", []))


def main():
    os.makedirs(os.path.join(HERE, "data"), exist_ok=True)
    cards = []
    for b in BOOKS:
        b["_dir_n"] = build_directory(b)
        b["_chron_n"] = build_chronology(b)
        tables = load(b)
        for t in tables:
            t["scans"] = scan_links(b, t)
        n, c = len(tables), cells(tables)
        chapters = len({t.get("chapter") for t in tables})
        if tables:
            os.makedirs(os.path.join(HERE, b["slug"]), exist_ok=True)
            clean = [{k: v for k, v in t.items() if k not in ("file",)} for t in tables]
            with open(os.path.join(HERE, "data", b["slug"] + ".json"), "w", encoding="utf-8") as fh:
                json.dump(clean, fh, ensure_ascii=False, indent=1)
            data = json.dumps(clean, ensure_ascii=False).replace("</", "<\\/")
            doc = (TEMPLATE.replace("__DATA__", data).replace("__COUNT__", str(n))
                   .replace("__HIDEIMG__", "true" if b.get("hide_images") else "false")
                   .replace("__XLSX__", f' · <a href="../{dl(b["slug"], "tables.xlsx")}" style="color:inherit" download>Excel (one sheet per table)</a>' if dl(b["slug"], "tables.xlsx") else "")
                   .replace("__CELLS__", f"{c:,}").replace("__BOOK__", html.escape(b["title"]))
                   .replace("__SLUG__", b["slug"]).replace("__SOURCE__", html.escape(b["source"]))
                   .replace("__DIRLINK__", (f'<a class="dirbtn" href="directory.html">{html.escape(b.get("dir_label", "Who\'s Who & Directories"))} · {b["_dir_n"]:,} entries →</a>' if b.get("_dir_n") else "")
                            + (f'<a class="dirbtn" href="chronology.html">Chronologies · {b["_chron_n"]:,} events →</a>' if b.get("_chron_n") else "")))
            with open(os.path.join(HERE, b["slug"], "index.html"), "w", encoding="utf-8") as fh:
                fh.write(doc)
        cards.append((b, n, c, chapters))
        print(f"{b['slug']}: {n} tables, {c:,} cells")
    with open(os.path.join(HERE, "index.html"), "w", encoding="utf-8") as fh:
        fh.write(landing(cards))
    books = [{"slug": b["slug"], "title": b["title"], "dir": bool(b.get("_dir_n"))} for b, n, c, ch in cards if n]
    with open(os.path.join(HERE, "search.html"), "w", encoding="utf-8") as fh:
        fh.write(SEARCH.replace("__BOOKS__", json.dumps(books, ensure_ascii=False)))


def landing(cards):
    items = []
    for b, n, c, ch in cards:
        stat = (f"<b>{n}</b> tables · <b>{c:,}</b> cells · {ch} chapters" if n else "<i>transcription in progress</i>")
        if n and b.get("in_progress"):
            stat += " · <i>transcription in progress</i>"
        link = f'<a class="go dirgo" href="{b["slug"]}/">Browse tables →</a>' if n else ""
        if b.get("_dir_n"):
            stat += f' · <b>{b["_dir_n"]:,}</b> directory entries' + (" (in progress)" if b.get("dir_in_progress") else "")
            link += f' <a class="go dirgo" href="{b["slug"]}/directory.html">{html.escape(b.get("dir_label", "Who's Who & Directories"))} →</a>'
        if b.get("_chron_n"):
            stat += f' · <b>{b["_chron_n"]:,}</b> chronology events'
            link += f' <a class="go dirgo" href="{b["slug"]}/chronology.html">Chronologies →</a>'
        item = f' · <a href="{b["item"]}">original scan</a>' if b.get("item") else ""
        about, dlg = "", ""
        if b.get("gaps") and n:
            about = f'<button class="about" data-about="about-{b["slug"]}">About this volume</button>'
            dlg = (f'<dialog id="about-{b["slug"]}"><h3>{html.escape(b["title"])}</h3><div class="pub">{html.escape(b["publisher"])}</div>'
                   f'<p>{html.escape(b["gaps"])}</p><form method="dialog"><button>Close</button></form></dialog>')
        dls = [(f"data/{b['slug']}.json", "JSON")] if n else []
        for suf, name in (("tables.xlsx", "Excel"), ("directory.md", "Directory (Markdown)"), ("chronology.md", "Chronology (Markdown)")):
            if dl(b["slug"], suf):
                dls.append((dl(b["slug"], suf), name))
        dlhtml = ('<div class="src">Download: ' + " · ".join(f'<a href="{u}" download>{t}</a>' for u, t in dls) + "</div>") if dls else ""
        items.append(f"""<article><h2>{html.escape(b["title"])}</h2><div class="pub">{html.escape(b["publisher"])}</div>
<div class="stat">{stat}</div><div class="src">{html.escape(b["source"])}{item}</div>{dlhtml}<div class="links">{about}{link}</div>{dlg}</article>""")
    return LANDING.replace("__CARDS__", "\n".join(items))


LANDING = r"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>East Asian Statistical Tables</title>
<style>
:root{--bg:#f4f5f3;--panel:#ffffff;--ink:#1b2420;--muted:#5d6a62;--line:#d8ded9;--accent:#1f4a2c;--accent-ink:#ffffff}
@media (prefers-color-scheme: dark){:root:not([data-theme="light"]){--bg:#111814;--panel:#17211b;--ink:#e4ebe6;--muted:#9aa89f;--line:#2c3a31;--accent:#8cc49e;--accent-ink:#0f1a13}}
:root[data-theme="dark"]{--bg:#111814;--panel:#17211b;--ink:#e4ebe6;--muted:#9aa89f;--line:#2c3a31;--accent:#8cc49e;--accent-ink:#0f1a13}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font:16px/1.55 Georgia,"Times New Roman",serif}
.band{background:var(--accent);color:var(--accent-ink)}.band>div{max-width:980px;margin:0 auto;padding:34px 16px 30px}.band h1{font-weight:normal;font-size:30px;margin:0 0 8px}.band .lede{color:var(--accent-ink);opacity:.9;margin:0}
main{max-width:980px;margin:0 auto;padding:26px 16px 60px}
.searchbtn{display:inline-block;background:var(--accent-ink);color:var(--accent);font-weight:bold;padding:9px 16px;border-radius:5px;text-decoration:none;font-size:15px}
.lede{color:var(--muted);max-width:720px}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:18px;margin-top:28px}
article{background:var(--panel);border:1px solid var(--line);border-top:3px solid var(--accent);padding:18px 18px 16px;display:flex;flex-direction:column}
h2{font-size:20px;font-weight:normal;margin:0 0 4px}.pub{color:var(--muted);font-size:13px;margin-bottom:8px}
.links{margin-top:auto;display:flex;flex-wrap:wrap;gap:8px;align-items:center}.links .dirgo{margin:0}
.about{font:inherit;font-size:13px;background:transparent;color:var(--accent);border:1px solid var(--accent);border-radius:5px;padding:5px 10px;cursor:pointer;flex-basis:100%;max-width:max-content}
dialog{max-width:min(560px,calc(100vw - 32px));border:1px solid var(--line);border-top:4px solid var(--accent);background:var(--panel);color:var(--ink);padding:18px 20px;border-radius:6px}
dialog::backdrop{background:rgba(0,0,0,.45)}dialog h3{margin:0 0 2px;font-weight:normal;font-size:19px}dialog p{font-size:14.5px}
dialog form button{font:inherit;font-size:14px;background:var(--accent);color:var(--accent-ink);border:0;border-radius:5px;padding:6px 14px;cursor:pointer}.stat{font-size:14px;margin-bottom:6px}.src{font-size:12.5px;color:var(--muted);margin-bottom:12px}
a{color:var(--accent)}.go{font-size:15px;text-decoration:none;font-weight:bold}.dirgo{display:inline-block;margin:8px 8px 0 0;background:var(--accent);color:var(--accent-ink);padding:6px 12px;border-radius:5px;font-size:14px}
.llmwarn{margin:28px 0 0;padding:12px 14px;border:1px solid #8a5a00;border-left:4px solid #8a5a00;background:var(--panel);font-size:14px}
footer{margin-top:24px;font-size:13px;color:var(--muted);border-top:1px solid var(--line);padding-top:14px}
</style></head><body><div class="band"><div>
<h1>East Asian Statistical Tables, 1929–1942</h1>
<p class="lede">Every statistical table in English-language official yearbooks on Japan and its empire, LLM-transcribed cell by cell from page images. The figures are kept exactly as printed, including the printers' errors. Where a printed total does not add up, a transcriber's note says so, and figures that could not be read are left blank.</p>
<p style="margin:18px 0 0"><a class="searchbtn" href="search.html">Search all books: tables &amp; directories →</a></p>
</div></div>
<main>
<div class="grid">
__CARDS__
</div>
<div class="llmwarn" role="note"><b>Warning:</b> These tables were transcribed by the vision model of Opus 5.5. Before using any of these figures, you must verify specific statistics with the original source which is linked to whenever possible.</div>
<script>document.addEventListener("click",e=>{const b=e.target.closest("[data-about]");if(b){document.getElementById(b.dataset.about).showModal();return}
if(e.target.tagName==="DIALOG")e.target.close()});</script>
<footer>Each table can be downloaded as CSV from its page. Each book can be downloaded whole as an Excel workbook (one sheet per table, with a linked contents sheet) or as JSON; directories are available as Markdown.</footer>
</main></body></html>
"""


TEMPLATE = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>__BOOK__ · Tables</title>
<style>
:root{--bg:#f4f5f3;--panel:#ffffff;--ink:#1b2420;--muted:#5d6a62;--line:#d8ded9;--accent:#1f4a2c;--accent-ink:#ffffff;--hi:#e2ece4;--warn:#8a5a00}
@media (prefers-color-scheme: dark){:root:not([data-theme="light"]){--bg:#111814;--panel:#17211b;--ink:#e4ebe6;--muted:#9aa89f;--line:#2c3a31;--accent:#8cc49e;--accent-ink:#0f1a13;--hi:#1f3527;--warn:#e0a54a}}
:root[data-theme="dark"]{--bg:#111814;--panel:#17211b;--ink:#e4ebe6;--muted:#9aa89f;--line:#2c3a31;--accent:#8cc49e;--accent-ink:#0f1a13;--hi:#1f3527;--warn:#e0a54a}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);font:15px/1.45 Georgia,"Times New Roman",serif}
header{padding:14px 18px;background:var(--accent);color:var(--accent-ink);display:flex;gap:14px;align-items:baseline;flex-wrap:wrap}
header a,header .meta{color:var(--accent-ink)!important;opacity:.88}
header button{background:transparent;color:var(--accent-ink);border-color:currentColor}
header h1{font-size:20px;margin:0;font-weight:normal}
header .meta{color:var(--muted);font-size:13px}
#wrap{display:grid;grid-template-columns:340px 1fr;height:calc(100vh - 56px)}
#side{border-right:1px solid var(--line);display:flex;flex-direction:column;min-height:0}
#side .ctl{padding:10px;border-bottom:1px solid var(--line);display:flex;flex-direction:column;gap:6px}
input,select,button{font:inherit;font-size:14px;padding:6px 8px;border:1px solid var(--line);background:var(--panel);color:var(--ink);border-radius:4px}
button{cursor:pointer}
#list{overflow:auto;flex:1}
#list .ch{position:sticky;top:0;background:var(--bg);cursor:pointer;padding:8px 10px 4px;font-size:12px;letter-spacing:.06em;text-transform:uppercase;color:var(--accent);border-bottom:1px solid var(--line)}
#list a{display:block;padding:6px 10px;border-bottom:1px solid var(--line);color:inherit;text-decoration:none;font-size:14px}
#list a:hover{background:var(--hi)}
#list a.on,#list a.on:hover{background:var(--accent);color:var(--accent-ink);border-left:3px solid var(--accent)}
#list a.on small{color:var(--accent-ink);opacity:.85}
body.kbd #list a:not(.on):hover{background:transparent}
#list a small{color:var(--muted);display:block;font-size:12px}
#main{overflow:auto;padding:18px 22px;min-width:0}
h2{margin:0 0 4px;font-weight:normal;font-size:22px}
.sub{color:var(--muted);font-size:14px;margin-bottom:10px}
.tw{overflow:auto;border:1px solid var(--line);background:var(--panel);margin:8px 0 16px;max-height:70vh}
table{border-collapse:collapse;font-size:13.5px;font-family:"Iowan Old Style",Georgia,serif}
th,td{border:1px solid var(--line);padding:3px 7px;vertical-align:top}
th{position:sticky;top:0;background:var(--panel);text-align:left;font-weight:bold;font-size:12.5px}
th.sortable{cursor:pointer;user-select:none;padding-right:18px;position:sticky}
th.sortable::after{content:"\2195";position:absolute;right:5px;opacity:.3;font-weight:normal}
th.sortable[aria-sort="ascending"]::after{content:"\25B2";opacity:.9}
th.sortable[aria-sort="descending"]::after{content:"\25BC";opacity:.9}
th.sortable:hover{background:var(--hi)}
td.num{text-align:right;font-variant-numeric:tabular-nums;white-space:nowrap}
td.blank{background:repeating-linear-gradient(45deg,transparent 0 4px,var(--hi) 4px 8px)}
tr:hover td{background:var(--hi)}
tr.sec td:first-child{font-weight:bold;font-style:italic}
.part{font-weight:bold;margin-top:12px}
.tbl{padding-bottom:22px;margin-bottom:26px;border-bottom:2px solid var(--line)}
.chhead{font-size:13px;letter-spacing:.06em;text-transform:uppercase;color:var(--accent);margin:0 0 4px}
.chsum{color:var(--muted);font-size:14px;margin-bottom:18px}
.tbl h2 a{color:inherit;text-decoration:none}
.keys{font-size:12px;color:var(--muted)}
.llmwarn{margin:24px 0 8px;padding:12px 14px;border:1px solid var(--warn);border-left:4px solid var(--warn);background:var(--panel);color:var(--ink);font-size:14px}
.notes{font-size:13.5px;color:var(--muted)}
.notes li.warn{color:var(--warn)}
.row{display:flex;gap:8px;flex-wrap:wrap;align-items:center;margin:8px 0}
.scan{display:flex;gap:10px;flex-wrap:wrap;margin-top:10px}
.scan a img{height:160px;border:1px solid var(--line)}
mark{background:var(--hi);color:inherit}
#toggle{margin-left:auto}
.dirbtn{margin-left:auto;background:var(--accent-ink);color:var(--accent)!important;opacity:1!important;font-weight:bold;font-size:14px;padding:6px 14px;border-radius:5px;text-decoration:none;align-self:center}.dirbtn:hover{filter:brightness(.93)}.dirbtn+#toggle,.dirbtn+.dirbtn{margin-left:0}
@media (max-width:760px){#wrap{grid-template-columns:minmax(0,1fr);height:auto}#side,#main{min-width:0;max-width:100vw}#list a{overflow-wrap:anywhere}.tw{max-height:none}header{padding:12px 16px}header h1{font-size:18px}.dirbtn{margin-left:0}#side{border-right:0;border-bottom:1px solid var(--line)}#list{max-height:40vh}#main{padding:14px 16px}}
</style>
</head>
<body>
<header><a href="../" style="text-decoration:none;font-size:14px">← All books</a><h1>__BOOK__</h1>
<span class="meta">__COUNT__ tables · __CELLS__ cells · __SOURCE__ · <a href="../data/__SLUG__.json" style="color:inherit">JSON</a>__XLSX__</span>
__DIRLINK__<button id="toggle" title="Toggle light/dark">◐</button></header>
<div id="wrap">
<nav id="side"><div class="ctl">
<input id="q" type="search" placeholder="Search titles, headings, cells…">
<select id="ch"><option value="">All chapters</option></select>
<label style="font-size:13px;color:var(--muted)"><input type="checkbox" id="flag"> only tables with transcriber warnings</label>
<span class="keys">↑ / ↓ keys: previous / next table</span>
</div><div id="list"></div></nav>
<main id="main"></main>
</div>
<script>
const T=__DATA__;
const HIDEIMG=__HIDEIMG__;
const $=s=>document.querySelector(s);
const esc=s=>String(s??"").replace(/[&<>"]/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]));
const isNum=s=>/^[\s(]*[-—–]?[\d.,]+[)*%]*\s*$/.test(s)||/^[—–-]$/.test(s.trim())||s.trim()==="...";
const warnRe=/not reconcile|unreadable|illegible|uncertain|could not|does not/i;
T.forEach(t=>{t._text=[t.title,t.table_no,t.caption_extra,t.chapter,...(t.parts||[]).flatMap(p=>[p.label,...p.columns,...p.rows.flat()]),...(t.footnotes||[])].join(" ").toLowerCase();
 t._warn=(t.transcriber_notes||[]).some(n=>warnRe.test(n));});
const chapters=[...new Set(T.map(t=>t.chapter||"(no chapter)"))];
chapters.forEach(c=>$("#ch").insertAdjacentHTML("beforeend",`<option>${esc(c)}</option>`));
function label(t){return (t.table_no?`Table ${t.table_no}. `:"")+(t.title||"")+(t.continued?" (continued)":"")}
function renderList(){const q=$("#q").value.trim().toLowerCase(),ch=$("#ch").value,fl=$("#flag").checked;let h="",last=null,n=0;
 T.forEach((t,i)=>{if(ch&&(t.chapter||"(no chapter)")!==ch)return;if(fl&&!t._warn)return;if(q&&!q.split(/\s+/).every(w=>t._text.includes(w)))return;
  const c=t.chapter||"(no chapter)";if(c!==last){h+=`<div class="ch">${esc(c)}</div>`;last=c}
  h+=`<a href="#${t.id}" data-i="${i}">${esc(label(t))}<small>p. ${esc((t.printed_pages||[]).join(", "))}${HIDEIMG?"":" · "+esc(t.image)}${t._warn?" · ⚠":""}</small></a>`;n++});
 $("#list").innerHTML=h||"<p style='padding:10px'>No matches.</p>";mark()}
function hl(s,q){s=esc(s);if(!q)return s;q.split(/\s+/).filter(Boolean).forEach(w=>{s=s.replace(new RegExp("("+w.replace(/[.*+?^${}()|[\]\\]/g,"\\$&")+")","ig"),"<mark>$1</mark>")});return s}
function csv(t){const L=[];(t.parts||[]).forEach(p=>{if(p.label)L.push([p.label]);L.push(p.columns);p.rows.forEach(r=>L.push(r));L.push([])});
 return L.map(r=>r.map(c=>/[",\n]/.test(c??"")?'"'+String(c).replace(/"/g,'""')+'"':(c??"")).join(",")).join("\n")}
function tableHTML(t,q){let h=`<section class="tbl" id="t-${t.id}"><h2><a href="#${t.id}">${hl(label(t),q)}</a></h2><div class="sub">${esc(t.chapter||"")} · printed page${(t.printed_pages||[]).length>1?"s":""} ${esc((t.printed_pages||[]).join(", "))}${HIDEIMG?"":` · ${/^p\d/.test(t.image||"")?"scan leaf":"photo"} ${esc((t.images||[t.image]).join(", "))}`}</div>`;
 if(t.caption_extra)h+=`<div class="sub"><i>${hl(t.caption_extra,q)}</i></div>`;
 (t.parts||[]).forEach(p=>{if(p.label)h+=`<div class="part">${hl(p.label,q)}</div>`;
  h+=`<div class="tw"><table><thead><tr>${p.columns.map((c,j)=>`<th class="sortable" data-col="${j}" title="Click to sort">${hl(c,q)}</th>`).join("")}</tr></thead><tbody>`;
  p.rows.forEach((r,ri)=>{const sec=r.length>1&&r.slice(1).every(c=>c==="");h+=`<tr data-i="${ri}"${sec?' class="sec"':""}>`+r.map((c,j)=>`<td class="${j&&isNum(c)?"num":""}${j&&c===""&&!sec?" blank":""}">${hl(c,q)}</td>`).join("")+"</tr>"});
  h+="</tbody></table></div>"});
 if((t.footnotes||[]).length)h+=`<div class="notes"><b>Printed notes</b><ul>${t.footnotes.map(n=>`<li>${hl(n,q)}</li>`).join("")}</ul></div>`;
 if((t.transcriber_notes||[]).length)h+=`<div class="notes"><b>Transcriber's notes</b><ul>${t.transcriber_notes.map(n=>`<li class="${warnRe.test(n)?"warn":""}">${esc(n)}</li>`).join("")}</ul></div>`;
 h+=`<div class="row"><button data-act="dl" data-id="${t.id}">Download CSV</button><button data-act="cp" data-id="${t.id}">Copy as TSV</button></div>`;
 if(!HIDEIMG)h+=`<div class="sub">Source: ${(t.scans||[]).map(s=>s.url?`<a href="${s.url}" target="_blank" rel="noopener">${esc(s.label)}</a>`:esc(s.label)).join(", ")}</div>`;
 h+=`</section>`;
 return h}
const LLMWARN=`<div class="llmwarn" role="note"><b>Warning:</b> These tables were transcribed by the vision model of Opus 5.5. Before using any of these figures, you must verify specific statistics with the original source which is linked to whenever possible.</div>`;
function filtered(){const q=$("#q").value.trim().toLowerCase(),ch=$("#ch").value,fl=$("#flag").checked;
 return T.filter(t=>(!ch||(t.chapter||"(no chapter)")===ch)&&(!fl||t._warn)&&(!q||q.split(/\s+/).every(w=>t._text.includes(w))))}
let mode="one",cur=null;
function showOne(id){const t=T.find(x=>x.id===id)||T[0];if(!t){$("#main").innerHTML="<p>No tables yet.</p>";return}
 mode="one";cur=t.id;$("#main").innerHTML=tableHTML(t,$("#q").value.trim())+LLMWARN;$("#main").scrollTop=0;
 document.querySelectorAll("#main table").forEach(initSort);mark()}
function showChapter(ch){const q=$("#q").value.trim();const ts=filtered();mode="chapter";cur=null;
 let h=`<div class="chhead">Chapter</div><h2 style="margin-bottom:6px">${esc(ch)}</h2><div class="chsum">${ts.length} table${ts.length===1?"":"s"}${$("#flag").checked||q?" matching the current filters":""}</div>`;
 h+=(ts.map(t=>tableHTML(t,q)).join("")||"<p>No tables match.</p>")+LLMWARN;
 $("#main").innerHTML=h;$("#main").scrollTop=0;document.querySelectorAll("#main table").forEach(initSort);
 if(enterAt&&ts.length){const t=enterAt==="first"?ts[0]:ts[ts.length-1];cur=t.id;const el=document.getElementById("t-"+t.id);if(el&&enterAt==="last")el.scrollIntoView({block:"start"});
  const a=document.querySelector(`#list a[href="#${CSS.escape(t.id)}"]`);if(a)a.scrollIntoView({block:"nearest"})}
 enterAt=null;mark()}
let enterAt=null;
function route(){const h=decodeURIComponent(location.hash.slice(1));
 if(h.startsWith("ch=")){const ch=h.slice(3);if($("#ch").value!==ch){$("#ch").value=ch;renderList()}showChapter(ch);return}
 if(mode==="chapter"&&h&&document.getElementById("t-"+h)){cur=h;document.getElementById("t-"+h).scrollIntoView({block:"start"});mark();return}
 showOne(h||(T[0]&&T[0].id))}
$("#main").addEventListener("click",e=>{const b=e.target.closest("button[data-act]");if(!b)return;const t=T.find(x=>x.id===b.dataset.id);if(!t)return;
 if(b.dataset.act==="dl"){const bl=new Blob(["﻿"+csv(t)],{type:"text/csv"});const a=document.createElement("a");a.href=URL.createObjectURL(bl);a.download=t.id+".csv";a.click()}
 else navigator.clipboard.writeText((t.parts||[]).map(p=>[p.columns,...p.rows].map(r=>r.join("\t")).join("\n")).join("\n\n"))});
$("#list").addEventListener("click",e=>{const c=e.target.closest(".ch");if(!c)return;location.hash="ch="+encodeURIComponent(c.textContent)});
// Up/Down arrows: previous/next table in the sidebar list (ignored while typing in a field)
document.addEventListener("keydown",e=>{if(e.key!=="ArrowDown"&&e.key!=="ArrowUp")return;if(e.altKey||e.ctrlKey||e.metaKey)return;
 const tag=(document.activeElement&&document.activeElement.tagName)||"";if(/INPUT|SELECT|TEXTAREA/.test(tag))return;
 const links=[...document.querySelectorAll("#list a[href^='#']")];if(!links.length)return;
 document.body.classList.add("kbd");
 let i=links.findIndex(a=>a.classList.contains("on"));const down=e.key==="ArrowDown";
 const ch=$("#ch").value;
 // at either end of a chapter's list, step into the next/previous chapter
 if(ch&&i>-1&&((down&&i===links.length-1)||(!down&&i===0))){
  const opts=[...$("#ch").options].map(o=>o.value).filter(Boolean);const k=opts.indexOf(ch)+(down?1:-1);
  if(k>=0&&k<opts.length){e.preventDefault();enterAt=down?"first":"last";location.hash="ch="+encodeURIComponent(opts[k])}
  return}
 i=i<0?(down?0:links.length-1):Math.min(links.length-1,Math.max(0,i+(down?1:-1)));
 e.preventDefault();location.hash=links[i].getAttribute("href").slice(1);links[i].scrollIntoView({block:"nearest"})});
document.addEventListener("mousemove",()=>document.body.classList.remove("kbd"));
// Click-to-sort: asc -> desc -> original. Numeric-aware; blanks/dashes last; total rows pinned;
// sorting happens within blocks delimited by section-heading rows.
const pinRe=/^\s*(grand\s+)?(total|totals|sum|average|mean)\b/i;
function sortVal(s){s=(s||"").trim();if(s===""||/^[—–\-.…]+$/.test(s))return null;
 const neg=/^\(.*\)$/.test(s)||/^[-−–]\s*\d/.test(s);const n=s.replace(/[,\s¥$£%*†‡()]/g,"").replace(/^[-−–]/,"");
 if(/^\d+(\.\d+)?$/.test(n))return (neg?-1:1)*parseFloat(n);return s.toLowerCase()}
function cmp(a,b){if(a===null&&b===null)return 0;if(a===null)return 1;if(b===null)return -1;
 if(typeof a==="number"&&typeof b==="number")return a-b;return String(a).localeCompare(String(b),undefined,{numeric:true})}
function initSort(tbl){const ths=[...tbl.querySelectorAll("th.sortable")];
 ths.forEach(th=>th.addEventListener("click",()=>{const col=+th.dataset.col;const cur=th.getAttribute("aria-sort");
  const next=cur==="ascending"?"descending":cur==="descending"?null:"ascending";
  ths.forEach(x=>x.removeAttribute("aria-sort"));if(next)th.setAttribute("aria-sort",next);
  const tb=tbl.tBodies[0];const rows=[...tb.rows];const blocks=[[]];
  rows.sort((a,b)=>a.dataset.i-b.dataset.i).forEach(r=>{if(r.classList.contains("sec")){blocks.push([r]);blocks.push([])}else blocks[blocks.length-1].push(r)});
  const out=[];blocks.forEach(bl=>{if(bl.length&&bl[0].classList.contains("sec")){out.push(...bl);return}
   if(!next){out.push(...bl);return}
   const pinned=bl.filter(r=>pinRe.test(r.cells[0].textContent)),body=bl.filter(r=>!pinRe.test(r.cells[0].textContent));
   body.sort((a,b)=>{const va=sortVal(a.cells[col].textContent),vb=sortVal(b.cells[col].textContent);
    if(va===null||vb===null)return cmp(va,vb);const c=cmp(va,vb);return next==="ascending"?c:-c});
   out.push(...body,...pinned)});
  out.forEach(r=>tb.appendChild(r))}))}
function mark(){const id=cur||decodeURIComponent(location.hash.slice(1));document.querySelectorAll("#list a").forEach(a=>a.classList.toggle("on",a.getAttribute("href")==="#"+id))}
$("#ch").addEventListener("input",()=>{renderList();const ch=$("#ch").value;
 if(ch)location.hash="ch="+encodeURIComponent(ch);else{history.replaceState(null,"",location.pathname);showOne(T[0]&&T[0].id)}});
["q","flag"].forEach(k=>$("#"+k).addEventListener("input",()=>{renderList();if(mode==="chapter")showChapter($("#ch").value)}));
window.addEventListener("hashchange",route);
$("#toggle").onclick=()=>{const r=document.documentElement,d=r.dataset.theme==="dark"||(!r.dataset.theme&&matchMedia("(prefers-color-scheme: dark)").matches);r.dataset.theme=d?"light":"dark"};
renderList();route();
</script>
</body>
</html>
"""


def dir_key(f):
    m = re.search(r"(\d+)", os.path.basename(f))
    return int(m.group(1)) if m else 0


def build_directory(book):
    """Write <slug>/directory.html from <dir>/_work/directory/*.json; return the entry count."""
    files = sorted(glob.glob(os.path.join(book_dir(book), "_work", "directory", "*.json")), key=dir_key)
    entries = []
    for f in files:
        try:
            with open(f, encoding="utf-8") as fh:
                d = json.load(fh)
        except (FileNotFoundError, json.JSONDecodeError):
            print("skipped", f)
            continue
        leaf = d.get("leaf") or os.path.basename(f)[:-5]
        scan = scan_links(book, {"images": [leaf]})[0]
        for e in d.get("entries", []):
            sec = e.get("section") or ""
            if sec.isupper():
                sec = sec.title()
            entries.append({"a": d.get("appendix") or "", "s": sec, "n": (e.get("name") or "").rstrip(" ,."),
                            "t": e.get("text") or "", "p": e.get("page") or ", ".join(d.get("printed_pages") or []),
                            "l": scan["label"], "u": scan["url"]})
    if not entries:
        return 0
    os.makedirs(os.path.join(HERE, book["slug"]), exist_ok=True)
    with open(os.path.join(HERE, "data", book["slug"] + "-directory.json"), "w", encoding="utf-8") as fh:
        json.dump(entries, fh, ensure_ascii=False, indent=1)
    data = json.dumps(entries, ensure_ascii=False).replace("</", "<\\/")
    doc = (DIRTEMPLATE.replace("__DATA__", data).replace("__COUNT__", f"{len(entries):,}")
           .replace("__BOOK__", html.escape(book["title"])).replace("__SLUG__", book["slug"])
           .replace("__PROG__", " · <i>transcription in progress</i>" if book.get("dir_in_progress") else "")
           .replace("__MD__", f' · <a href="../{dl(book["slug"], "directory.md")}" download>Markdown</a>' if dl(book["slug"], "directory.md") else ""))
    with open(os.path.join(HERE, book["slug"], "directory.html"), "w", encoding="utf-8") as fh:
        fh.write(doc)
    print(f"{book['slug']}: {len(entries)} directory entries")
    return len(entries)


def build_chronology(book):
    """Write <slug>/chronology.html from <dir>/_work/chronology/*.json (events lists); return the event count."""
    files = sorted(glob.glob(os.path.join(book_dir(book), "_work", "chronology", "*.json")), key=dir_key)
    events = []
    for f in files:
        try:
            with open(f, encoding="utf-8") as fh:
                c = json.load(fh)
        except (FileNotFoundError, json.JSONDecodeError):
            continue
        scan = scan_links(book, {"images": [c.get("image") or os.path.basename(f)[:-5].split("_")[0]]})[0]
        head = " — ".join(x for x in (c.get("chapter"), c.get("title")) if x)
        for e in c.get("events", []):
            events.append({"a": head, "s": "", "n": e.get("date") or "", "t": e.get("text") or "",
                           "p": e.get("page") or ", ".join(c.get("printed_pages") or []), "l": scan["label"], "u": scan["url"]})
    if not events:
        return 0
    os.makedirs(os.path.join(HERE, book["slug"]), exist_ok=True)
    with open(os.path.join(HERE, "data", book["slug"] + "-chronology.json"), "w", encoding="utf-8") as fh:
        json.dump(events, fh, ensure_ascii=False, indent=1)
    data = json.dumps(events, ensure_ascii=False).replace("</", "<\\/")
    doc = (DIRTEMPLATE.replace("__DATA__", data).replace("__COUNT__", f"{len(events):,}")
           .replace("__BOOK__", html.escape(book["title"])).replace("__SLUG__", book["slug"])
           .replace("__PROG__", " · <i>transcription in progress</i>" if book.get("in_progress") else "")
           .replace("· Directories", "· Chronologies").replace("-directory.json", "-chronology.json")
           .replace(" entries", " events").replace("Filter names, places, firms, words…", "Filter dates, names, places, words…")
           .replace("> names only<", "> dates only<").replace("These entries were", "These events were")
           .replace("__MD__", f' · <a href="../{dl(book["slug"], "chronology.md")}" download>Markdown</a>' if dl(book["slug"], "chronology.md") else ""))
    with open(os.path.join(HERE, book["slug"], "chronology.html"), "w", encoding="utf-8") as fh:
        fh.write(doc)
    print(f"{book['slug']}: {len(events)} chronology events")
    return len(events)


DIRTEMPLATE = r"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>__BOOK__ · Directories</title>
<style>
:root{--bg:#f4f5f3;--panel:#ffffff;--ink:#1b2420;--muted:#5d6a62;--line:#d8ded9;--accent:#1f4a2c;--accent-ink:#ffffff;--hi:#e2ece4;--warn:#8a5a00}
@media (prefers-color-scheme: dark){:root:not([data-theme="light"]){--bg:#111814;--panel:#17211b;--ink:#e4ebe6;--muted:#9aa89f;--line:#2c3a31;--accent:#8cc49e;--accent-ink:#0f1a13;--hi:#1f3527;--warn:#e0a54a}}
:root[data-theme="dark"]{--bg:#111814;--panel:#17211b;--ink:#e4ebe6;--muted:#9aa89f;--line:#2c3a31;--accent:#8cc49e;--accent-ink:#0f1a13;--hi:#1f3527;--warn:#e0a54a}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);font:15px/1.5 Georgia,"Times New Roman",serif}
header{padding:14px 18px;background:var(--accent);color:var(--accent-ink);display:flex;gap:14px;align-items:baseline;flex-wrap:wrap}
header a,header .meta{color:var(--accent-ink)!important;opacity:.88}
header h1{font-size:20px;margin:0;font-weight:normal}
header .meta{font-size:13px}
header button{margin-left:auto;background:transparent;color:var(--accent-ink);border-color:currentColor}
.bar{position:sticky;top:0;z-index:2;background:var(--bg);border-bottom:1px solid var(--line)}
.bar>div{max-width:900px;margin:0 auto;padding:12px 16px;display:flex;gap:8px;flex-wrap:wrap;align-items:center}
input,select,button{font:inherit;font-size:14px;padding:7px 9px;border:1px solid var(--line);background:var(--panel);color:var(--ink);border-radius:4px}
button{cursor:pointer}
#q{flex:1 1 260px;font-size:16px}
#cnt{color:var(--muted);font-size:13px;width:100%}
main{max-width:900px;margin:0 auto;padding:10px 16px 60px}
.sec{font-size:13px;letter-spacing:.06em;text-transform:uppercase;color:var(--accent);margin:22px 0 6px;border-bottom:1px solid var(--line);padding-bottom:3px}
.e{background:var(--panel);border:1px solid var(--line);border-left:3px solid var(--accent);padding:9px 12px;margin:0 0 8px}
.e b{font-size:15.5px}
.e .t{font-size:14.5px}
.e .m{font-size:12.5px;color:var(--muted);margin-top:3px}
.e .m a{color:var(--accent)}
mark{background:#f3e3a0;color:inherit}
:root[data-theme="dark"] mark{background:#5a4d1c}
#more{display:block;margin:14px auto}#more[hidden]{display:none}
.llmwarn{margin:24px 0 8px;padding:12px 14px;border:1px solid var(--warn);border-left:4px solid var(--warn);background:var(--panel);font-size:14px}
</style></head><body>
<header><a href="./" style="text-decoration:none;font-size:14px">← Tables</a><a href="../" style="text-decoration:none;font-size:14px">All books</a><h1>__BOOK__ · Directories</h1>
<span class="meta">__COUNT__ entries__PROG__ · LLM-transcribed · <a href="../data/__SLUG__-directory.json">JSON</a>__MD__</span>
<button id="toggle" title="Toggle light/dark">◐</button></header>
<div class="bar"><div>
<input id="q" type="search" placeholder="Filter names, places, firms, words…" autofocus>
<select id="ap"><option value="">All sections</option></select>
<label style="font-size:13px"><input type="checkbox" id="nameonly"> names only</label>
<div id="cnt"></div></div></div>
<main><div id="out"></div><button id="more" hidden>Show more</button>
<div class="llmwarn" role="note"><b>Warning:</b> These entries were transcribed by the vision model of Opus 5.5. Before using any of them, you must verify specific details with the original source which is linked to whenever possible.</div></main>
<script>
const E=__DATA__;
const $=s=>document.querySelector(s);
const esc=s=>String(s).replace(/[&<>"]/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]));
const norm=s=>s.normalize("NFD").replace(/[̀-ͯ]/g,"").toLowerCase();
E.forEach(e=>{e._n=norm(e.n);e._all=norm(e.n+" "+e.t+" "+e.s)});
const groups=[...new Set(E.map(e=>e.a+(e.s?" — "+e.s:"")))];
const apps=[...new Set(E.map(e=>e.a))];
const sel=$("#ap");
apps.forEach(a=>{const o=document.createElement("option");o.value="A:"+a;o.textContent=a;sel.appendChild(o);
 groups.filter(g=>g.startsWith(a+" — ")).forEach(g=>{const o=document.createElement("option");o.value="G:"+g;o.textContent="   "+g.slice(a.length+3);sel.appendChild(o)})});
function hl(s,terms){s=esc(s);if(!terms.length)return s;
 // highlight accent-insensitively by matching on normalised text
 const src=s,n=norm(src);let marks=[];terms.forEach(t=>{let i=0;const et=norm(esc(t));while(et&&(i=n.indexOf(et,i))>-1){marks.push([i,i+et.length]);i+=et.length}});
 if(!marks.length)return s;marks.sort((a,b)=>a[0]-b[0]);let out="",pos=0;
 marks.forEach(([a,b])=>{if(a<pos)return;out+=src.slice(pos,a)+"<mark>"+src.slice(a,b)+"</mark>";pos=b});return out+src.slice(pos)}
let res=[],shown=0;const STEP=300;
function run(){const q=norm($("#q").value.trim());const terms=q.split(/\s+/).filter(Boolean);const v=sel.value;const no=$("#nameonly").checked;
 res=E.filter(e=>{if(v.startsWith("A:")&&e.a!==v.slice(2))return false;if(v.startsWith("G:")&&e.a+(e.s?" — "+e.s:"")!==v.slice(2))return false;
  const hay=no?e._n:e._all;return terms.every(t=>hay.includes(t))});
 $("#cnt").textContent=`${res.length.toLocaleString()} of ${E.length.toLocaleString()} entries`;
 $("#out").innerHTML="";shown=0;more(terms);
 try{history.replaceState(null,"",(q||v)?"#"+new URLSearchParams({q:$("#q").value.trim(),s:v}).toString():location.pathname)}catch(e){}}
function more(terms){terms=terms||norm($("#q").value.trim()).split(/\s+/).filter(Boolean);
 let h="",last=shown?groupOf(res[shown-1]):null;
 res.slice(shown,shown+STEP).forEach(e=>{const g=groupOf(e);if(g!==last){h+=`<div class="sec">${esc(g)}</div>`;last=g}
  h+=`<div class="e"><b>${hl(e.n,terms)}</b> <span class="t">${hl(e.t,terms)}</span><div class="m">p. ${esc(e.p)}${e.u?` · <a href="${e.u}" target="_blank" rel="noopener">${esc(e.l)}</a>`:e.l?" · "+esc(e.l):""}</div></div>`});
 $("#out").insertAdjacentHTML("beforeend",h);shown=Math.min(res.length,shown+STEP);$("#more").hidden=shown>=res.length}
const groupOf=e=>e.a+(e.s?" — "+e.s:"");
let tm;$("#q").addEventListener("input",()=>{clearTimeout(tm);tm=setTimeout(run,120)});
sel.addEventListener("change",run);$("#nameonly").addEventListener("change",run);$("#more").addEventListener("click",()=>more());
$("#toggle").addEventListener("click",()=>{const r=document.documentElement;const d=r.dataset.theme?r.dataset.theme==="dark":matchMedia("(prefers-color-scheme: dark)").matches;r.dataset.theme=d?"light":"dark"});
try{const p=new URLSearchParams(location.hash.slice(1));if(p.get("q"))$("#q").value=p.get("q");if(p.get("s"))sel.value=p.get("s")}catch(e){}
run();
</script></body></html>
"""


SEARCH = r"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Search All Books</title>
<style>
:root{--bg:#f4f5f3;--panel:#ffffff;--ink:#1b2420;--muted:#5d6a62;--line:#d8ded9;--accent:#1f4a2c;--accent-ink:#ffffff;--hi:#e2ece4;--warn:#8a5a00;--mark:#f3e3a0}
@media (prefers-color-scheme: dark){:root:not([data-theme="light"]){--bg:#111814;--panel:#17211b;--ink:#e4ebe6;--muted:#9aa89f;--line:#2c3a31;--accent:#8cc49e;--accent-ink:#0f1a13;--hi:#1f3527;--warn:#e0a54a;--mark:#5a4d1c}}
:root[data-theme="dark"]{--bg:#111814;--panel:#17211b;--ink:#e4ebe6;--muted:#9aa89f;--line:#2c3a31;--accent:#8cc49e;--accent-ink:#0f1a13;--hi:#1f3527;--warn:#e0a54a;--mark:#5a4d1c}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font:15px/1.5 Georgia,"Times New Roman",serif}
header{padding:14px 18px;background:var(--accent);color:var(--accent-ink);display:flex;gap:14px;align-items:baseline;flex-wrap:wrap}
header a{color:var(--accent-ink);opacity:.88;font-size:14px;text-decoration:none}header h1{font-size:20px;margin:0;font-weight:normal}
header button{margin-left:auto;background:transparent;color:var(--accent-ink);border:1px solid currentColor;border-radius:4px;font:inherit;padding:4px 8px;cursor:pointer}
main{max-width:1000px;margin:0 auto;padding:18px 16px 60px}
.boxes{display:grid;grid-template-columns:1fr 1fr;gap:16px}
.box{background:var(--panel);border:1px solid var(--line);border-top:3px solid var(--accent);padding:14px}
.box h2{font-size:17px;font-weight:normal;margin:0 0 8px}.box p{font-size:13px;color:var(--muted);margin:6px 0 0}
input{font:inherit;font-size:16px;padding:8px 10px;border:1px solid var(--line);background:var(--bg);color:var(--ink);border-radius:4px;width:100%}
.tabs{display:flex;gap:6px;margin:22px 0 8px;border-bottom:1px solid var(--line)}
.tabs button{font:inherit;font-size:14px;padding:7px 12px;border:1px solid var(--line);border-bottom:0;background:var(--bg);color:var(--ink);border-radius:5px 5px 0 0;cursor:pointer}
.tabs button.on{background:var(--accent);color:var(--accent-ink);border-color:var(--accent)}
#status{color:var(--muted);font-size:13px;margin:6px 0 10px}
.bk{font-size:13px;letter-spacing:.06em;text-transform:uppercase;color:var(--accent);margin:18px 0 6px;border-bottom:1px solid var(--line);padding-bottom:3px}
.r{background:var(--panel);border:1px solid var(--line);border-left:3px solid var(--accent);padding:8px 12px;margin:0 0 7px}
.r a.t{font-size:15.5px;color:var(--ink);text-decoration:none;font-weight:bold}.r a.t:hover{text-decoration:underline}
.r .m{font-size:12.5px;color:var(--muted)}.r .m a{color:var(--accent)}
.r .snip{font-size:13px;margin-top:4px;font-family:"Iowan Old Style",Georgia,serif}
.r .snip div{white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
mark{background:var(--mark);color:inherit}
.llmwarn{margin:24px 0 8px;padding:12px 14px;border:1px solid var(--warn);border-left:4px solid var(--warn);background:var(--panel);font-size:14px}
@media (max-width:700px){.boxes{grid-template-columns:1fr}}
</style></head><body>
<header><a href="./">← All books</a><h1>Search all books</h1><button id="toggle" title="Toggle light/dark">◐</button></header>
<main>
<div class="boxes">
<div class="box"><h2>Tables</h2><input id="qt" type="search" placeholder="e.g. rice, Dairen, cotton exports…"><p>Titles, chapters, column headings, cells and notes of every table in every book.</p></div>
<div class="box"><h2>Who's Who &amp; Directories</h2><input id="qd" type="search" placeholder="e.g. Mitsui, Kato, Keio, Osaka…"><p>People, firms, societies and institutions across all the directory appendices.</p></div>
</div>
<div class="tabs"><button id="tt" class="on">Table results</button><button id="td">Directory results</button></div>
<div id="status"></div><div id="out"></div>
<div class="llmwarn" role="note"><b>Warning:</b> These tables were transcribed by the vision model of Opus 5.5. Before using any of these figures, you must verify specific statistics with the original source which is linked to whenever possible.</div>
</main>
<script>
const BOOKS=__BOOKS__;
const $=s=>document.querySelector(s);
const esc=s=>String(s??"").replace(/[&<>"]/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]));
const norm=s=>String(s??"").normalize("NFD").replace(/[̀-ͯ]/g,"").toLowerCase();
function hl(s,terms){s=String(s??"");const n=norm(s);let marks=[];terms.forEach(t=>{let i=0;while(t&&(i=n.indexOf(t,i))>-1){marks.push([i,i+t.length]);i+=t.length}});
 if(!marks.length)return esc(s);marks.sort((a,b)=>a[0]-b[0]);let out="",pos=0;marks.forEach(([a,b])=>{if(a<pos)return;out+=esc(s.slice(pos,a))+"<mark>"+esc(s.slice(a,b))+"</mark>";pos=b});return out+esc(s.slice(pos))}
let TB=null,DR=null,tab="t";
async function loadTables(){if(TB)return TB;$("#status").textContent="Loading tables…";
 TB=(await Promise.all(BOOKS.map(b=>fetch("data/"+b.slug+".json").then(r=>r.json()).then(ts=>ts.map(t=>{
  const rows=(t.parts||[]).flatMap(p=>p.rows||[]);
  return {b,t,rows,head:norm([t.title,t.table_no,t.chapter,t.caption_extra].join(" ")),all:norm([t.title,t.table_no,t.chapter,t.caption_extra,...(t.parts||[]).flatMap(p=>[p.label,...(p.columns||[])]),...rows.map(r=>r.join(" ")),...(t.footnotes||[])].join(" \n "))}}))))).flat();return TB}
async function loadDirs(){if(DR)return DR;$("#status").textContent="Loading directories…";
 DR=(await Promise.all(BOOKS.filter(b=>b.dir).map(b=>fetch("data/"+b.slug+"-directory.json").then(r=>r.json()).then(es=>es.map(e=>({b,e,n:norm(e.n),all:norm(e.n+" "+e.t+" "+e.s)})))))).flat();return DR}
const LIMIT=400;
async function runT(){const q=$("#qt").value.trim();const terms=norm(q).split(/\s+/).filter(Boolean);
 if(!terms.length){$("#status").textContent="Type in the Tables box to search.";$("#out").innerHTML="";return}
 const all=await loadTables();if(norm($("#qt").value.trim())!==norm(q))return;
 const res=all.filter(x=>terms.every(w=>x.all.includes(w)));res.sort((a,b)=>terms.filter(w=>b.head.includes(w)).length-terms.filter(w=>a.head.includes(w)).length);
 const by={};res.slice(0,LIMIT).forEach(x=>(by[x.b.slug]=by[x.b.slug]||[]).push(x));
 $("#status").textContent=`${res.length.toLocaleString()} table${res.length===1?"":"s"}${res.length>LIMIT?` (showing ${LIMIT})`:""}`;
 let h="";BOOKS.forEach(b=>{const xs=by[b.slug];if(!xs)return;h+=`<div class="bk">${esc(b.title)} · ${xs.length}</div>`;
  xs.forEach(x=>{const t=x.t;const lab=(t.table_no?`Table ${t.table_no}. `:"")+(t.title||"");
   const hits=x.rows.filter(r=>terms.some(w=>norm(r.join(" ")).includes(w))).slice(0,3);
   h+=`<div class="r"><a class="t" href="${b.slug}/#${encodeURIComponent(t.id)}">${hl(lab,terms)}</a><div class="m">${esc(t.chapter||"")} · p. ${esc((t.printed_pages||[]).join(", "))}${(t.scans||[])[0]&&t.scans[0].url?` · <a href="${t.scans[0].url}" target="_blank" rel="noopener">scan</a>`:""}</div>`+
    (hits.length?`<div class="snip">${hits.map(r=>`<div>${r.map(c=>hl(c,terms)).join(" · ")}</div>`).join("")}</div>`:"")+`</div>`})});
 $("#out").innerHTML=h||"<p>No tables match.</p>"}
async function runD(){const q=$("#qd").value.trim();const terms=norm(q).split(/\s+/).filter(Boolean);
 if(!terms.length){$("#status").textContent="Type in the Directories box to search.";$("#out").innerHTML="";return}
 const all=await loadDirs();if(norm($("#qd").value.trim())!==norm(q))return;
 const res=all.filter(x=>terms.every(w=>x.all.includes(w)));res.sort((a,b)=>terms.filter(w=>b.n.includes(w)).length-terms.filter(w=>a.n.includes(w)).length);
 const by={};res.slice(0,LIMIT).forEach(x=>(by[x.b.slug]=by[x.b.slug]||[]).push(x));
 $("#status").textContent=`${res.length.toLocaleString()} entr${res.length===1?"y":"ies"}${res.length>LIMIT?` (showing ${LIMIT})`:""}`;
 let h="";BOOKS.forEach(b=>{const xs=by[b.slug];if(!xs)return;h+=`<div class="bk">${esc(b.title)} · ${xs.length} · <a href="${b.slug}/directory.html#${new URLSearchParams({q}).toString()}" style="color:inherit">open in book directory</a></div>`;
  xs.forEach(({e})=>{h+=`<div class="r"><b>${hl(e.n,terms)}</b> <span class="snip">${hl(e.t,terms)}</span><div class="m">${esc(e.a)}${e.s?" — "+esc(e.s):""} · p. ${esc(e.p)}${e.u?` · <a href="${e.u}" target="_blank" rel="noopener">${esc(e.l)}</a>`:e.l?" · "+esc(e.l):""}</div></div>`})});
 $("#out").innerHTML=h||"<p>No entries match.</p>"}
function setTab(x){tab=x;$("#tt").classList.toggle("on",x==="t");$("#td").classList.toggle("on",x==="d");(x==="t"?runT:runD)();
 try{history.replaceState(null,"","#"+new URLSearchParams({t:$("#qt").value,d:$("#qd").value,tab:x}).toString())}catch(e){}}
let tm;const deb=x=>()=>{clearTimeout(tm);tm=setTimeout(()=>setTab(x),200)};
$("#qt").addEventListener("input",deb("t"));$("#qd").addEventListener("input",deb("d"));
$("#qt").addEventListener("focus",()=>tab!=="t"&&setTab("t"));$("#qd").addEventListener("focus",()=>tab!=="d"&&setTab("d"));
$("#tt").addEventListener("click",()=>setTab("t"));$("#td").addEventListener("click",()=>setTab("d"));
$("#toggle").addEventListener("click",()=>{const r=document.documentElement;const d=r.dataset.theme?r.dataset.theme==="dark":matchMedia("(prefers-color-scheme: dark)").matches;r.dataset.theme=d?"light":"dark"});
try{const p=new URLSearchParams(location.hash.slice(1));$("#qt").value=p.get("t")||"";$("#qd").value=p.get("d")||"";setTab(p.get("tab")==="d"?"d":"t")}catch(e){setTab("t")}
</script></body></html>
"""

if __name__ == "__main__":
    main()
