/* Shared table badges and topic/tag browsing. No dependencies. */
(function(global){
  "use strict";
  const esc=value=>String(value??"").replace(/[&<>"']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
  const fold=value=>String(value??"").normalize("NFKC").toLowerCase();
  const vocabulary=()=>global.TagVocabulary||{topics:{},tags:{},flags:{}};
  function href(kind,id,prefix=""){return `${prefix}topics/${kind==="topics"?"topic":kind==="tags"?"tag":"flag"}-${encodeURIComponent(id)}.html`;}
  function chip(kind,id,prefix="",count){const entry=vocabulary()[kind]?.[id];if(!entry)return "";return `<a class="tag-chip ${kind==="topics"?"topic":kind==="flags"?"flag":""}" href="${href(kind,id,prefix)}" title="${esc(entry.definition)}">${esc(entry.label)}${count===undefined?"":`<small>${count.toLocaleString()}</small>`}</a>`;}
  function render(row,prefix=""){if(!row)return `<div class="table-tags"><a class="tag-pending" href="${prefix}topics/index.html">Tags pending review</a></div>`;const html=["topics","tags","flags"].map(kind=>(row[kind]||[]).map(id=>chip(kind,id,prefix)).join("")).join("");return `<div class="table-tags" aria-label="Table topics and tags">${html||`<a class="tag-pending" href="${prefix}topics/index.html">Tags pending review</a>`}</div>`;}
  function saveGroup(value){try{localStorage.setItem("tag-grouping",value);}catch(e){}}
  function savedGroup(){try{return localStorage.getItem("tag-grouping")==="year"?"year":"book";}catch(e){return "book";}}
  function matches(item,filters,books){const book=books[item.s];return (!filters.collection||book.g===filters.collection)&&(!filters.book||item.s===filters.book)&&(!filters.tag||item.tags.includes(filters.tag))&&(!filters.query||fold([item.t,item.e,item.c,book.title,...item.topics.map(id=>vocabulary().topics[id]?.label),...item.tags.map(id=>vocabulary().tags[id]?.label)].join(" ")).includes(fold(filters.query)));}
  function grouping(items,mode,books){const map=new Map();for(const item of items){const key=mode==="year"?String(books[item.s].y||"Undated"):item.s;if(!map.has(key))map.set(key,[]);map.get(key).push(item);}return [...map.entries()].sort((a,b)=>mode==="year"?a[0].localeCompare(b[0],undefined,{numeric:true}):(books[a[0]].y-books[b[0]].y||books[a[0]].title.localeCompare(books[b[0]].title)));}
  global.TableTags={render,chip,href,esc,fold,matches,grouping};
  if(typeof module!=="undefined")module.exports=global.TableTags;
  if(typeof document==="undefined")return;
  const dataNode=document.getElementById("tag-browser-data");if(!dataNode)return;
  const D=JSON.parse(dataNode.textContent),$=id=>document.getElementById(id),V=Object.fromEntries(D.books.map(b=>[b.s,b]));
  if(D.mode==="index"){
    const search=$("tag-query"),topic=$("topic-filter");
    for(const [id,entry] of Object.entries(vocabulary().topics)){topic.add(new Option(entry.label,id));}
    function drawTags(){const q=fold(search.value.trim()),selected=topic.value;const entries=Object.entries(vocabulary().tags).filter(([id,e])=>(!q||fold(id+" "+e.label+" "+e.definition).includes(q))&&(!selected||(D.tagTopics[id]||[]).includes(selected))).sort((a,b)=>a[1].label.localeCompare(b[1].label));$("tag-count").textContent=`${entries.length} detailed tags`;$("tag-cards").innerHTML=entries.map(([id,e])=>`<a class="tag-card" href="tag-${encodeURIComponent(id)}.html"><strong>${esc(e.label)}</strong> <span class="count">${(D.tagCounts[id]||0).toLocaleString()} tables</span><div class="definition">${esc(e.definition)}</div></a>`).join("")||'<p class="muted">No tags match.</p>';}
    search.oninput=drawTags;topic.onchange=drawTags;drawTags();return;
  }
  let limit=150,pick=null;
  const collection=$("collection"),book=$("book"),tag=$("detail"),query=$("query"),group=$("group");
  const availableCollections=[...new Set(D.items.map(i=>V[i.s].g))];for(const key of availableCollections)collection.add(new Option(D.collections[key],key));
  for(const b of D.books.filter(b=>D.items.some(i=>i.s===b.s)))book.add(new Option(b.title,b.s));
  const tagCounts={};for(const i of D.items)for(const id of i.tags)tagCounts[id]=(tagCounts[id]||0)+1;
  for(const id of Object.keys(tagCounts).sort((a,b)=>vocabulary().tags[a].label.localeCompare(vocabulary().tags[b].label)))tag.add(new Option(`${vocabulary().tags[id].label} (${tagCounts[id]})`,id));
  function readURL(){const p=new URLSearchParams(location.search);collection.value=p.get("collection")||D.region||"";book.value=p.get("book")||"";tag.value=p.get("tag")||"";query.value=p.get("q")||"";group.value=p.get("group")==="year"?"year":p.get("group")==="book"?"book":savedGroup();limit=150;pick=null;}
  function filters(){return {collection:collection.value,book:pick?.book||book.value,tag:pick?.tag||tag.value,query:query.value.trim()};}
  function url(){const p=new URLSearchParams();for(const [key,value] of Object.entries({collection:collection.value,book:book.value,tag:tag.value,q:query.value.trim(),group:group.value}))if(value)p.set(key,value);history.replaceState(null,"",location.pathname+(p.size?"?"+p:""));}
  function result(item){const b=V[item.s];return `<article class="result"><div class="edition"><b>${esc(b.ed)}</b><span class="swatch" style="--series-color:${b.color}"></span>${esc(b.series)}</div><div><a class="title" href="../book/${encodeURIComponent(item.s)}/#${encodeURIComponent(item.id)}">${esc(item.t)}</a>${item.e&&item.e!==item.t?`<div class="translation">${esc(item.e)}</div>`:""}<div class="meta">${esc(b.title)} · ${esc(item.c)}${item.pp?` · p. ${esc(item.pp)}`:""}</div>${render(item,"../")}</div></article>`;}
  function coverage(items){const volumes=D.books.filter(b=>items.some(i=>i.s===b.s)),counts={},dimensions=new Map();for(const item of items){for(const id of item.tags){dimensions.set(id,(dimensions.get(id)||0)+1);const key=item.s+":"+id;counts[key]=(counts[key]||0)+1;}}
    const dims=[...dimensions].sort((a,b)=>b[1]-a[1]);const shown=dims.slice(0,$("all-grid-tags").checked?dims.length:24);
    $("coverage").innerHTML=shown.length?`<table><thead><tr><th>Detailed tag / edition</th>${volumes.map(b=>`<th title="${esc(b.title)}"><span class="swatch" style="--series-color:${b.color}"></span>${esc(b.ed)}</th>`).join("")}</tr></thead><tbody>${shown.map(([id])=>`<tr><th><a href="tag-${id}.html">${esc(vocabulary().tags[id].label)}</a></th>${volumes.map(b=>{const n=counts[b.s+":"+id]||0;return n?`<td><button type="button" data-pick-book="${b.s}" data-pick-tag="${id}" aria-label="${esc(vocabulary().tags[id].label)} in ${esc(b.title)}: ${n} tables" class="${pick?.book===b.s&&pick?.tag===id?"picked":""}" style="background:${b.color};color:#fff">${n}</button></td>`:'<td class="zero">·</td>';}).join("")}</tr>`).join("")}</tbody></table>`:'<p class="muted">No detailed-tag coverage for this selection.</p>';
    $("grid-note").textContent=`${shown.length} of ${dims.length} detailed tags shown. Columns are book editions, coloured by series. Click a number to select that book and tag. Blank cells mean no assigned match.`;
  }
  function draw(){const f=filters(),items=D.items.filter(i=>matches(i,f,V));$("result-count").textContent=`${items.length.toLocaleString()} tables in ${new Set(items.map(i=>i.s)).size} books`;
    let remaining=limit,html="";for(const [key,list] of grouping(items,group.value,V)){if(!remaining)break;const shown=list.slice(0,remaining);remaining-=shown.length;html+=`<section><h3>${esc(group.value==="year"?key:V[key].title)} <span class="count">${list.length.toLocaleString()} tables${group.value==="year"?" · edition year":""}</span></h3>${shown.map(result).join("")}</section>`;}
    $("results").innerHTML=html||'<p class="muted">No tables match these filters.</p>';$("more").hidden=items.length<=limit;$("more").textContent=`Show more (${Math.max(0,items.length-limit).toLocaleString()} remaining)`;$("clear-pick").hidden=!pick;
    const baseFilters={...f,book:book.value,tag:tag.value};const base=D.items.filter(i=>matches(i,baseFilters,V));coverage(base);
    const co={};for(const item of items)for(const id of item.tags)co[id]=(co[id]||0)+1;const pairs=Object.entries(co).sort((a,b)=>b[1]-a[1]);$("related-tags").innerHTML=pairs.slice(0,20).map(([id,n])=>chip("tags",id,"../",n)).join("");$("related-more").hidden=pairs.length<=20;$("related-extra").innerHTML=pairs.slice(20).map(([id,n])=>chip("tags",id,"../",n)).join("");
  }
  for(const control of [collection,book,tag,query,group])control.addEventListener(control===query?"input":"change",()=>{pick=null;limit=150;saveGroup(group.value);url();draw();});
  $("more").onclick=()=>{limit+=150;draw();};$("all-grid-tags").onchange=draw;$("clear-pick").onclick=()=>{pick=null;draw();};
  $("coverage").onclick=event=>{const button=event.target.closest("[data-pick-book]");if(!button)return;pick={book:button.dataset.pickBook,tag:button.dataset.pickTag};limit=150;draw();$("result-count").scrollIntoView({behavior:"smooth",block:"start"});};
  $("reset").onclick=()=>{collection.value=D.region||"";book.value="";tag.value="";query.value="";pick=null;limit=150;url();draw();};
  addEventListener("popstate",()=>{readURL();draw();});readURL();draw();
})(typeof window!=="undefined"?window:globalThis);
