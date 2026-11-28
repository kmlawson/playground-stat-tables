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
main,.band>div{max-width:2200px}
@media (min-width:701px){main,.band>div{padding-left:24px;padding-right:24px}}
.nm-key,.llmwarn,footer,.nm-dl{max-width:980px}
.nm-wrap{overflow:auto;border:1px solid var(--line);max-height:78vh;box-sizing:border-box;width:100%}
.nm-key,.nm-tools{max-width:100%;overflow-wrap:anywhere}
.nm-tools label{display:inline-flex;align-items:center;gap:6px;max-width:100%;flex-wrap:wrap}
.nm-tools select{max-width:100%;min-width:0}
@media (max-width:700px){.nm-tools input[type=search]{min-width:0;flex-basis:100%}.nm-tools label{white-space:normal}
  .nm-tools select{max-width:calc(100vw - 110px)}}
table.nm{border-collapse:collapse;font-size:14px;min-width:1700px;width:100%}
table.nm th,table.nm td{border-bottom:1px solid var(--line);padding:5px 8px;vertical-align:top;text-align:left}
table.nm thead th{position:sticky;top:0;background:var(--panel);font-weight:normal;color:var(--muted);font-size:13px;z-index:2;border-bottom:2px solid var(--line)}
table.nm td:first-child,table.nm th:first-child{position:sticky;left:0;background:var(--bg,var(--panel));z-index:1;min-width:170px;max-width:220px}
table.nm thead th:first-child{z-index:3;background:var(--panel)}
table.nm tr.nm-sub td{border-top:none}
table.nm tr.nm-sub td:first-child{padding-left:22px;color:var(--muted);font-size:13px}
table.nm tr.nm-first td{border-top:1px solid var(--line)}
.nm-place{font-size:15px;color:var(--ink)}
.nm-alt{font-size:14px;color:var(--muted);margin-left:2px;white-space:nowrap}
.nm-hd{display:flex;align-items:flex-start;gap:0}.nm-hd>.nm-tog,.nm-hd>.nm-tog0{flex:none;margin-top:2px}.nm-hdn{min-width:0}
table.nm td:first-child,table.nm th:first-child{min-width:230px}
.nm-x{display:none}td.nm-open .nm-x{display:inline}
.nm-more{font:inherit;font-size:12px;padding:0 5px;margin-top:2px;border:1px solid var(--line);background:transparent;color:var(--accent);cursor:pointer}
table.nm tr.nm-first td{border-bottom:none;padding-bottom:1px}
table.nm tr.nm-info td{padding:0 8px 6px 30px;font-size:12.5px;color:var(--muted);border-top:none}
.nm-infol{position:sticky;left:30px;max-width:min(1200px, calc(100vw - 90px))}
.nm-infol a{color:var(--accent)}.nm-sep{color:var(--line)}
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
.nm-colbar{display:flex;flex-wrap:wrap;gap:6px 10px;align-items:center;font-size:14px;margin:0 0 8px}
.nm-colbar button{font:inherit;padding:4px 10px;border:1px solid var(--accent);background:var(--panel);color:var(--accent);cursor:pointer}
.nm-colbar a{color:var(--accent)}
.nm-views{margin-right:10px}.nm-views a.on{color:var(--ink);font-weight:bold;text-decoration:none}
.nm-tog{font:inherit;font-size:12px;width:20px;height:20px;padding:0;margin:0 4px 0 -2px;border:1px solid var(--line);background:var(--panel);color:var(--accent);cursor:pointer;vertical-align:1px}
.nm-tog0{display:inline-block;width:22px}
tr.nm-node td{background:var(--panel);font-size:15px;position:sticky;left:0}
:root{--tA:#cfe3d5;--tB:#e2efe6;--tC:#f3f8f4}
@media (prefers-color-scheme: dark){:root:not([data-theme="light"]){--tA:#2b4535;--tB:#22372a;--tC:#1a2a20}}
:root[data-theme="dark"]{--tA:#2b4535;--tB:#22372a;--tC:#1a2a20}
table.nm tr.tA td{background:var(--tA)}table.nm tr.tB td{background:var(--tB)}table.nm tr.tC td{background:var(--tC)}
table.nm th[data-col]{cursor:pointer;user-select:none}
table.nm th[data-col]:hover{color:var(--ink)}
table.nm th.cf,table.nm td.cf{width:16px;min-width:16px;max-width:16px;padding:4px 2px;overflow:hidden;white-space:nowrap}
table.nm td.cf>*{display:none}
table.nm th.cf{color:var(--accent);text-align:center}
.nm-mv{display:inline-flex;gap:2px;margin-left:4px;vertical-align:middle}
.nm-mv button{font:inherit;font-size:11px;line-height:1;padding:1px 4px;border:1px solid var(--line);background:var(--panel);color:var(--muted);cursor:pointer}
.nm-mv button:hover{color:var(--accent);border-color:var(--accent)}
table.nm th.nm-drop{box-shadow:inset 3px 0 0 var(--accent)}
.nm-srch a{white-space:nowrap}
tr.nm-cat td{color:var(--muted);font-size:12.5px;text-transform:uppercase;letter-spacing:.04em;border-bottom:none;padding-top:8px}
tr.nm-ctx td{opacity:.6}.nm-cnt{color:var(--muted);font-size:13px;font-weight:normal}
[hidden]{display:none!important}
#nm-cols{background:var(--panel);border:1px solid var(--line);padding:8px 12px;margin:0 0 10px;columns:4 160px;column-gap:18px;font-size:14px;max-width:980px}
#nm-cols label{display:block;white-space:nowrap;break-inside:avoid}
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
<label><input type="checkbox" id="nm-cjkfirst"> Hanzi/Kanji/Hanja names first</label>
<label title="Hide forms added from reference data and forms used only in our English translations"><input type="checkbox" id="nm-orig"> only forms printed in the tables</label>
<span class="nm-count" id="nm-n"></span>
</div>
<div class="nm-colbar"><span class="nm-views">View: <a href="#" data-view="tree">hierarchy</a> · <a href="#" data-view="az">A–Z</a>
<span id="nm-fold">(<a href="#" id="nm-exp">unfold all</a> · <a href="#" id="nm-shut">fold all</a>)</span></span>
<button type="button" id="nm-colbtn" aria-expanded="false" aria-controls="nm-cols">Columns ▾</button>
<span>show: <a href="#" data-preset="all">all</a> · <a href="#" data-preset="chars">characters</a> · <a href="#" data-preset="rom">romanisations</a> · <a href="#" data-preset="zh">Chinese</a> · <a href="#" data-preset="jk">Japanese &amp; Korean</a> · <a href="#" data-preset="links">links</a></span></div>
<div id="nm-cols" hidden></div>
<p class="nm-chip" id="nm-chip" hidden></p>
<p class="nm-key">Plain: printed in a table of our books · <span class="nm-tr">italic</span>: used only in our English translations · <span class="nm-add">dotted</span>: added from reference data (Hangul, McCune–Reischauer, Hepburn, English Wikipedia) or the unambiguous pinyin reading of the characters; hover for the source.</p>
<div class="nm-wrap"><table class="nm"><thead id="nm-h"></thead><tbody id="nm-b"></tbody></table></div>
<noscript><p>The glossary needs JavaScript. The data is also at <a href="data/places.json">data/places.json</a>.</p></noscript>
<p class="nm-dl" style="font-size:14px;color:var(--muted)">Download: <a href="data/place-names.sqlite">data/place-names.sqlite</a> (SQLite database: places, names, every form with its system and years, and every label as printed with its book and table) · <a href="data/places.json">data/places.json</a> (this table) · <a href="data/places-evidence.json">data/places-evidence.json</a> (labels as printed, per place).</p>
<div class="llmwarn" role="note"><b>Warning:</b> These names were transcribed by vision models and matched and sorted by machine. Check the tables, and the original scans linked from them, before relying on a form.</div>
__FOOT__
</main>
<script>
const KEEP=__KEEP__;
// column order and folded columns, remembered in this browser (Place stays first)
const LABEL=Object.fromEntries(__COLS__.concat([["ll","Lat, long"],["whg","WHG"],["wp","Wikipedia"],["nb","Books"]]));
const DEFAULT_ORDER=Object.keys(LABEL);
let ORDER=DEFAULT_ORDER.slice(), FOLD=new Set();
try{const o=JSON.parse(localStorage.getItem("nm-order")||"null");if(Array.isArray(o)&&o.length===DEFAULT_ORDER.length&&DEFAULT_ORDER.every(c=>o.includes(c)))ORDER=o}catch(_){}
try{FOLD=new Set(JSON.parse(localStorage.getItem("nm-fold")||"[]"))}catch(_){}
function saveCols(){try{localStorage.setItem("nm-order",JSON.stringify(ORDER));localStorage.setItem("nm-fold",JSON.stringify([...FOLD]))}catch(_){}}
function renderHead(){
  document.getElementById("nm-h").innerHTML='<tr><th>Place</th>'+ORDER.map(c=>FOLD.has(c)
    ?'<th class="nmc-'+c+' cf" data-col="'+c+'" draggable="true" title="'+esc(LABEL[c])+' (folded): click to unfold">▸</th>'
    :'<th class="nmc-'+c+'" data-col="'+c+'" draggable="true" title="click to fold; drag, or use ‹ ›, to move"><span>'+esc(LABEL[c])+'</span><span class="nm-mv"><button type="button" data-mv="-1" aria-label="move left">‹</button><button type="button" data-mv="1" aria-label="move right">›</button></span></th>').join("")+'</tr>';
}
const D=__DATA__, C=__COLS__, P=__PARENTS__, POP=new Set(__POP__), VAR=__VAR__;
// search folds character variants together (臺/台, 滿/満/满) and drops diacritics
const fold=s=>[...s.normalize("NFKD").replace(/[\\u0300-\\u036f]/g,"").toLowerCase()].map(c=>VAR[c]||c).join("").replace(/[^a-z0-9\\u3040-\\u30ff\\u3400-\\u9fff\\uf900-\\ufaff\\uac00-\\ud7af]/g,"");
const esc=s=>String(s).replace(/[&<>"]/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]));
const BYID={}; D.forEach(e=>BYID[e.id]=e);
// canonical names: pinyin for Chinese-language places, McCune-Reischauer for Korea, Hepburn for the Japanese places
// (Taiwan: Hepburn with pinyin, the site's rule); the characters as printed are the other half of the heading
const TONED=/[āáǎàēéěèīíǐìōóǒòūúǔùǖǘǚǜ]/;
const PFOLD=s=>s.normalize("NFKD").replace(/[̀-ͯ]/g,"").toLowerCase().replace(/[^a-z]/g,"");
function allOf(r,c){return [...(r.cols[c]||[]),...((r.added||{})[c]||[])]}
function romName(e){
  const r=e.rows[0], head=e.en;
  const std=(r.cols.std||[]).filter(x=>(r.src||{})[x]!=="x");
  if(std.length){const k=std.filter(x=>KEEP.includes(x)).sort((a,b)=>b.length-a.length);
    return k[0]||std[0]}                              // the adopted standard: Kwantung Leased Territory, Hong Kong, Harbin
  if(["China","Manchuria","Kwantung"].includes(e.r)){
    const p=allOf(r,"py").filter(x=>!/\\s(Shì|Shěng|Xiàn|Qū)$/.test(x)), pf=new Set(p.map(PFOLD));
    if(pf.has(PFOLD(head.split(/\\s*[,(]/)[0])))return TONED.test(head)?head.split(/\\s*\\(/)[0]:(p.find(x=>TONED.test(x)&&PFOLD(x)===PFOLD(head))||head);
    return p.find(x=>TONED.test(x))||p[0]||(r.cols.oth||[])[0]||(r.cols.wg||[])[0]||head;   // Qiqihar: Tsitsihar, not 'Chichiharu'
  }
  if(e.r==="Korea"){const m=[...((r.added||{}).mr||[]),...(r.cols.mr||[])].filter(x=>!/\\s(Province|District|County|Town)$/.test(x));return m[0]||head}
  if(e.r==="Taiwan"){const p=allOf(r,"py").filter(x=>!TONED.test(x));const pp=p[0];return pp&&PFOLD(pp)!==PFOLD(head)?head+" ("+pp+")":head}
  return head;
}
function cjkName(e){
  const r=e.rows[0], order=["China","Manchuria","Kwantung"].includes(e.r)?["tc","jo","jn","sc"]:["jo","tc","jn","sc"];
  for(const c of order){
    const printed=(r.cols[c]||[]).filter(x=>(r.src||{})[x]!=="x"&&/[㐀-鿿ァ-ヺ]/.test(x)).slice(0,3);
    if(printed.length)return printed.reduce((a,b)=>b.length<a.length?b:a);
  }
  for(const c of order){const a=allOf(r,c).filter(x=>/[㐀-鿿ァ-ヺ]/.test(x));if(a.length)return a[0]}
  return "";
}
D.forEach(e=>{e.rom=romName(e);e.cjk=cjkName(e)});
let CJKFIRST=false;try{CJKFIRST=localStorage.getItem("nm-cjkfirst")==="1"}catch(_){}
const shown=e=>CJKFIRST&&e.cjk?[e.cjk,e.rom]:[e.rom,e.cjk];
const up=id=>(BYID[id]&&BYID[id].up)||(P[id]&&P[id].up)||"";
const nameOf=id=>(BYID[id]&&BYID[id].rom)||(P[id]&&P[id].en)||id;
const KIDS={};
D.forEach(e=>{let a=e.up,seen=new Set();while(a&&!seen.has(a)){seen.add(a);(KIDS[a]=KIDS[a]||[]).push(e.id);a=up(a)}});
D.forEach(e=>{e.key=fold(e.en+" "+(e.today||"")+" "+(e.today_ko||"")+" "+(e.same||[]).map(x=>x.cjk).join(" ")+" "+e.rows.map(r=>r.note+" "+Object.values(r.cols).flat().join(" ")+" "+Object.values(r.added||{}).flat().join(" ")).join(" "))});
const tb=document.getElementById("nm-b");
const yr=y=>y?(y[0]===y[1]?String(y[0]):y[0]+"–"+y[1]):"";
function cell(v,a,src,orig,as,fy){
  const parts=(v||[]).filter(f=>!orig||(src||{})[f]!=="x").map(f=>{const y=(fy||{})[f],t=y?" · in books of "+yr(y):"";
    return (src||{})[f]==="x"
    ?'<span class="nm-f"><span class="nm-tr" title="used in our English translations, not printed in the tables'+t+'">'+esc(f)+'</span></span>'
    :'<span class="nm-f"'+(y?' title="printed in books of '+yr(y)+'"':"")+'>'+esc(f)+'</span>'});
  if(!orig)(a||[]).forEach(f=>parts.push('<span class="nm-f"><span class="nm-add" title="added: '+esc((as||{})[f]||"not printed in our books")+'">'+esc(f)+'</span></span>'));
  // three forms at most on the line; the rest behind "+N", so that a long list of spellings does not make the row tall
  if(parts.length<=3)return parts.join("");
  return parts.slice(0,3).join("")+'<span class="nm-x">'+parts.slice(3).join("")+'</span><button type="button" class="nm-more" data-n="'+(parts.length-3)+'">+'+(parts.length-3)+' more</button>';
}
function readHash(){const h=decodeURIComponent(location.hash.slice(1));ONLY="";WITHIN="";
  if(h.startsWith("in="))WITHIN=h.slice(3);else if(h&&BYID[h])ONLY=h;}
function within(e,w){let a=e.up,seen=new Set();while(a&&!seen.has(a)){if(a===w)return true;seen.add(a);a=up(a)}return false}
function searchTerms(e){
  // the most printed characters (shortest of the leading forms: 京城 rather than 京城府) and the heading without tones
  const r=e.rows[0],out=[];
  const cj=["jo","tc","jn","sc"].flatMap(c=>(r.cols[c]||[]).slice(0,3)).filter(f=>/[\u3400-\u9fff]/.test(f));
  if(cj.length)out.push(cj.reduce((a,b)=>b.length<a.length?b:a));
  // the romanised form the tables print most (pinyin or Wade-Giles first for China, Hepburn for the empire)
  const order=["China","Manchuria","Kwantung"].includes(e.r)?["py","wg","oth","std","hep"]:["hep","oth","mr","std","py","wg"];
  let lat="";
  for(const c of order){const f=(r.cols[c]||[]).find(x=>(r.src||{})[x]!=="x");if(f){lat=f;break}}
  if(!lat)lat=e.en.split(/\\s*[,(]/)[0].normalize("NFKD").replace(/[\u0300-\u036f]/g,"").replace(/[’ʻ]/g,"'").trim();
  if(lat&&!out.includes(lat))out.push(lat);
  return out}
function head(e,ctx){
  const [a1,a2]=shown(e);
  const h='<span class="nm-place">'+esc(a1)+'</span>'+(a2?' <span class="nm-alt">'+esc(a2)+'</span>':"")+' <a class="nm-anchor" href="#'+encodeURIComponent(e.id)+'" title="link to this place">¶</a>';
  return ctx?h+' <span class="nm-cnt">'+esc(e.k)+'</span>':h}
// the second line of a place: everything about it except its names, as one indented line under the names
function info(e){
  const it=[];
  it.push(esc(e.k)+' · '+esc(e.r)+(e.up&&e.up!=="world"&&e.up!=="empire"?' · in <a href="#'+(BYID[e.up]?"":"in=")+encodeURIComponent(e.up)+'">'+esc(nameOf(e.up))+'</a>':""));
  if(e.today||e.today_ko)it.push('<span title="present-day name (not printed in our books)">today '+esc([e.today,e.today_ko].filter(Boolean).join(" "))+'</span>');
  const yrs=e.rows[0].yrs; if(yrs)it.push('<span title="edition years of the books that print this name">printed '+yr(yrs)+'</span>');
  const kids=KIDS[e.id]; if(kids&&kids.length)it.push('<a href="#in='+encodeURIComponent(e.id)+'">'+kids.length+(kids.length===1?" place":" places")+' in it</a>');
  if(e.ne)it.push('<a href="#" data-ev="'+esc(e.id)+'">printed in '+e.ne+(e.ne===1?" table":" tables")+' ▸</a>');
  if(POP.has(e.id))it.push('<a href="figures/population.html#p='+encodeURIComponent(e.id)+'">population figures</a>');
  const qs=searchTerms(e); if(qs.length)it.push('search the site: '+qs.map(t=>'<a href="search.html#'+new URLSearchParams({q:t}).toString()+'" title="search all tables for '+esc(t)+'">'+esc(t)+'</a>').join(", "));
  if(PFOLD(e.en)!==PFOLD(e.rom)&&!e.rom.startsWith(e.en))it.push('<span title="the name the site&#39;s gazetteer and finder pages use">gazetteer: '+esc(e.en)+'</span>');
  if(e.same)it.push('same characters as '+e.same.map(x=>'<a href="#'+encodeURIComponent(x.id)+'">'+esc(x.en)+'</a> ('+esc(x.r)+')').join(", "));
  return it.join('<span class="nm-sep"> · </span>');
}
// ---- views: hierarchy (folding, A-Z within category) or flat A-Z
const CATI={country:0,colony:1,empire:1,region:1,world:1,province:2,prefecture:2,district:3,county:3,city:4,town:4,settlement:4,ward:5,island:6};
const CATN=["Countries","Colonies and regions","Provinces and prefectures","Districts and counties","Cities and towns","Wards","Islands","Other places"];
const catOf=k=>(k in CATI)?CATI[k]:7;
const SK=s=>s.normalize("NFKD").replace(/[̀-ͯ]/g,"").toLowerCase();
const NODE={};
function node(id){if(!NODE[id])NODE[id]={id,en:nameOf(id),k:(BYID[id]&&BYID[id].k)||"",entry:BYID[id]||null,kids:[]};return NODE[id]}
D.forEach(e=>node(e.id)); Object.keys(P).forEach(id=>node(id));
let ROOTS=[];
Object.values(NODE).forEach(n=>{const u=up(n.id);if(u&&u!==n.id&&NODE[u])NODE[u].kids.push(n);else ROOTS.push(n)});
(function reach(){const seen=new Set(),st=[...ROOTS];while(st.length){const n=st.pop();if(seen.has(n.id))continue;seen.add(n.id);st.push(...n.kids)}
  Object.values(NODE).forEach(n=>{if(!seen.has(n.id))ROOTS.push(n)})})();   // a parent loop in the gazetteer: shown at the top
const RORD=["empire","china","manchuria","world"];
const nm_=x=>x.entry?x.entry.rom:(x.rom||x.en);
const byName=(a,b)=>SK(nm_(a))<SK(nm_(b))?-1:SK(nm_(a))>SK(nm_(b))?1:0;
ROOTS.sort((a,b)=>{const ia=RORD.indexOf(a.id),ib=RORD.indexOf(b.id);return (ia<0?99:ia)-(ib<0?99:ib)||byName(a,b)});
Object.values(NODE).forEach(n=>n.kids.sort((a,b)=>catOf(a.k)-catOf(b.k)||byName(a,b)));
const NDESC={};function ndesc(n){if(n.id in NDESC)return NDESC[n.id];let c=0;for(const k of n.kids)c+=(k.entry?1:0)+ndesc(k);return NDESC[n.id]=c}
const DAZ=[...D].sort(byName);
let VIEW="tree";try{VIEW=localStorage.getItem("nm-view")||"tree"}catch(_){}
const OPEN=new Set(),SHUT=new Set();
const isOpen=(n,d)=>OPEN.has(n.id)||(!SHUT.has(n.id)&&d<1);
const TIER_TOP=new Set(["empire","china","world","japan","manchuria","chinaproper"]);
function tierOf(k,id){
  if(["country","empire","colony","world"].includes(k)||TIER_TOP.has(id))return "tA";   // countries and colonies
  if(["province","prefecture","region","district"].includes(k))return "tB";            // provinces, prefectures, regions
  return "tC";                                                                       // cities, counties and below
}
const TRAIL=["ll","whg","wp","nb"];
function tdFor(e,row,c,first,ctx,orig){
  const cls="nmc-"+c+(FOLD.has(c)?" cf":"")+(c==="ll"?" nm-ll":"");
  let v="";
  if(!ctx){
    if(c==="ll")v=first&&e.ll?e.ll.join(", "):"";
    else if(c==="whg")v=first&&e.whg?'<a href="https://whgazetteer.org/places/'+e.whg.pid+'/portal" title="'+esc((e.whg.title||"")+(e.whg.sources>1?" — WHG index record gathering "+e.whg.sources+" sources":" — one source record"))+'">WHG</a>':"";
    else if(c==="wp")v=first&&e.wp?'<a href="https://en.wikipedia.org/wiki/'+encodeURIComponent(e.wp.title.replace(/ /g,"_"))+'" title="'+esc(e.wp.title+" ("+(e.wp.how||"")+")")+'">WP</a>':"";
    else if(c==="nb")v=first?String(e.nb):"";
    else v=cell(row.cols[c],(row.added||{})[c],row.src,orig,row.asrc,row.fy);
  }
  return '<td class="'+cls+'">'+v+'</td>';
}
function entryRows(e,d,tog,ctx,orig){
  const lv=" "+tierOf(e.k,e.id);
  const pad='style="padding-left:8px"',padS='style="padding-left:30px"';
  const rows=ctx?[e.rows[0]]:e.rows,out=[];
  rows.forEach((row,i)=>{
    const first=i===0;
    let h='<tr class="'+(first?"nm-first":"nm-sub")+(ctx?" nm-ctx":"")+lv+'"'+(first?' id="'+esc(e.id)+'"':"")+'><td '+(first?pad:padS)+'>'+(first?'<div class="nm-hd">'+tog+'<div class="nm-hdn">'+head(e,ctx)+'</div></div>'
      :'<span class="nm-tag">'+esc(row.status||(row.note?"former name":"other form"))+'</span>'+esc(row.note||"")+(row.yrs?'<span class="nm-meta">printed '+yr(row.yrs)+'</span>':""))+'</td>';
    for(const c of ORDER) h+=tdFor(e,row,c,first,ctx,orig);
    out.push(h+'</tr>');
    if(first&&!ctx)out.push('<tr class="nm-info'+lv+'"><td colspan="18"><div class="nm-infol">'+info(e)+'</div></td></tr>');
  });
  if(!ctx)out.push('<tr class="nm-ev" data-for="'+esc(e.id)+'" hidden><td colspan="18"></td></tr>');
  return out.join("");
}
function render(){
  readHash();
  renderHead();
  const q=fold(document.getElementById("nm-q").value), r=document.getElementById("nm-r").value,
        k=document.getElementById("nm-k").value, sub=document.getElementById("nm-sub").checked, orig=document.getElementById("nm-orig").checked;
  const chip=document.getElementById("nm-chip");
  chip.innerHTML=ONLY?'Showing one place: <b>'+esc(nameOf(ONLY))+'</b> <a href="#" id="nm-clear">show all</a>'
    :WITHIN?'Places in <b>'+esc(nameOf(WITHIN))+'</b> <a href="#" id="nm-clear">show all</a>':"";
  chip.hidden=!(ONLY||WITHIN);
  document.querySelectorAll("[data-view]").forEach(a=>a.classList.toggle("on",a.dataset.view===VIEW));
  document.getElementById("nm-fold").hidden=VIEW!=="tree"||!!ONLY;
  const pass=e=>!(r&&!r.split(" ").some(x=>e.t.includes(x))||k&&e.k!==k||sub&&e.rows.length<2||q&&!e.key.includes(q));
  const active=!!(q||r||k||sub);
  let out=[], n=0;
  if(ONLY||VIEW==="az"){
    for(const e of (ONLY?[BYID[ONLY]]:DAZ)){
      if(!e)continue;
      if(!ONLY&&(WITHIN&&!within(e,WITHIN)||!pass(e)))continue;
      n++;out.push(entryRows(e,0,"",false,orig));
    }
  }else{
    const HIT={};
    const hits=nd=>{if(nd.id in HIT)return HIT[nd.id];let h=!!(nd.entry&&pass(nd.entry));for(const c of nd.kids)if(hits(c))h=true;return HIT[nd.id]=h};
    const walk=(nd,d)=>{
      if(!hits(nd))return;
      const self=!!(nd.entry&&pass(nd.entry)),hasK=nd.kids.some(hits),open=hasK&&!SHUT.has(nd.id)&&(active||isOpen(nd,d));   // a unit folded by hand stays folded, also in a search
      const tog=hasK?'<button type="button" class="nm-tog" data-tog="'+esc(nd.id)+'" aria-expanded="'+open+'" title="'+(open?"fold":"unfold")+'">'+(open?"▾":"▸")+'</button>':'<span class="nm-tog0"></span>';
      if(nd.entry)out.push(entryRows(nd.entry,d,tog,!self,orig));
      else out.push('<tr class="nm-node tA"><td colspan="18" style="padding-left:8px">'+tog+'<b>'+esc(nd.en)+'</b> <span class="nm-cnt">'+ndesc(nd)+' places</span></td></tr>');
      if(!open)return;
      let last=-1;const kids=nd.kids.filter(hits),cats=new Set(kids.map(c=>catOf(c.k)));
      for(const c of kids){const ci=catOf(c.k);
        if(cats.size>1&&ci!==last){out.push('<tr class="nm-cat '+(ci<=1?"tA":ci===2?"tB":"tC")+'"><td colspan="18" style="padding-left:30px">'+CATN[ci]+'</td></tr>');last=ci}
        walk(c,d+1)}
    };
    if(WITHIN&&NODE[WITHIN])walk(NODE[WITHIN],0);else ROOTS.forEach(rt=>walk(rt,0));
    n=D.filter(e=>pass(e)&&(!WITHIN||within(e,WITHIN)||e.id===WITHIN)).length;   // every matching place, folded or not
  }
  tb.innerHTML=out.join("")||'<tr><td colspan="18" class="nm-empty">No place matches.</td></tr>';
  if(ONLY&&BYID[ONLY]&&BYID[ONLY].ne){const a=tb.querySelector('a[data-ev]'),tr=tb.querySelector('tr.nm-ev');if(a&&tr){a.textContent=a.textContent.replace("▸","▾");evidence(ONLY,tr)}}
  document.getElementById("nm-n").textContent=n.toLocaleString()+(n===1?" place":" places");
}
tb.addEventListener("click",ev=>{const m=ev.target.closest("button.nm-more");if(!m)return;const td=m.closest("td");const open=td.classList.toggle("nm-open");
  m.textContent=open?"fewer":"+"+m.dataset.n+" more"});
tb.addEventListener("click",ev=>{const b=ev.target.closest("button[data-tog]");if(!b)return;const id=b.dataset.tog;
  if(b.getAttribute("aria-expanded")==="true"){OPEN.delete(id);SHUT.add(id)}else{SHUT.delete(id);OPEN.add(id)}render()});
document.querySelectorAll("[data-view]").forEach(a=>a.addEventListener("click",ev=>{ev.preventDefault();VIEW=a.dataset.view;try{localStorage.setItem("nm-view",VIEW)}catch(_){}render()}));
document.getElementById("nm-exp").addEventListener("click",ev=>{ev.preventDefault();SHUT.clear();Object.values(NODE).forEach(n=>{if(n.kids.length)OPEN.add(n.id)});render()});
document.getElementById("nm-shut").addEventListener("click",ev=>{ev.preventDefault();OPEN.clear();Object.values(NODE).forEach(n=>{if(n.kids.length)SHUT.add(n.id)});render()});
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
  +'<label><a href="#" id="nm-all">show all</a> · <a href="#" id="nm-none">hide all</a> · <a href="#" id="nm-reset">reset order and folding</a></label>';
const PRESETS={all:ALLC.map(x=>x[0]),chars:["tc","sc","jo","jn","ko"],rom:["py","wg","oth","hep","mr","mn","std"],
  zh:["tc","sc","py","wg","oth","std"],jk:["jo","jn","ko","hep","mr"],links:["ll","whg","wp","nb"]};
document.querySelectorAll("a[data-preset]").forEach(a=>a.addEventListener("click",ev=>{ev.preventDefault();const show=PRESETS[a.dataset.preset];
  hidden=ALLC.map(x=>x[0]).filter(c=>!show.includes(c));document.querySelectorAll("#nm-cols input").forEach(i=>i.checked=!hidden.includes(i.dataset.c));applyCols()}));
document.getElementById("nm-colbtn").addEventListener("click",()=>{const p=document.getElementById("nm-cols"),b=document.getElementById("nm-colbtn");
  p.hidden=!p.hidden;b.setAttribute("aria-expanded",String(!p.hidden));b.textContent=p.hidden?"Columns ▾":"Columns ▴"});
document.getElementById("nm-cols").addEventListener("change",ev=>{const c=ev.target.dataset.c;if(!c)return;hidden=ev.target.checked?hidden.filter(x=>x!==c):hidden.concat([c]);applyCols()});
function setAll(show){hidden=show?[]:ALLC.map(x=>x[0]);document.querySelectorAll("#nm-cols input").forEach(i=>i.checked=show);applyCols()}
document.getElementById("nm-all").onclick=ev=>{ev.preventDefault();setAll(true)};document.getElementById("nm-none").onclick=ev=>{ev.preventDefault();setAll(false)};
applyCols();
document.getElementById("nm-reset").addEventListener("click",ev=>{ev.preventDefault();ORDER=DEFAULT_ORDER.slice();FOLD=new Set();saveCols();render()});
const cjb=document.getElementById("nm-cjkfirst");cjb.checked=CJKFIRST;
cjb.addEventListener("change",()=>{CJKFIRST=cjb.checked;try{localStorage.setItem("nm-cjkfirst",CJKFIRST?"1":"0")}catch(_){}render()});
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
(function(){
  const th=document.getElementById("nm-h");let drag=null;
  th.addEventListener("click",ev=>{const cell=ev.target.closest("th[data-col]");if(!cell)return;const c=cell.dataset.col,mv=ev.target.closest("button[data-mv]");
    if(mv){const i=ORDER.indexOf(c),j=i+Number(mv.dataset.mv);if(j<0||j>=ORDER.length)return;ORDER.splice(i,1);ORDER.splice(j,0,c)}
    else{FOLD.has(c)?FOLD.delete(c):FOLD.add(c)}
    saveCols();render()});
  th.addEventListener("dragstart",ev=>{const cell=ev.target.closest("th[data-col]");if(!cell)return;drag=cell.dataset.col;ev.dataTransfer.effectAllowed="move";try{ev.dataTransfer.setData("text/plain",drag)}catch(_){}});
  th.addEventListener("dragover",ev=>{const cell=ev.target.closest("th[data-col]");if(!cell||!drag)return;ev.preventDefault();th.querySelectorAll(".nm-drop").forEach(x=>x.classList.remove("nm-drop"));cell.classList.add("nm-drop")});
  th.addEventListener("dragleave",ev=>{const cell=ev.target.closest("th[data-col]");if(cell)cell.classList.remove("nm-drop")});
  th.addEventListener("drop",ev=>{const cell=ev.target.closest("th[data-col]");if(!cell||!drag)return;ev.preventDefault();const to=cell.dataset.col;
    if(to!==drag){ORDER.splice(ORDER.indexOf(drag),1);ORDER.splice(ORDER.indexOf(to),0,drag);saveCols();render()}drag=null});
  th.addEventListener("dragend",()=>{drag=null;th.querySelectorAll(".nm-drop").forEach(x=>x.classList.remove("nm-drop"))});
})();
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
            .replace("__KEEP__", json.dumps(sorted(k for k in json.load(open(os.path.join(BUILD, "romanisation", "conversions.json"),
                                                                            encoding="utf-8")).get("keep", {})), ensure_ascii=False))
            .replace("__VAR__", json.dumps(variant_map(slim), ensure_ascii=False, separators=(",", ":")))
            .replace("__DATA__", json.dumps(slim, ensure_ascii=False, separators=(",", ":"))))
    open(os.path.join(SITE, "places.html"), "w", encoding="utf-8").write(page)
    os.makedirs(os.path.join(SITE, "data"), exist_ok=True)
    json.dump({"_doc": "Draft place-name glossary of Old Tables of East Asia (places.html). cols: " +
               ", ".join(f"{k} = {l}" for k, l in COLS) + ". Only forms printed in our books or used in our translations.",
               "entries": slim}, open(os.path.join(SITE, "data", "places.json"), "w", encoding="utf-8"),
              ensure_ascii=False, separators=(",", ":"))
    # names per place for other pages (the Population page loads it): [status, note, years, {system: forms}, {system: added}]
    corr = json.load(open(os.path.join(HERE, "corrections.json"), encoding="utf-8")) if os.path.exists(os.path.join(HERE, "corrections.json")) else {}
    pf = {"_doc": "Place names of places.html, per place id: rows [status, note, [first, last year printed], forms printed or "
                  "translated {system: [...]}, forms added {system: [...]}]. alias: ids merged into another place.",
          "sys": dict(COLS), "alias": corr.get("merge", {}),
          "places": {e["id"]: [[r.get("status") or "", r.get("note") or "", r.get("yrs") or None, r["cols"], r.get("added") or {}]
                               for r in e["rows"]] for e in slim}}
    json.dump(pf, open(os.path.join(SITE, "data", "place-forms.json"), "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))
    return {"places": len(E)}


if __name__ == "__main__":
    print(main())
