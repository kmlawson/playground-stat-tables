"""Directory-page template (shared with the main build_site.py directory feature)."""
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
<span class="meta">__COUNT__ entries__PROG__ · LLM-transcribed · <a href="../data/__SLUG__-directory.json">JSON</a></span>
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
  h+=`<div class="e"><b>${hl(e.n,terms)}</b> <span class="t">${hl(e.t,terms)}</span><div class="m">p. ${esc(e.p)} · ${e.u?`<a href="${e.u}" target="_blank" rel="noopener">${esc(e.l)}</a>`:esc(e.l)}</div></div>`});
 $("#out").insertAdjacentHTML("beforeend",h);shown=Math.min(res.length,shown+STEP);$("#more").hidden=shown>=res.length}
const groupOf=e=>e.a+(e.s?" — "+e.s:"");
let tm;$("#q").addEventListener("input",()=>{clearTimeout(tm);tm=setTimeout(run,120)});
sel.addEventListener("change",run);$("#nameonly").addEventListener("change",run);$("#more").addEventListener("click",()=>more());
$("#toggle").addEventListener("click",()=>{const r=document.documentElement;const d=r.dataset.theme?r.dataset.theme==="dark":matchMedia("(prefers-color-scheme: dark)").matches;r.dataset.theme=d?"light":"dark"});
try{const p=new URLSearchParams(location.hash.slice(1));if(p.get("q"))$("#q").value=p.get("q");if(p.get("s"))sel.value=p.get("s")}catch(e){}
run();
</script></body></html>
"""
