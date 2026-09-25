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
    {"slug": "manchoukuo-1942", "dir": ".", "title": "The Manchoukuo Year Book 1942",
     "publisher": "Manchoukuo Year Book Co., Hsinking, 1942",
     "blurb": "Official English-language yearbook of Manchukuo: geography, population, finance, banking, trade, agriculture, mining, industry, transport, labour, education and more.",
     "source": "LLM-transcribed from 498 photographs of the printed volume (two-page spreads).",
     "gaps": "Pages 502–503 (Mining) and 966–967 (Index) were not photographed. Gaps in table numbering (e.g. Agriculture Tables 2–3 and 11–17) are in the printed book itself.",
     "scan": None},
    {"slug": "korea-1929-30", "dir": "Korea_Annual_Report_1929-30",
     "title": "Annual Report on Administration of Chosen 1929-30",
     "publisher": "Government-General of Chosen, Keijo, 1931",
     "blurb": "The Government-General's English-language annual report on colonial Korea: population, finance, banking, trade, education, industry, communications, police, public health and local administration.",
     "source": "LLM-transcribed from the Internet Archive scan.",
     "gaps": "The Internet Archive scan is missing the text page beside each photo plate (printed pp. 66, 74, 82, 92, 96, 100, 104, 140, 152 and 172), as well as the appendix tables of weights and measures and of governors. On p. 13 the Total column is in a different typeface from the rest of the table, which may mean the scan was retouched.",
     "scan": "https://archive.org/details/annualreportonreformsandprogressinchosenkorea192930/page/n{leaf}/mode/1up",
     "item": "https://archive.org/details/annualreportonreformsandprogressinchosenkorea192930"},
    {"slug": "japan-1930", "dir": "Japan_Year_Book_1930", "title": "The Japan Year Book 1930",
     "publisher": "The Japan Year Book Office, Tokyo, 1930",
     "blurb": "Comprehensive English-language reference on the Japanese Empire in 1930, covering geography, population, government, defence, education, labour, justice, communications, railways, shipping, banking, finance, agriculture, industry, trade, the six premier cities and the colonies.",
     "source": "LLM-transcribed from the Internet Archive scan.",
     "gaps": "Advertisements, the Who's Who, the Business Directory and the Index were screened but contain no tables. The shop and restaurant lists in Appendix D are included; the physicians' lists are not. On p. 439 the right edge of the scan cuts off the 1927 export figures, so those cells are blank.",
     "scan": "https://archive.org/details/japan-year-book-1930/page/n{leaf}/mode/1up",
     "item": "https://archive.org/details/japan-year-book-1930"},
    {"slug": "japan-1939-40", "dir": "Japan_Year_Book_1939-40", "title": "The Japan Year Book 1939-40",
     "publisher": "The Foreign Affairs Association of Japan, Tokyo, 1939",
     "blurb": "The wartime edition of the standard English-language reference on the Japanese Empire.",
     "source": "LLM-transcribed from the Internet Archive scan.",
     "in_progress": True,
     "scan": "https://archive.org/details/japan-year-book-1939-1940/page/n{leaf}/mode/1up",
     "item": "https://archive.org/details/japan-year-book-1939-1940"},
]


def page_key(t):
    m = re.search(r"(\d+)", t["file"])
    img = int(m.group(1)) if m else 0
    n = int(re.search(r"_(\d+)\.json$", t["file"]).group(1))
    return (img, n)


def load(book):
    tables = []
    for f in sorted(glob.glob(os.path.join(ROOT, book["dir"], "_work", "tables", "*.json"))):
        with open(f, encoding="utf-8") as fh:
            t = json.load(fh)
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
            out.append({"label": f"photo {im}", "url": None})
    return out


def cells(tables):
    return sum(len(r) for t in tables for p in t.get("parts", []) for r in p.get("rows", []))


def main():
    os.makedirs(os.path.join(HERE, "data"), exist_ok=True)
    cards = []
    for b in BOOKS:
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
                   .replace("__CELLS__", f"{c:,}").replace("__BOOK__", html.escape(b["title"]))
                   .replace("__SLUG__", b["slug"]).replace("__SOURCE__", html.escape(b["source"])))
            with open(os.path.join(HERE, b["slug"], "index.html"), "w", encoding="utf-8") as fh:
                fh.write(doc)
        cards.append((b, n, c, chapters))
        print(f"{b['slug']}: {n} tables, {c:,} cells")
    with open(os.path.join(HERE, "index.html"), "w", encoding="utf-8") as fh:
        fh.write(landing(cards))


def landing(cards):
    items = []
    for b, n, c, ch in cards:
        stat = (f"<b>{n}</b> tables · <b>{c:,}</b> cells · {ch} chapters" if n else "<i>transcription in progress</i>")
        if n and b.get("in_progress"):
            stat += " · <i>transcription in progress: early chapters only so far</i>"
        link = f'<a class="go" href="{b["slug"]}/">Browse tables →</a>' if n else ""
        item = f' · <a href="{b["item"]}">original scan</a>' if b.get("item") else ""
        gaps = f'<div class="src">{html.escape(b["gaps"])}</div>' if b.get("gaps") and n else ""
        items.append(f"""<article><h2>{html.escape(b["title"])}</h2><div class="pub">{html.escape(b["publisher"])}</div>
<p>{html.escape(b["blurb"])}</p><div class="stat">{stat}</div><div class="src">{html.escape(b["source"])}{item}</div>{gaps}{link}</article>""")
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
.lede{color:var(--muted);max-width:720px}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:18px;margin-top:28px}
article{background:var(--panel);border:1px solid var(--line);border-top:3px solid var(--accent);padding:18px 18px 16px;display:flex;flex-direction:column}
h2{font-size:20px;font-weight:normal;margin:0 0 4px}.pub{color:var(--muted);font-size:13px;margin-bottom:8px}
article p{font-size:14.5px;margin:0 0 12px;flex:1}.stat{font-size:14px;margin-bottom:6px}.src{font-size:12.5px;color:var(--muted);margin-bottom:12px}
a{color:var(--accent)}.go{font-size:15px;text-decoration:none;font-weight:bold}
.llmwarn{margin:28px 0 0;padding:12px 14px;border:1px solid #8a5a00;border-left:4px solid #8a5a00;background:var(--panel);font-size:14px}
footer{margin-top:24px;font-size:13px;color:var(--muted);border-top:1px solid var(--line);padding-top:14px}
</style></head><body><div class="band"><div>
<h1>East Asian Statistical Tables, 1929–1942</h1>
<p class="lede">Every statistical table in English-language official yearbooks on Japan and its empire, LLM-transcribed cell by cell from page images. The figures are kept exactly as printed, including the printers' errors. Where a printed total does not add up, a transcriber's note says so, and figures that could not be read are left blank.</p>
</div></div>
<main>
<div class="grid">
__CARDS__
</div>
<div class="llmwarn" role="note"><b>Warning:</b> These tables were transcribed by the vision model of Opus 5.5. Before using any of these figures, you must verify specific statistics with the original source which is linked to whenever possible.</div>
<footer>Each table can be downloaded as CSV, and the full data for each book is in <code>data/*.json</code>.</footer>
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
#list a.on{background:var(--hi);border-left:3px solid var(--accent)}
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
@media (max-width:760px){#wrap{grid-template-columns:1fr;height:auto}#side{border-right:0;border-bottom:1px solid var(--line)}#list{max-height:40vh}#main{padding:14px 16px}}
</style>
</head>
<body>
<header><a href="../" style="text-decoration:none;font-size:14px">← All books</a><h1>__BOOK__</h1>
<span class="meta">__COUNT__ tables · __CELLS__ cells · __SOURCE__ · <a href="../data/__SLUG__.json" style="color:inherit">JSON</a></span>
<button id="toggle" title="Toggle light/dark">◐</button></header>
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
  h+=`<a href="#${t.id}" data-i="${i}">${esc(label(t))}<small>p. ${esc((t.printed_pages||[]).join(", "))} · ${esc(t.image)}${t._warn?" · ⚠":""}</small></a>`;n++});
 $("#list").innerHTML=h||"<p style='padding:10px'>No matches.</p>";mark()}
function hl(s,q){s=esc(s);if(!q)return s;q.split(/\s+/).filter(Boolean).forEach(w=>{s=s.replace(new RegExp("("+w.replace(/[.*+?^${}()|[\]\\]/g,"\\$&")+")","ig"),"<mark>$1</mark>")});return s}
function csv(t){const L=[];(t.parts||[]).forEach(p=>{if(p.label)L.push([p.label]);L.push(p.columns);p.rows.forEach(r=>L.push(r));L.push([])});
 return L.map(r=>r.map(c=>/[",\n]/.test(c??"")?'"'+String(c).replace(/"/g,'""')+'"':(c??"")).join(",")).join("\n")}
function tableHTML(t,q){let h=`<section class="tbl" id="t-${t.id}"><h2><a href="#${t.id}">${hl(label(t),q)}</a></h2><div class="sub">${esc(t.chapter||"")} · printed page${(t.printed_pages||[]).length>1?"s":""} ${esc((t.printed_pages||[]).join(", "))} · ${/^p\d/.test(t.image||"")?"scan leaf":"photo"} ${esc((t.images||[t.image]).join(", "))}</div>`;
 if(t.caption_extra)h+=`<div class="sub"><i>${hl(t.caption_extra,q)}</i></div>`;
 (t.parts||[]).forEach(p=>{if(p.label)h+=`<div class="part">${hl(p.label,q)}</div>`;
  h+=`<div class="tw"><table><thead><tr>${p.columns.map((c,j)=>`<th class="sortable" data-col="${j}" title="Click to sort">${hl(c,q)}</th>`).join("")}</tr></thead><tbody>`;
  p.rows.forEach((r,ri)=>{const sec=r.length>1&&r.slice(1).every(c=>c==="");h+=`<tr data-i="${ri}"${sec?' class="sec"':""}>`+r.map((c,j)=>`<td class="${j&&isNum(c)?"num":""}${j&&c===""&&!sec?" blank":""}">${hl(c,q)}</td>`).join("")+"</tr>"});
  h+="</tbody></table></div>"});
 if((t.footnotes||[]).length)h+=`<div class="notes"><b>Printed notes</b><ul>${t.footnotes.map(n=>`<li>${hl(n,q)}</li>`).join("")}</ul></div>`;
 if((t.transcriber_notes||[]).length)h+=`<div class="notes"><b>Transcriber's notes</b><ul>${t.transcriber_notes.map(n=>`<li class="${warnRe.test(n)?"warn":""}">${esc(n)}</li>`).join("")}</ul></div>`;
 h+=`<div class="row"><button data-act="dl" data-id="${t.id}">Download CSV</button><button data-act="cp" data-id="${t.id}">Copy as TSV</button></div>`;
 h+=`<div class="sub">Source: ${(t.scans||[]).map(s=>s.url?`<a href="${s.url}" target="_blank" rel="noopener">${esc(s.label)}</a>`:esc(s.label)).join(", ")}</div></section>`;
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
 $("#main").innerHTML=h;$("#main").scrollTop=0;document.querySelectorAll("#main table").forEach(initSort);mark()}
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
 let i=links.findIndex(a=>a.classList.contains("on"));
 i=i<0?(e.key==="ArrowDown"?0:links.length-1):Math.min(links.length-1,Math.max(0,i+(e.key==="ArrowDown"?1:-1)));
 e.preventDefault();location.hash=links[i].getAttribute("href").slice(1);links[i].scrollIntoView({block:"nearest"})});
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

if __name__ == "__main__":
    main()
