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
     "source": "Hand-transcribed from 498 photographs of the printed volume (two-page spreads).",
     "gaps": "Pages 502–503 (Mining) and 966–967 (Index) were not photographed. Gaps in table numbering (e.g. Agriculture Tables 2–3 and 11–17) are in the printed book itself.",
     "scan": None},
    {"slug": "korea-1929-30", "dir": "Korea_Annual_Report_1929-30",
     "title": "Annual Report on Administration of Chosen 1929-30",
     "publisher": "Government-General of Chosen, Keijo, 1931",
     "blurb": "The Government-General's English-language annual report on colonial Korea: population, finance, banking, trade, education, industry, communications, police, public health and local administration.",
     "source": "Hand-transcribed from the Internet Archive scan.",
     "gaps": "The Internet Archive scan is missing the text page beside each photo plate (printed pp. 66, 74, 82, 92, 96, 100, 104, 140, 152 and 172), as well as the appendix tables of weights and measures and of governors. On p. 13 the Total column is in a different typeface from the rest of the table, which may mean the scan was retouched.",
     "scan": "https://archive.org/details/annualreportonreformsandprogressinchosenkorea192930/page/n{leaf}/mode/1up",
     "item": "https://archive.org/details/annualreportonreformsandprogressinchosenkorea192930"},
    {"slug": "japan-1930", "dir": "Japan_Year_Book_1930", "title": "The Japan Year Book 1930",
     "publisher": "The Japan Year Book Office, Tokyo, 1930",
     "blurb": "Comprehensive English-language reference on the Japanese Empire in 1930, covering geography, population, government, defence, education, labour, justice, communications, railways, shipping, banking, finance, agriculture, industry, trade, the six premier cities and the colonies.",
     "source": "Hand-transcribed from the Internet Archive scan.",
     "gaps": "Advertisements, the Who's Who, the Business Directory and the Index were screened but contain no tables (the restaurant lists in Appendix D are the one exception). On p. 439 the right edge of the scan cuts off the 1927 export figures, so those cells are blank.",
     "scan": "https://archive.org/details/japan-year-book-1930/page/n{leaf}/mode/1up",
     "item": "https://archive.org/details/japan-year-book-1930"},
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
:root{--bg:#f7f5f0;--panel:#fffdf8;--ink:#1f1d1a;--muted:#6b665d;--line:#ddd6c8;--accent:#8a2b1d}
@media (prefers-color-scheme: dark){:root:not([data-theme="light"]){--bg:#1a1917;--panel:#23211e;--ink:#ece7dc;--muted:#a39d91;--line:#3a3631;--accent:#e08b6f}}
:root[data-theme="dark"]{--bg:#1a1917;--panel:#23211e;--ink:#ece7dc;--muted:#a39d91;--line:#3a3631;--accent:#e08b6f}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font:16px/1.55 Georgia,"Times New Roman",serif}
main{max-width:980px;margin:0 auto;padding:40px 16px 60px}h1{font-weight:normal;font-size:30px;margin:0 0 6px}
.lede{color:var(--muted);max-width:720px}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:18px;margin-top:28px}
article{background:var(--panel);border:1px solid var(--line);border-top:3px solid var(--accent);padding:18px 18px 16px;display:flex;flex-direction:column}
h2{font-size:20px;font-weight:normal;margin:0 0 4px}.pub{color:var(--muted);font-size:13px;margin-bottom:8px}
article p{font-size:14.5px;margin:0 0 12px;flex:1}.stat{font-size:14px;margin-bottom:6px}.src{font-size:12.5px;color:var(--muted);margin-bottom:12px}
a{color:var(--accent)}.go{font-size:15px;text-decoration:none;font-weight:bold}
footer{margin-top:36px;font-size:13px;color:var(--muted);border-top:1px solid var(--line);padding-top:14px}
</style></head><body><main>
<h1>East Asian Statistical Tables, 1929–1942</h1>
<p class="lede">Every statistical table in three English-language official yearbooks on Japan and its empire, transcribed cell by cell from the printed page. The figures are kept exactly as printed, including the printers' errors. Where a printed total does not add up, a transcriber's note says so, and figures that could not be read are left blank.</p>
<div class="grid">
__CARDS__
</div>
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
:root{--bg:#f7f5f0;--panel:#fffdf8;--ink:#1f1d1a;--muted:#6b665d;--line:#ddd6c8;--accent:#8a2b1d;--hi:#f3e7c9;--warn:#9a5b00}
@media (prefers-color-scheme: dark){:root:not([data-theme="light"]){--bg:#1a1917;--panel:#23211e;--ink:#ece7dc;--muted:#a39d91;--line:#3a3631;--accent:#e08b6f;--hi:#3b3322;--warn:#e0a54a}}
:root[data-theme="dark"]{--bg:#1a1917;--panel:#23211e;--ink:#ece7dc;--muted:#a39d91;--line:#3a3631;--accent:#e08b6f;--hi:#3b3322;--warn:#e0a54a}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);font:15px/1.45 Georgia,"Times New Roman",serif}
header{padding:14px 18px;border-bottom:1px solid var(--line);display:flex;gap:14px;align-items:baseline;flex-wrap:wrap}
header h1{font-size:20px;margin:0;font-weight:normal}
header .meta{color:var(--muted);font-size:13px}
#wrap{display:grid;grid-template-columns:340px 1fr;height:calc(100vh - 56px)}
#side{border-right:1px solid var(--line);display:flex;flex-direction:column;min-height:0}
#side .ctl{padding:10px;border-bottom:1px solid var(--line);display:flex;flex-direction:column;gap:6px}
input,select,button{font:inherit;font-size:14px;padding:6px 8px;border:1px solid var(--line);background:var(--panel);color:var(--ink);border-radius:4px}
button{cursor:pointer}
#list{overflow:auto;flex:1}
#list .ch{position:sticky;top:0;background:var(--bg);padding:8px 10px 4px;font-size:12px;letter-spacing:.06em;text-transform:uppercase;color:var(--accent);border-bottom:1px solid var(--line)}
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
td.num{text-align:right;font-variant-numeric:tabular-nums;white-space:nowrap}
td.blank{background:repeating-linear-gradient(45deg,transparent 0 4px,var(--hi) 4px 8px)}
tr:hover td{background:var(--hi)}
tr.sec td:first-child{font-weight:bold;font-style:italic}
.part{font-weight:bold;margin-top:12px}
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
<header><a href="../" style="color:var(--muted);text-decoration:none;font-size:14px">← All books</a><h1>__BOOK__</h1>
<span class="meta">__COUNT__ tables · __CELLS__ cells · __SOURCE__ · <a href="../data/__SLUG__.json" style="color:inherit">JSON</a></span>
<button id="toggle" title="Toggle light/dark">◐</button></header>
<div id="wrap">
<nav id="side"><div class="ctl">
<input id="q" type="search" placeholder="Search titles, headings, cells…">
<select id="ch"><option value="">All chapters</option></select>
<label style="font-size:13px;color:var(--muted)"><input type="checkbox" id="flag"> only tables with transcriber warnings</label>
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
function show(id){const t=T.find(x=>x.id===id)||T[0];if(!t){$("#main").innerHTML="<p>No tables yet.</p>";return}
 const q=$("#q").value.trim();let h=`<h2>${hl(label(t),q)}</h2><div class="sub">${esc(t.chapter||"")} · printed page${(t.printed_pages||[]).length>1?"s":""} ${esc((t.printed_pages||[]).join(", "))} · ${/^p\d/.test(t.image||"")?"scan leaf":"photo"} ${esc((t.images||[t.image]).join(", "))}</div>`;
 if(t.caption_extra)h+=`<div class="sub"><i>${hl(t.caption_extra,q)}</i></div>`;
 (t.parts||[]).forEach(p=>{if(p.label)h+=`<div class="part">${hl(p.label,q)}</div>`;
  h+=`<div class="tw"><table><thead><tr>${p.columns.map(c=>`<th>${hl(c,q)}</th>`).join("")}</tr></thead><tbody>`;
  p.rows.forEach(r=>{const sec=r.length>1&&r.slice(1).every(c=>c==="");h+=`<tr${sec?' class="sec"':""}>`+r.map((c,j)=>`<td class="${j&&isNum(c)?"num":""}${j&&c===""&&!sec?" blank":""}">${hl(c,q)}</td>`).join("")+"</tr>"});
  h+="</tbody></table></div>"});
 if((t.footnotes||[]).length)h+=`<div class="notes"><b>Printed notes</b><ul>${t.footnotes.map(n=>`<li>${hl(n,q)}</li>`).join("")}</ul></div>`;
 if((t.transcriber_notes||[]).length)h+=`<div class="notes"><b>Transcriber's notes</b><ul>${t.transcriber_notes.map(n=>`<li class="${warnRe.test(n)?"warn":""}">${esc(n)}</li>`).join("")}</ul></div>`;
 h+=`<div class="row"><button id="dl">Download CSV</button><button id="cp">Copy as TSV</button></div>`;
 h+=`<div class="sub">Source: ${(t.scans||[]).map(s=>s.url?`<a href="${s.url}" target="_blank" rel="noopener">${esc(s.label)}</a>`:esc(s.label)).join(", ")}</div>`;
 $("#main").innerHTML=h;$("#main").scrollTop=0;
 $("#dl").onclick=()=>{const b=new Blob(["\ufeff"+csv(t)],{type:"text/csv"});const a=document.createElement("a");a.href=URL.createObjectURL(b);a.download=t.id+".csv";a.click()};
 $("#cp").onclick=()=>{navigator.clipboard.writeText((t.parts||[]).map(p=>[p.columns,...p.rows].map(r=>r.join("\t")).join("\n")).join("\n\n"))};
 mark()}
function mark(){const id=location.hash.slice(1);document.querySelectorAll("#list a").forEach(a=>a.classList.toggle("on",a.getAttribute("href")==="#"+id))}
["q","ch","flag"].forEach(k=>$("#"+k).addEventListener("input",()=>{renderList();if(location.hash)show(location.hash.slice(1))}));
window.addEventListener("hashchange",()=>show(location.hash.slice(1)));
$("#toggle").onclick=()=>{const r=document.documentElement,d=r.dataset.theme==="dark"||(!r.dataset.theme&&matchMedia("(prefers-color-scheme: dark)").matches);r.dataset.theme=d?"light":"dark"};
renderList();show(location.hash.slice(1)||(T[0]&&T[0].id));
</script>
</body>
</html>
"""

if __name__ == "__main__":
    main()
