"""Write places.html ("Places", the draft place-name glossary) and data/places.json from build/names/glossary.json.

Run by build_site.py after the finder pages (it copies the header and footer of index.html); can be run alone:
    python3 build/names/build_names.py
glossary.json is made by collect.py (see there for what goes in a cell: only forms our books already use).
"""
import html, json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
BUILD = os.path.dirname(HERE)
SITE = os.path.dirname(BUILD)
sys.path.insert(0, os.path.join(BUILD, "finders"))

COLS = [("tc", "Chinese (traditional)"), ("sc", "Chinese (simplified)"), ("jo", "Japanese (old forms)"),
        ("jn", "Japanese (new forms)"), ("ko", "Korean (Hangul)"), ("py", "Pinyin"), ("wg", "Wade-Giles"), ("oth", "Postal or other romanisation"),
        ("hep", "Hepburn"), ("mr", "McCune–Reischauer"), ("mn", "Mongolian (romanised)"), ("mns", "Mongolian (script)"),
        ("std", "Adopted standard form")]

PAGE = """__HEAD__<title>Places · Old Tables of East Asia</title>
<meta name="description" content="A draft glossary of the place names used in the books on this site, in every script and romanisation they print.">
<style>
__STYLE__
.crumbs{font-size:14px;color:var(--muted);margin:0 0 8px}.crumbs a{color:var(--accent);text-decoration:none}
.nm-intro{max-width:780px}
.nm-tools{display:flex;flex-wrap:wrap;gap:10px 16px;align-items:center;margin:18px 0 10px;font-size:15px}
.nm-tools input[type=search]{font:inherit;padding:6px 9px;border:1px solid var(--line);background:var(--panel);color:var(--ink);min-width:min(100%,280px);flex:1 1 280px;max-width:420px}
.nm-tools select{font:inherit;padding:5px 6px;border:1px solid var(--line);background:var(--panel);color:var(--ink)}
.nm-count{color:var(--muted);font-size:14px}
.nm-wrap{overflow:auto;border:1px solid var(--line);max-height:78vh;box-sizing:border-box;
  width:min(2200px, calc(100vw - 48px));margin-left:calc(50% - min(1100px, 50vw - 24px))}
@media (max-width:700px){.nm-wrap{width:calc(100vw - 32px);margin-left:calc(50% - 50vw + 16px)}}
.nm-key,.nm-tools{max-width:100%;overflow-wrap:anywhere}
@media (max-width:700px){.nm-tools input[type=search]{min-width:0;flex-basis:100%}.nm-tools label{white-space:normal}
  details.nm-cols>div{position:static;columns:1;min-width:0;max-width:calc(100vw - 32px);box-shadow:none}}
table.nm{border-collapse:collapse;font-size:14px;min-width:1700px;width:100%}
table.nm th,table.nm td{border-bottom:1px solid var(--line);padding:5px 8px;vertical-align:top;text-align:left}
table.nm thead th{position:sticky;top:0;background:var(--panel);font-weight:normal;color:var(--muted);font-size:13px;z-index:2;border-bottom:2px solid var(--line)}
table.nm td:first-child,table.nm th:first-child{position:sticky;left:0;background:var(--bg,var(--panel));z-index:1;min-width:170px;max-width:220px}
table.nm thead th:first-child{z-index:3;background:var(--panel)}
table.nm tr.nm-sub td{border-top:none}
table.nm tr.nm-sub td:first-child{padding-left:22px;color:var(--muted);font-size:13px}
table.nm tr.nm-first td{border-top:1px solid var(--line)}
.nm-place{font-size:15px;color:var(--ink)}
.nm-meta{display:block;color:var(--muted);font-size:12.5px}
.nm-f{display:block;white-space:nowrap}
.nm-f+.nm-f{color:var(--muted)}
.nm-tag{display:inline-block;font-size:11.5px;border:1px solid var(--line);padding:0 4px;margin-right:4px;color:var(--muted)}
td.nm-ll{white-space:nowrap;font-variant-numeric:tabular-nums;color:var(--muted)}
.nm-empty{color:var(--muted)}
.nm-anchor{color:var(--muted);text-decoration:none;font-size:13px}.nm-anchor:hover{color:var(--accent)}
.nm-meta a{color:var(--accent)}
.nm-chip{font-size:14px;margin:0 0 8px;padding:6px 10px;border:1px solid var(--line);background:var(--panel);display:inline-block}
.nm-chip a{color:var(--accent);margin-left:6px}.nm-chip[hidden]{display:none}
tr.nm-ev td{background:var(--panel);font-size:13.5px;position:static}
.nm-evl{max-height:260px;overflow:auto;max-width:min(1100px, calc(100vw - 70px));position:sticky;left:8px}.nm-evl div{margin:2px 0}.nm-evl a{color:var(--accent)}
.nm-add{border-bottom:1px dotted var(--muted);cursor:help}
.nm-tr{font-style:italic;cursor:help}
.nm-key{font-size:13px;color:var(--muted);margin:4px 0 8px}
.nm-same a{color:var(--accent)}
.nm-cols{position:relative}.nm-cols summary{cursor:pointer;color:var(--accent)}
.nm-cols>div{position:absolute;z-index:5;background:var(--panel);border:1px solid var(--line);padding:8px 12px;margin-top:4px;
  columns:2;column-gap:18px;min-width:min(420px,86vw);font-size:14px;box-shadow:0 2px 8px rgba(0,0,0,.12)}
.nm-cols label{display:block;white-space:nowrap;break-inside:avoid}
.nm-cols .nm-cb{column-span:all;margin-top:6px;font-size:13px}
</style></head><body>__BAND__
<main>
<div class="crumbs"><a href="about.html">About</a> › Places</div>
<h2 style="font-weight:normal;font-size:28px;margin:4px 0 6px">Places</h2>
<div class="nm-tools">
<input type="search" id="nm-q" placeholder="Search any form: 北平, Peiping, Keijō, Mukden…" aria-label="Search names">
<label>Where <select id="nm-r"><option value="">Everywhere</option>
<option value="em">Japanese empire (to 1936, with Manchukuo)</option><option value="jp">Japan</option><option value="kr">Korea</option>
<option value="tw">Taiwan</option><option value="kf">Karafuto</option><option value="ns">South Seas</option>
<option value="cx mc">China, including Manchuria</option><option value="cx">China, excluding Manchuria</option>
<option value="mc">Manchuria (with Kwantung)</option><option value="se">Southeast Asia</option><option value="rw">Rest of the world</option></select></label>
<label>Kind <select id="nm-k"><option value="">All</option>__KINDS__</select></label>
<label><input type="checkbox" id="nm-sub"> only places with other names</label>
<label title="Hide forms added from reference data and forms used only in our English translations"><input type="checkbox" id="nm-orig"> only forms printed in the tables</label>
<details class="nm-cols"><summary>Columns</summary><div id="nm-cols"></div></details>
<span class="nm-count" id="nm-n"></span>
</div>
<p class="nm-chip" id="nm-chip" hidden></p>
<p class="nm-key">Plain: printed in a table of our books · <span class="nm-tr">italic</span>: used only in our English translations · <span class="nm-add">dotted</span>: added from reference data (Hangul, McCune–Reischauer, Hepburn, English Wikipedia) or the unambiguous pinyin reading of the characters; hover for the source.</p>
<div class="nm-wrap"><table class="nm"><thead><tr><th>Place</th>__TH__<th class="nmc-ll">Lat, long</th><th class="nmc-whg">WHG</th><th class="nmc-wp">Wikipedia</th><th class="nmc-nb">Books</th></tr></thead><tbody id="nm-b"></tbody></table></div>
<noscript><p>The glossary needs JavaScript. The data is also at <a href="data/places.json">data/places.json</a>.</p></noscript>
<p style="font-size:14px;color:var(--muted)">Download: <a href="data/place-names.sqlite">data/place-names.sqlite</a> (SQLite database: places, names, every form with its system and years, and every label as printed with its book and table) · <a href="data/places.json">data/places.json</a> (this table) · <a href="data/places-evidence.json">data/places-evidence.json</a> (labels as printed, per place).</p>
<div class="llmwarn" role="note"><b>Warning:</b> These names were transcribed by vision models and matched and sorted by machine. Check the tables, and the original scans linked from them, before relying on a form.</div>
__FOOT__
</main>
<script>
const D=__DATA__, C=__COLS__, P=__PARENTS__, POP=new Set(__POP__), VAR=__VAR__;
// search folds character variants together (臺/台, 滿/満/满) and drops diacritics
const fold=s=>[...s.normalize("NFKD").replace(/[\\u0300-\\u036f]/g,"").toLowerCase()].map(c=>VAR[c]||c).join("").replace(/[^a-z0-9\\u3040-\\u30ff\\u3400-\\u9fff\\uf900-\\ufaff\\uac00-\\ud7af]/g,"");
const esc=s=>String(s).replace(/[&<>"]/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]));
const BYID={}; D.forEach(e=>BYID[e.id]=e);
const up=id=>(BYID[id]&&BYID[id].up)||(P[id]&&P[id].up)||"";
const nameOf=id=>(BYID[id]&&BYID[id].en)||(P[id]&&P[id].en)||id;
const KIDS={};
D.forEach(e=>{let a=e.up,seen=new Set();while(a&&!seen.has(a)){seen.add(a);(KIDS[a]=KIDS[a]||[]).push(e.id);a=up(a)}});
D.forEach(e=>{e.key=fold(e.en+" "+(e.today||"")+" "+(e.today_ko||"")+" "+(e.same||[]).map(x=>x.cjk).join(" ")+" "+e.rows.map(r=>r.note+" "+Object.values(r.cols).flat().join(" ")+" "+Object.values(r.added||{}).flat().join(" ")).join(" "))});
const tb=document.getElementById("nm-b");
const yr=y=>y?(y[0]===y[1]?String(y[0]):y[0]+"–"+y[1]):"";
function cell(v,a,src,orig,as,fy){
  const pr=(v||[]).filter(f=>!orig||(src||{})[f]!=="x").map(f=>{const y=(fy||{})[f],t=y?" · in books of "+yr(y):"";
    return (src||{})[f]==="x"
    ?'<span class="nm-f"><span class="nm-tr" title="used in our English translations, not printed in the tables'+t+'">'+esc(f)+'</span></span>'
    :'<span class="nm-f"'+(y?' title="printed in books of '+yr(y)+'"':"")+'>'+esc(f)+'</span>'}).join("");
  return pr+(orig?"":(a||[]).map(f=>'<span class="nm-f"><span class="nm-add" title="added: '+esc((as||{})[f]||"not printed in our books")+'">'+esc(f)+'</span></span>').join(""))}
let ONLY="", WITHIN="";
function readHash(){const h=decodeURIComponent(location.hash.slice(1));ONLY="";WITHIN="";
  if(h.startsWith("in="))WITHIN=h.slice(3);else if(h&&BYID[h])ONLY=h;}
function within(e,w){let a=e.up,seen=new Set();while(a&&!seen.has(a)){if(a===w)return true;seen.add(a);a=up(a)}return false}
function head(e){
  let h='<span class="nm-place">'+esc(e.en)+'</span> <a class="nm-anchor" href="#'+encodeURIComponent(e.id)+'" title="link to this place">¶</a>';
  h+='<span class="nm-meta">'+esc(e.k)+' · '+esc(e.r)+(e.up&&e.up!=="world"&&e.up!=="empire"?' · in <a href="#'+(BYID[e.up]?"":"in=")+encodeURIComponent(e.up)+'">'+esc(nameOf(e.up))+'</a>':"")+'</span>';
  if(e.today||e.today_ko)h+='<span class="nm-meta" title="present-day name (not printed in our books)">today '+esc([e.today,e.today_ko].filter(Boolean).join(" "))+'</span>';
  const yrs=e.rows[0].yrs; if(yrs)h+='<span class="nm-meta" title="edition years of the books that print this name">printed '+yr(yrs)+'</span>';
  const kids=KIDS[e.id]; if(kids&&kids.length)h+='<span class="nm-meta"><a href="#in='+encodeURIComponent(e.id)+'">'+kids.length+(kids.length===1?" place":" places")+' in it</a></span>';
  if(e.ne)h+='<span class="nm-meta"><a href="#" data-ev="'+esc(e.id)+'">printed in '+e.ne+(e.ne===1?" table":" tables")+' ▸</a></span>';
  if(POP.has(e.id))h+='<span class="nm-meta"><a href="figures/population.html#p='+encodeURIComponent(e.id)+'">population figures</a></span>';
  if(e.same)h+='<span class="nm-meta nm-same">same characters as '+e.same.map(x=>'<a href="#'+encodeURIComponent(x.id)+'">'+esc(x.en)+'</a> ('+esc(x.r)+')').join(", ")+'</span>';
  return h}
function render(){
  readHash();
  const q=fold(document.getElementById("nm-q").value), r=document.getElementById("nm-r").value,
        k=document.getElementById("nm-k").value, sub=document.getElementById("nm-sub").checked, orig=document.getElementById("nm-orig").checked;
  const chip=document.getElementById("nm-chip");
  chip.innerHTML=ONLY?'Showing one place: <b>'+esc(nameOf(ONLY))+'</b> <a href="#" id="nm-clear">show all</a>'
    :WITHIN?'Places in <b>'+esc(nameOf(WITHIN))+'</b> <a href="#" id="nm-clear">show all</a>':"";
  chip.hidden=!(ONLY||WITHIN);
  let out=[], n=0;
  for(const e of D){
    if(ONLY){if(e.id!==ONLY)continue}
    else{
      if(WITHIN&&!within(e,WITHIN))continue;
      if(r&&!r.split(" ").some(x=>e.t.includes(x))||k&&e.k!==k||sub&&e.rows.length<2||q&&!e.key.includes(q)) continue;
    }
    n++;
    e.rows.forEach((row,i)=>{
      const first=i===0;
      let h='<tr class="'+(first?"nm-first":"nm-sub")+'"'+(first?' id="'+esc(e.id)+'"':"")+'><td>'+(first?head(e)
        :'<span class="nm-tag">'+esc(row.status||(row.note?"former name":"other form"))+'</span>'+esc(row.note||"")+(row.yrs?'<span class="nm-meta">printed '+yr(row.yrs)+'</span>':""))+'</td>';
      for(const [c] of C) h+='<td class="nmc-'+c+'">'+cell(row.cols[c],(row.added||{})[c],row.src,orig,row.asrc,row.fy)+'</td>';
      if(first){
        h+='<td class="nm-ll nmc-ll">'+(e.ll?e.ll.join(", "):"")+'</td>';
        h+='<td class="nmc-whg">'+(e.whg?'<a href="https://whgazetteer.org/places/'+e.whg.pid+'/portal" title="'+esc(e.whg.title||"")+'">WHG</a>':"")+'</td>';
        h+='<td class="nmc-wp">'+(e.wp?'<a href="https://en.wikipedia.org/wiki/'+encodeURIComponent(e.wp.title.replace(/ /g,"_"))+'" title="'+esc(e.wp.title+" ("+(e.wp.how||"")+")")+'">WP</a>':"")+'</td>';
        h+='<td class="nmc-nb">'+e.nb+'</td>';
      } else h+='<td class="nmc-ll"></td><td class="nmc-whg"></td><td class="nmc-wp"></td><td class="nmc-nb"></td>';
      out.push(h+'</tr>');
    });
    out.push('<tr class="nm-ev" data-for="'+esc(e.id)+'" hidden><td colspan="18"></td></tr>');
  }
  tb.innerHTML=out.join("")||'<tr><td colspan="18" class="nm-empty">No place matches.</td></tr>';
  if(ONLY&&BYID[ONLY]&&BYID[ONLY].ne){const a=tb.querySelector('a[data-ev]'),tr=tb.querySelector('tr.nm-ev');if(a&&tr){a.textContent=a.textContent.replace("▸","▾");evidence(ONLY,tr)}}
  document.getElementById("nm-n").textContent=n.toLocaleString()+(n===1?" place":" places");
}
// evidence: every label as printed, loaded on first use
let EV=null;
async function evidence(id,tr){
  if(!EV){try{EV=await (await fetch("data/places-evidence.json")).json()}catch(_){tr.firstChild.textContent="The list could not be loaded here; it is in data/places-evidence.json.";tr.hidden=false;return}}
  const L=(EV.places||{})[id]||[], by={};
  L.forEach(([b,t,l])=>{(by[b]=by[b]||[]).push([t,l])});
  tr.firstChild.innerHTML='<div class="nm-evl">'+Object.entries(by).map(([b,xs])=>{const bk=EV.books[b]||[b,""];
    return '<div><b>'+esc(bk[0])+'</b>'+(bk[1]?" ("+bk[1]+")":"")+': '+xs.map(([t,l])=>'<a href="book/'+encodeURIComponent(b)+'/#'+encodeURIComponent(t)+'">'+esc(l)+'</a>').join(" · ")+'</div>'}).join("")+'</div>';
  tr.hidden=false;
}
// columns: shown or hidden, remembered in this browser
const ALLC=C.concat([["ll","Lat, long"],["whg","WHG"],["wp","Wikipedia"],["nb","Books"]]), cst=document.createElement("style"); document.head.appendChild(cst);
let hidden=[]; try{hidden=JSON.parse(localStorage.getItem("nm-hidden")||"[]")}catch(_){hidden=[]}
function applyCols(){cst.textContent=hidden.map(c=>".nmc-"+c+"{display:none}").join("");try{localStorage.setItem("nm-hidden",JSON.stringify(hidden))}catch(_){}}
document.getElementById("nm-cols").innerHTML=ALLC.map(([c,l])=>'<label><input type="checkbox" data-c="'+c+'"'+(hidden.includes(c)?"":" checked")+'> '+esc(l)+'</label>').join("")
  +'<div class="nm-cb"><a href="#" id="nm-all">show all</a> · <a href="#" id="nm-none">hide all</a></div>';
document.getElementById("nm-cols").addEventListener("change",ev=>{const c=ev.target.dataset.c;if(!c)return;hidden=ev.target.checked?hidden.filter(x=>x!==c):hidden.concat([c]);applyCols()});
function setAll(show){hidden=show?[]:ALLC.map(x=>x[0]);document.querySelectorAll("#nm-cols input").forEach(i=>i.checked=show);applyCols()}
document.getElementById("nm-all").onclick=ev=>{ev.preventDefault();setAll(true)};document.getElementById("nm-none").onclick=ev=>{ev.preventDefault();setAll(false)};
applyCols();
let t;["nm-q","nm-r","nm-k","nm-sub","nm-orig"].forEach(id=>document.getElementById(id).addEventListener("input",()=>{clearTimeout(t);t=setTimeout(()=>{if(location.hash)history.replaceState(null,"",location.pathname+location.search);render()},120)}));
const p=new URLSearchParams(location.search); if(p.get("q")) document.getElementById("nm-q").value=p.get("q");
if(p.get("w")){const o=[...document.getElementById("nm-r").options].find(o=>o.value===p.get("w"));if(o)o.selected=true}
window.addEventListener("hashchange",()=>{render();window.scrollTo(0,document.querySelector(".nm-tools").offsetTop-10)});
document.addEventListener("click",ev=>{
  if(ev.target.id==="nm-clear"){ev.preventDefault();history.pushState(null,"",location.pathname+location.search);render();return}
  const a=ev.target.closest("a[data-ev]");if(!a)return;ev.preventDefault();
  const tr=tb.querySelector('tr.nm-ev[data-for="'+CSS.escape(a.dataset.ev)+'"]');
  if(!tr.hidden){tr.hidden=true;a.textContent=a.textContent.replace("▾","▸");return}
  a.textContent=a.textContent.replace("▸","▾");evidence(a.dataset.ev,tr);
});
render();
</script>
</body></html>
"""


def variant_map(entries):
    """{character: representative} so that search folds variants together: traditional/simplified Chinese (the site's
    simplify tables) and old/new Japanese forms (the same tables and OpenCC's lists in shinjitai.json). Only the variant
    groups of characters our data uses are kept."""
    T = json.load(open(os.path.join(BUILD, "simplify", "tables.json"), encoding="utf-8"))
    V = json.load(open(os.path.join(HERE, "shinjitai.json"), encoding="utf-8"))
    par = {}

    def find(x):
        while par.get(x, x) != x:
            par[x] = par.get(par[x], par[x])
            x = par[x]
        return x

    def union(a, b):
        ra, rb = find(a), find(b)
        if ra != rb:
            par[max(ra, rb)] = min(ra, rb)
    for table in (T["zh"], T["ja"], V["new"], V["sc"]):
        for a, b in table.items():
            if len(a) == 1 and len(b) == 1:
                union(a, b)
    used = set()
    for e in entries:
        for r in e["rows"]:
            for v in list(r["cols"].values()) + list(r.get("added", {}).values()):
                for f in v:
                    used |= set(f)
    groups = {}
    for c in par:
        groups.setdefault(find(c), set()).add(c)
    out = {}
    for root, members in groups.items():
        members.add(root)
        if members & used:
            for c in members:
                if c != root:
                    out[c] = root
    return out


def main():
    from build_all import chrome
    G = json.load(open(os.path.join(HERE, "glossary.json"), encoding="utf-8"))
    E = G["entries"]
    ORDER = ["China", "Manchuria", "Kwantung", "Korea", "Taiwan", "Japan", "Karafuto", "South Seas", "Other"]
    E.sort(key=lambda e: (ORDER.index(e["r"]) if e["r"] in ORDER else 99, e["en"].lower()))
    EV = json.load(open(os.path.join(SITE, "data", "places-evidence.json"), encoding="utf-8"))["places"] \
        if os.path.exists(os.path.join(SITE, "data", "places-evidence.json")) else {}
    slim = [{k: e[k] for k in ("id", "en", "k", "r", "t", "up", "rows", "nb", "ll", "whg", "wp", "today", "today_ko", "same") if k in e} for e in E]
    for e in slim:
        e["rows"] = [{k: r[k] for k in ("note", "status", "cols", "added", "src", "asrc", "fy", "yrs") if r.get(k)} | {"cols": r["cols"], "note": r["note"]}
                     for r in e["rows"]]
        if EV.get(e["id"]):
            e["ne"] = len({(b, t) for b, t, _l in EV[e["id"]]})
        if e.get("same"):
            e["same"] = list({x["id"]: x for x in e["same"]}.values())
    pop_p = os.path.join(SITE, "data", "population", "index.json")
    pop = sorted(set(json.load(open(pop_p, encoding="utf-8"))["places"]) & {e["id"] for e in E}) if os.path.exists(pop_p) else []
    head, style, band, foot = chrome("")
    kinds = sorted({e["k"] for e in E if e["k"]})
    page = (PAGE.replace("__HEAD__", head).replace("__STYLE__", style).replace("__BAND__", band).replace("__FOOT__", foot)
            .replace("__KINDS__", "".join(f'<option>{html.escape(k)}</option>' for k in kinds))
            .replace("__TH__", "".join(f'<th class="nmc-{k}">{html.escape(l)}</th>' for k, l in COLS))
            .replace("__N__", f"{len(E):,}").replace("__R__", f"{sum(len(e['rows']) for e in E):,}")
            .replace("__COLS__", json.dumps(COLS, ensure_ascii=False))
            .replace("__PARENTS__", json.dumps(G.get("parents", {}), ensure_ascii=False, separators=(",", ":")))
            .replace("__POP__", json.dumps(pop, separators=(",", ":")))
            .replace("__VAR__", json.dumps(variant_map(slim), ensure_ascii=False, separators=(",", ":")))
            .replace("__DATA__", json.dumps(slim, ensure_ascii=False, separators=(",", ":"))))
    open(os.path.join(SITE, "places.html"), "w", encoding="utf-8").write(page)
    os.makedirs(os.path.join(SITE, "data"), exist_ok=True)
    json.dump({"_doc": "Draft place-name glossary of Old Tables of East Asia (places.html). cols: " +
               ", ".join(f"{k} = {l}" for k, l in COLS) + ". Only forms printed in our books or used in our translations.",
               "entries": slim}, open(os.path.join(SITE, "data", "places.json"), "w", encoding="utf-8"),
              ensure_ascii=False, separators=(",", ":"))
    return {"places": len(E)}


if __name__ == "__main__":
    print(main())
