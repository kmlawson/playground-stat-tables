/* charts.js — chart views of transcribed tables (stat-tables-site). No dependencies.
   A chart is another way of reading the printed table above it, never a cleaned copy of it:
   only figures printed in the table are drawn; unreadable cells, blanks, dashes and ditto marks are gaps,
   never filled, interpolated or carried over; labels are the printed labels; years keep their printed order. */
(function () {
  "use strict";
  const NS = "http://www.w3.org/2000/svg";
  const PAL = ["#4e79a7", "#f28e2b", "#e15759", "#59a14f", "#b07aa1", "#edc948", "#76b7b2", "#ff9da7", "#9c755f", "#8c8c8c",
    "#1f77b4", "#d62728", "#2ca02c", "#9467bd", "#bcbd22", "#17becf"];
  const ERA = { "明治": 1867, "大正": 1911, "昭和": 1925, "光武": 1896, "隆熙": 1906, "開國": 1391 };
  const CJK = /[぀-ヿ㐀-鿿豈-﫿]/;

  // ---- reading cells ---------------------------------------------------------------------------------------
  // Returns {k:"num",v} for a printed figure, else {k:"illeg"|"blank"|"dash"|"ditto"|"text"}; s = the printed text.
  function cell(c) {
    const s = String(c == null ? "" : c).trim();
    if (s === "") return { k: "blank", s };
    if (s === "[?]" || s === "?" || /^\[\?\]$/.test(s)) return { k: "illeg", s };
    const n = s.normalize("NFKC").replace(/\s+/g, " ").trim();
    if (/^[-–—―‐−ー…\.・]{1,3}$/.test(n) || n === "...") return { k: "dash", s };
    if (/^(同|〃|仝|″|"|do\.?|ditto)$/i.test(n)) return { k: "ditto", s };
    const m = n.match(/^(△|▲|-|−|\+|減|增|増)?\s*[¥$]?\s*(\d{1,3}(?:[,、]\d{3})+|\d+)?(\.\d+)?\.?\s*(%|[㐀-鿿]{1,2})?$/);
    if (m && (m[2] || m[3])) {
      let v = parseFloat((m[2] || "0").replace(/[,、]/g, "") + (m[3] || ""));
      if (m[1] && /[△▲\-−減]/.test(m[1])) v = -v;
      return { k: "num", v, s };
    }
    return { k: "text", s };
  }
  const seg = h => String(h || "").split(/\s+—\s+/);
  const TOT = /^(合計|總計|総計|計|總數|総数|總額|総額|累計|共計|合|小計|全鮮計|道計|府計|郡計|總|総|計數|total|totals|grand total|sum)$/i;
  function isTotal(label) {
    const s = String(label || "").replace(/[\s　]/g, "").normalize("NFKC");
    if (!s) return false;
    if (TOT.test(s)) return true;
    // English: "Total", "Totals", "Grand total", "Total (Yen)" — not "Total — women" or "Percentage of total"
    const e = String(label).replace(/[(（][^)）]*[)）]/g, "").replace(/[:.\s]+$/, "").trim();
    if (/^(grand\s+)?totals?$/i.test(e)) return true;
    return s.length <= 6 && /計$/.test(s) && !/(統|設|會|会|集|生|時|主)計$/.test(s);
  }
  // A printed year label -> a calendar year (for spacing only; the printed label is always what is shown).
  const KD = { "〇": 0, "一": 1, "二": 2, "三": 3, "四": 4, "五": 5, "六": 6, "七": 7, "八": 8, "九": 9 };
  function num(t) {   // "元", "14", "十四", "二十", "四" -> number
    if (t === "元") return 1;
    if (/^\d+$/.test(t)) return +t;
    let n = 0, cur = 0;
    for (const ch of t) { if (ch in KD) cur = KD[ch]; else if (ch === "十") { n += (cur || 1) * 10; cur = 0; } else return null; }
    return n + cur;
  }
  const YN = "(元|\\d{1,2}|[〇一二三四五六七八九十]{1,3})";
  const RE_ERA = new RegExp("(明治|大正|昭和|光武|隆熙)\\s*" + YN), RE_DIT = new RegExp("^\\s*(?:同|仝|〃)\\s*" + YN + "(?![\\d〇一二三四五六七八九十])"), RE_BARE = new RegExp("^\\s*" + YN + "\\s*年");
  function yearOf(label, ctx) {
    const s = String(label || "").normalize("NFKC");
    let m = s.match(RE_ERA);
    if (m && num(m[2]) != null) { ctx.era = m[1]; return ERA[m[1]] + num(m[2]); }
    m = s.match(/(?:^|[^\d])(1[89]\d\d)(?!\d)/);
    if (m) return +m[1];
    m = s.match(RE_DIT) || s.match(RE_BARE);
    if (m && ctx.era && num(m[1]) != null) return ERA[ctx.era] + num(m[1]);
    return null;
  }
  // Split a printed label into its year phrase and the rest ("昭和7年 內地人" -> 1932, "昭和7年", "內地人").
  const SUF = "(?:\\s*(?:年度末|年度|年末|年))?";
  const RX_ERA = new RegExp("(明治|大正|昭和|光武|隆熙)\\s*" + YN + SUF), RX_W = /(?:^|[^\d])((1[89]\d\d)(?:\s*[-–]\s*(?:\d{4}|\d{2}))?(?:\s*(?:年度末|年度|年末|年))?)(?!\d)/,
    RX_D = new RegExp("^\\s*((?:同|仝|〃)\\s*" + YN + SUF + ")(?![\\d〇一二三四五六七八九十])"), RX_B = new RegExp("^\\s*(" + YN + "\\s*(?:年度末|年度|年末|年))");
  function splitYear(label, ctx) {
    const s0 = String(label || "").normalize("NFKC"), s = s0.replace(/[(（][^()（）]*[)）]/g, x => " ".repeat(x.length));
    let y = null, t = "", m = s.match(RX_ERA);
    if (m && num(m[2]) != null) { ctx.era = m[1]; y = ERA[m[1]] + num(m[2]); t = m[0]; }
    else if ((m = s.match(RX_W))) { y = +m[2]; t = m[1]; }
    else if ((m = s.match(RX_D) || s.match(RX_B)) && ctx.era && num(m[2]) != null) { y = ERA[ctx.era] + num(m[2]); t = m[1]; }
    const rest = y == null ? s0 : s0.replace(t, "\u0000").split(/\s*(?:—|·)\s*/).map(x => x.replace("\u0000", "").trim()).filter(Boolean).join(" · ");
    return { y, t: t.trim(), rest };
  }
  // A list of printed labels read as a time axis: distinct years in printed order, and the rest of each label.
  function timeAxis(labels) {
    const ctx = {}, sp = labels.map(l => splitYear(l, ctx));
    const hit = sp.filter(x => x.y != null).length;
    if (hit < Math.max(3, Math.ceil(labels.length * 0.6))) return null;
    const keys = [];
    sp.forEach((x, i) => { if (x.y != null && !keys.some(k => k.y === x.y)) keys.push({ y: x.y, label: labels[i], t: x.t }); });
    if (keys.length < 3) return null;
    const rests = [...new Set(sp.filter(x => x.y != null).map(x => x.rest))];
    const dup = keys.length < hit;
    if (dup) keys.forEach(k => (k.label = k.t));       // the axis shows the year phrase; the rest goes to the series
    let prop = keys.every((k, i) => i === 0 || k.y > keys[i - 1].y), rev = false;
    if (!prop && keys.every((k, i) => i === 0 || k.y < keys[i - 1].y)) { keys.reverse(); prop = rev = true; }   // printed newest first
    return { sp, keys, rests, dup, prop, rev, undated: labels.filter((_, i) => sp[i].y == null) };
  }
  // ---- table -> chart model ----------------------------------------------------------------------------------
  function model(part) {
    const cols = part.columns || [], rows = (part.rows || []).map(r => cols.map((_, j) => cell(r[j])));
    if (!rows.length || cols.length < 2) return null;
    const yearCol = j => {   // a column of printed years (1908, 1909 …) labels the rows; it is not a quantity
      const hd = String(cols[j] || "").normalize("NFKC").trim();
      const yearish = rows.every(r => r[j].k !== "num" || (/^\d{4}$/.test(r[j].s.trim()) && r[j].v >= 1850 && r[j].v <= 1960));
      return yearish && (/^(years?|fiscal years?|年|年次|年度|年別|年末)$/i.test(hd) || hd === "" || j === 0);
    };
    const numCol = cols.map((_, j) => {
      let n = 0, t = 0;
      rows.forEach(r => { const c = r[j]; if (c.k === "num") n++; else if (c.k === "text") t++; });
      if (j === 0 && t > 0) return false;                  // the first column is a label unless it holds only figures
      return n >= 1 && n >= t && !yearCol(j);
    });
    if (!numCol.some(Boolean)) return null;
    // label columns: those with printed words; all-dash or empty columns label nothing
    const labJ = cols.map((_, j) => j).filter(j => !numCol[j] && rows.some(r => r[j].k === "text" || r[j].k === "num"));
    const prev = {};
    const lab = r => labJ.map(j => {
      let c = r[j];
      if ((c.k === "blank" || c.k === "ditto") && prev[j]) c = prev[j];    // printed blank / 〃 under a label = the label above
      else if (c.k !== "blank") prev[j] = c;
      return c.s;
    }).filter(x => x && !/^[-–—]+$/.test(x)).join(" · ");
    const R = [];
    let group = "";
    rows.forEach((r, i) => {
      const data = r.filter((_, j) => numCol[j]);
      const empty = data.every(c => c.k === "blank");
      const label = lab(r);
      if (empty && label) { group = label.replace(/[:：]\s*$/, ""); return; }        // section heading row
      if (!label && empty) return;
      R.push({ i, label: label || `(row ${i + 1})`, group, total: labJ.some(j => isTotal(r[j].s)) || isTotal(label), cells: r });
    });
    const C = [];
    cols.forEach((h, j) => { if (numCol[j]) { const sg = seg(h); C.push({ j, label: h, last: sg[sg.length - 1], pre: sg.slice(0, -1).join(" — "), total: isTotal(sg[sg.length - 1]) }); } });
    if (!R.length || !C.length) return null;
    const nums = R.reduce((a, r) => a + C.filter(c => r.cells[c.j].k === "num").length, 0);
    if (nums < 2) return null;
    return { R, C, cols, labHead: labJ.length ? cols[labJ[0]] : "" };
  }

  // ---- table -> one or more views ----------------------------------------------------------------------------
  // A view is one chart: kind ("line"|"bar"), x (years) or cats (rows), series. A table becomes several views when it
  // prints several measures (column groups, units, ratios) or a block of earlier-year rows under its main rows; each
  // measure gets its own axis. Undated rows of a time series are listed, not drawn.
  const NONE = { k: "none", s: "" };
  // Which chart each column belongs to. Two-level headings either name different measures (Revenue — …, Expenditure — …:
  // one chart each) or the same measures for different categories (Koreans — Male/Female/Total, Japanese — …). In the
  // second case the categories share one chart if the sub-columns add up to their printed total (one unit), else there
  // is one chart per sub-column (Schools / Students). Ratios, averages and differences always get their own chart.
  function viewKeys(m) {
    const K = {}, sg = c => seg(c.label), leafOf = c => sg(c)[1];
    const multi = m.C.filter(c => sg(c).length >= 2 && !RATIO.test(c.label));
    const tops = [...new Set(multi.map(c => sg(c)[0]))], lt = {};
    multi.forEach(c => (lt[leafOf(c)] = lt[leafOf(c)] || new Set()).add(sg(c)[0]));
    const leaves = Object.keys(lt);
    const repeated = tops.length >= 2 && leaves.length >= 2 && leaves.filter(l => lt[l].size >= 2).length >= leaves.length * 0.6;
    let mode = repeated ? "leaf" : "top";
    if (repeated) for (const t of tops) {
      const cs = multi.filter(c => sg(c)[0] === t && sg(c).length === 2), tot = cs.filter(c => isTotal(c.last)), parts = cs.filter(c => !isTotal(c.last));
      if (tot.length === 1 && parts.length >= 2) {
        let ok = 0, n = 0;
        m.R.forEach(r => { const tv = r.cells[tot[0].j]; if (tv.k !== "num" || !parts.every(c => r.cells[c.j].k === "num")) return; n++;
          if (Math.abs(parts.reduce((a, c) => a + r.cells[c.j].v, 0) - tv.v) <= Math.max(1, Math.abs(tv.v) * 0.005)) ok++; });
        if (n && ok >= n * 0.5) { mode = "one"; break; }
      }
    }
    m.C.forEach(c => {
      if (RATIO.test(c.label)) K[c.j] = "~" + (repeated && sg(c).length >= 2 ? leafOf(c) : c.label);
      else if (sg(c).length < 2) K[c.j] = "";
      else K[c.j] = mode === "top" ? sg(c)[0] : mode === "leaf" ? leafOf(c) : "";
    });
    return K;
  }
  function byView(series, names) {
    const keys = [];
    series.forEach(s => { if (!keys.includes(s.view)) keys.push(s.view); });
    return keys.map(k => ({ key: k, name: names(k, series.filter(s => s.view === k)), series: series.filter(s => s.view === k) }));
  }
  const listName = ss => { const n = [...new Set(ss.map(s => s.short || s.label))]; const t = n.slice(0, 4).join(", ") + (n.length > 4 ? "…" : ""); return t; };
  const vname = (k, ss) => k.startsWith("~") ? k.slice(1) : (k || listName(ss));
  // few years and several categories: grouped bars (categories) × (years) read better than 2–3-point lines
  function transpose(v) {
    return Object.assign({}, v, { kind: "bar", transposed: true,
      cats: v.series.map(s => ({ label: s.short || s.label, group: s.pre || "", total: s.total, i: (s.rows || [])[0] })),
      series: v.x.map((x, xi) => ({ label: x.label, short: x.label, pre: "", total: false, pts: v.series.map(s => s.pts[xi]) })) });
  }
  function views(m) {
    const out = [], K = viewKeys(m), gkey = c => K[c.j];
    const tr = timeAxis(m.R.map(r => r.label));
    if (tr) {
      const series = [];
      (tr.dup ? tr.rests : [null]).forEach(rest => m.C.forEach(c => {
        const pick = tr.keys.map(k => m.R.findIndex((r, i) => tr.sp[i].y === k.y && (rest === null || tr.sp[i].rest === rest)));
        const many = m.C.filter(x => gkey(x) === gkey(c)).length > 1;
        series.push({ view: gkey(c), label: (rest ? rest + " — " : "") + c.label, short: rest ? rest + (many ? " — " + c.last : "") : c.last, pre: rest && many ? c.last : (rest ? "" : c.pre),
          total: c.total || (rest != null && isTotal(rest)), pts: pick.map(i => i < 0 ? NONE : m.R[i].cells[c.j]), rows: pick.map(i => i < 0 ? null : m.R[i].i) });
      }));
      byView(series, vname).forEach(v => out.push(Object.assign({ kind: "line", x: tr.keys, prop: tr.prop, rev: tr.rev, undated: tr.undated }, v)));
    } else {
      const tc = timeAxis(m.C.map(c => c.label));
      if (tc) {
        const series = [];
        (tc.dup ? tc.rests : [null]).forEach(rest => m.R.forEach(r => {
          const pick = tc.keys.map(k => m.C.findIndex((c, i) => tc.sp[i].y === k.y && (rest === null || tc.sp[i].rest === rest)));
          series.push({ view: rest || "", label: (r.group ? r.group + " — " : "") + r.label + (rest ? " — " + rest : ""), short: r.label, pre: r.group, total: r.total,
            pts: pick.map(i => i < 0 ? NONE : r.cells[m.C[i].j]), rows: pick.map(() => r.i) });
        }));
        byView(series, k => k || "").forEach(v => out.push(Object.assign({ kind: "line", x: tc.keys, prop: tc.prop, rev: tc.rev, byRow: true, undated: tc.undated }, v, { name: v.name || listName(v.series) })));
      }
    }
    if (out.length) return out.map(v => v.x.length <= 3 && v.series.length >= 2 ? transpose(v) : v);
    // bars. One printed row with two-level headings ("Officials — Killed", "Officials — Wounded" …): the first level
    // gives the categories, the second the series.
    if (m.R.length === 1 && m.C.every(c => seg(c.label).length === 2 && !RATIO.test(c.label))) {
      const r = m.R[0], tops = [...new Set(m.C.map(c => seg(c.label)[0]))], leaves = [...new Set(m.C.map(c => c.last))];
      if (tops.length >= 2 && leaves.length >= 2 && leaves.length < m.C.length)
        return [{ kind: "bar", name: "", cats: tops.map(t => ({ label: t, group: "", total: isTotal(t), i: r.i })),
          series: leaves.map(l => ({ label: l, short: l, pre: "", total: isTotal(l), pts: tops.map(t => { const c = m.C.find(c => seg(c.label)[0] === t && c.last === l); return c ? r.cells[c.j] : NONE; }) })) }];
    }
    // Rows that are only two or three printed years (1911, 1910): the columns are the categories, the years the series.
    const ctx0 = {};
    if (m.R.length <= 3 && m.R.length >= 2 && m.R.every(r => { const x = splitYear(r.label, ctx0); return x.y != null && !x.rest; })) {
      const groups = [];
      m.C.forEach(c => { const k = gkey(c); let g = groups.find(x => x.key === k); if (!g) groups.push(g = { key: k, cs: [] }); g.cs.push(c); });
      return groups.map(g => ({ kind: "bar", transposed: true, name: groups.length > 1 ? (g.key.startsWith("~") ? g.key.slice(1) : g.key || listName(g.cs.map(c => ({ short: c.last })))) : "",
        cats: g.cs.map(c => ({ label: g.key && !g.key.startsWith("~") ? seg(c.label).slice(seg(g.key).length).join(" — ") || c.last : c.label, group: "", total: c.total, i: m.R[0].i })),
        series: m.R.map(r => ({ label: r.label, short: r.label, pre: "", total: false, pts: g.cs.map(c => r.cells[c.j]) })) }));
    }
    // One printed row: its columns are the categories, one chart per measure.
    if (m.R.length === 1) {
      const r = m.R[0], groups = [];
      m.C.forEach(c => { const k = gkey(c); let g = groups.find(x => x.key === k); if (!g) groups.push(g = { key: k, cs: [] }); g.cs.push(c); });
      return groups.map(g => ({ kind: "bar", name: g.key.startsWith("~") ? g.key.slice(1) : (g.key || listName(g.cs.map(c => ({ short: c.last })))),
        cats: g.cs.map(c => ({ label: g.key && !g.key.startsWith("~") ? c.last : c.label, group: "", total: c.total, i: r.i })),
        series: [{ label: r.label, short: r.label, pre: "", total: r.total, pts: g.cs.map(c => r.cells[c.j]) }] }));
    }
    // rows: the printed rows, and a trailing block of earlier-year rows (with the total above it) as its own chart
    const ctx = {}, yr = m.R.map(r => { const x = splitYear(r.label, ctx); return x.y != null && !x.rest; });
    let b0 = yr.indexOf(true);
    const rowSets = [];
    if (b0 >= 2 && yr.slice(b0).every((y, k) => y || m.R[b0 + k].total) && yr.slice(0, b0).filter(y => !y).length >= 2) {
      const tot = b0 > 0 && m.R[b0 - 1].total ? [m.R[b0 - 1]] : [];
      rowSets.push({ name: "", rows: m.R.slice(0, b0) });
      rowSets.push({ name: tot.length ? "Total and earlier years" : "Earlier years", rows: tot.concat(m.R.slice(b0)), keepTotals: true });
    } else rowSets.push({ name: "", rows: m.R });
    const cs = m.C.map(c => ({ view: gkey(c), c }));
    const colSets = byView(cs.map(x => Object.assign(x, { short: x.c.last, label: x.c.label })), vname);
    rowSets.forEach(rs => colSets.forEach(cg => out.push({ kind: "bar", keepTotals: rs.keepTotals,
      name: [rs.name, colSets.length > 1 || rs.name ? cg.name : ""].filter(Boolean).join(" · ") || (rowSets.length > 1 ? m.labHead || "Rows" : ""),
      cats: rs.rows.map(r => ({ label: r.label, group: r.group, total: r.total, i: r.i })),
      series: cg.series.map(x => ({ label: x.c.label, short: x.c.last, pre: x.c.pre, total: x.c.total, pts: rs.rows.map(r => r.cells[x.c.j]) })) })));
    return out;
  }
  const plan = m => views(m)[0];
  // series names that repeat within a chart (Male, Female under several nationalities) carry their group
  function uniq(v) {
    const seen = {};
    v.series.forEach(s => { const k = s.short || s.label; seen[k] = (seen[k] || 0) + 1; });
    v.series.forEach(s => { if (seen[s.short || s.label] > 1) s.short = s.pre ? s.pre + " — " + (s.short || s.label) : s.label; });
    return v;
  }

  // Ratios, averages and densities are never stacked.
  const RATIO = /density|\bper\b|per cent|percent|%|average|mean|ratio|\brate\b|index|increase|decrease|period of|比|率|平均|每|當り|当り|指數|百分|千分|割合|密度|增減|増減/i;
  // Stack only where the printed parts add up to the printed total in most rows that can be checked — the rows
  // where they do not are then marked ≠, which is a printed discrepancy rather than a wrong choice of columns.
  function addsUp(S, parts, tot) {
    let ok = 0, n = 0;
    S[tot].pts.forEach((t, i) => {
      if (t.k !== "num" || !parts.every(k => S[k].pts[i].k === "num")) return;
      n++; const a = parts.reduce((x, k) => x + S[k].pts[i].v, 0);
      if (Math.abs(a - t.v) <= Math.max(1, Math.abs(t.v) * 0.005)) ok++;
    });
    return n > 0 && ok >= Math.max(1, n * 0.5);
  }
  // Default series shown, and whether a stacked view makes sense (parts printed beside their own total).
  function defaults(p) {
    const S = p.series, n = S.length;
    p.stackable = null;
    if (p.kind === "bar") {
      const byPre = {};
      S.forEach((s, k) => (byPre[s.pre] = byPre[s.pre] || []).push(k));
      for (const pre in byPre) {
        const ks = byPre[pre], tot = ks.filter(k => S[k].total), parts = ks.filter(k => !S[k].total);
        const sub = parts.filter(k => !RATIO.test(S[k].label) && S[k].pts.every(c => c.k !== "num" || c.v >= 0));
        if (tot.length === 1 && sub.length >= 2 && addsUp(S, sub, tot[0])) { p.stackable = { total: tot[0], parts: sub }; break; }
      }
      if (p.stackable) return { on: new Set(p.stackable.parts), mode: "stack" };
      if (n <= 3) return { on: new Set(S.map((_, k) => k)), mode: "group" };
      const t = S.findIndex(s => s.total);
      return { on: new Set([t >= 0 ? t : 0]), mode: "group" };
    }
    let on = S.map((_, k) => k);
    if (n > 6) {
      // printed totals, unless they are a flat base (e.g. 100.00 in a percentage table)
      const flat = k => { const v = S[k].pts.filter(c => c.k === "num").map(c => c.v); return v.length > 1 && v.every(x => x === v[0]); };
      const t = on.filter(k => S[k].total && !flat(k)), rest = on.filter(k => !S[k].total && !flat(k));
      on = t.length && t.length <= 6 ? t : (rest.length ? rest : on).slice(0, 5);
    }
    return { on: new Set(on), mode: "auto" };
  }

  // ---- drawing helpers --------------------------------------------------------------------------------------
  function el(name, attrs, parent) {
    const e = document.createElementNS(NS, name);
    for (const a in attrs) if (attrs[a] != null) e.setAttribute(a, attrs[a]);
    if (parent) parent.appendChild(e);
    return e;
  }
  function txt(parent, x, y, s, attrs) { const t = el("text", Object.assign({ x, y }, attrs || {}), parent); t.textContent = s; return t; }
  function ticks(lo, hi, want) {
    if (lo === hi) { hi = lo === 0 ? 1 : lo * 1.1; if (lo > 0) lo = 0; }
    const raw = (hi - lo) / Math.max(2, want), mag = Math.pow(10, Math.floor(Math.log10(raw))), f = raw / mag;
    const step = (f < 1.5 ? 1 : f < 3 ? 2 : f < 7 ? 5 : 10) * mag;
    const a = Math.floor(lo / step) * step, b = Math.ceil(hi / step) * step, out = [];
    for (let v = a; v <= b + step / 2; v += step) out.push(+v.toFixed(10));
    return out;
  }
  function fmt(v) {
    const a = Math.abs(v);
    if (a >= 1e9) return +(v / 1e9).toFixed(a >= 1e10 ? 0 : 1) + "B";
    if (a >= 1e6) return +(v / 1e6).toFixed(a >= 1e7 ? 0 : 1) + "M";
    if (a >= 1e4) return +(v / 1e3).toFixed(0) + "k";
    if (a >= 1e3) return +(v / 1e3).toFixed(1) + "k";
    return String(+v.toFixed(2));
  }
  const textW = (s, px) => [...String(s)].reduce((w, ch) => w + (CJK.test(ch) ? px : ch.charCodeAt(0) > 255 ? px * 0.9 : px * 0.58), 0);
  function clip(s, px, maxW) {
    s = String(s);
    if (textW(s, px) <= maxW) return s;
    let o = "";
    for (const ch of s) { if (textW(o + ch + "…", px) > maxW) break; o += ch; }
    return o + "…";
  }
  const state = c => ({ illeg: "unreadable in the scan", blank: "blank in the original", dash: "printed “" , ditto: "printed ditto mark “", text: "printed “" }[c.k]);
  let MARKED = true;
  function shown(c) {
    if (c.k === "num") return c.s;
    if (c.k === "blank" && !MARKED) return "— empty in the transcription (blank in the original, or unreadable)";
    if (c.k === "none") return "— not in this table";
    if (c.k === "illeg" || c.k === "blank") return "— " + state(c);
    return "not plotted — " + state(c) + c.s + "”";
  }

  // ---- the widget -------------------------------------------------------------------------------------------
  function mount(host, table, pi, opt) {
    MARKED = !(opt && opt.marked === false);
    const part = (table.parts || [])[pi];
    const m = part && model(part);
    if (!m) { host.classList.add("tc-none"); host.innerHTML = '<p class="tc-msg">No chart for this table: it has too few printed figures to draw.</p>'; return false; }
    const V = views(m).map(uniq);
    let p, S, st;
    host.innerHTML = "";
    const tabs = document.createElement("div"); tabs.className = "tc-tabs"; host.appendChild(tabs);
    const bar = document.createElement("div"); bar.className = "tc-bar"; host.appendChild(bar);
    const leg = document.createElement("div"); leg.className = "tc-leg"; host.appendChild(leg);
    const plot = document.createElement("div"); plot.className = "tc-plot"; host.appendChild(plot);
    const tip = document.createElement("div"); tip.className = "tc-tip"; tip.hidden = true; host.appendChild(tip);
    const note = document.createElement("p"); note.className = "tc-note"; host.appendChild(note);
    const color = k => PAL[k % PAL.length];

    function noteText() {
      let nI = 0, nB = 0, nD = 0;
      S.forEach(s => s.pts.forEach(c => { if (c.k === "illeg") nI++; else if (c.k === "blank") nB++; else if (c.k !== "num" && c.k !== "none") nD++; }));
      const bits = [];
      if (nI) bits.push(`${nI} unreadable cell${nI > 1 ? "s" : ""} (marked ?)`);
      if (nB) bits.push(MARKED ? `${nB} blank${nB > 1 ? "s" : ""}` : `${nB} empty cell${nB > 1 ? "s" : ""} (blank in the original or unreadable — this book does not distinguish them)`);
      if (nD) bits.push(`${nD} printed dash${nD > 1 ? "es" : ""}, ditto marks or text`);
      const axis = p.kind === "line" ? (p.prop ? " Years are spaced by date" + (p.rev ? " (the table prints them newest first)." : ".") + " A dashed line joins years with unprinted years between them." : " Years are evenly spaced in printed order, not by date.") + (p.undated && p.undated.length ? ` Not dated, so not drawn: ${p.undated.slice(0, 4).join(", ")}${p.undated.length > 4 ? "…" : ""}.` : "") : "";
      note.textContent = (V.length > 1 ? `The table prints ${V.length} kinds of figures; each has its own chart (buttons above). ` : "") + "Drawn only from the figures printed in the table." + (bits.length ? " Not drawn: " + bits.join(", ") + "; nothing is filled in or interpolated." : "") + axis;
    }
    function setView(i) {
      p = V[i]; S = p.series; const d = defaults(p);
      st = { on: d.on, mode: d.mode, sort: "printed", totals: !!p.keepTotals, sep: null, view: i };
      tabs.innerHTML = "";
      if (V.length > 1) V.forEach((v, k) => {
        const b = document.createElement("button"); b.type = "button"; b.textContent = clip(v.name || `Chart ${k + 1}`, 13, 260); b.title = v.name;
        if (k === i) b.classList.add("on"); b.onclick = () => setView(k); tabs.appendChild(b);
      });
      noteText(); controls(); legend(); draw();
    }
    function btn(label, on, fn, title) {
      const b = document.createElement("button"); b.type = "button"; b.textContent = label; if (title) b.title = title;
      if (on) b.classList.add("on"); b.addEventListener("click", fn); bar.appendChild(b); return b;
    }
    function controls() {
      bar.innerHTML = "";
      if (p.kind === "bar") {
        if (p.stackable) {
          btn("Stacked", st.mode === "stack", () => { st.mode = "stack"; st.on = new Set(p.stackable.parts); legend(); controls(); draw(); }, "Parts stacked, with the printed total marked");
          btn("Side by side", st.mode === "group", () => { st.mode = "group"; controls(); draw(); });
        }
        const sel = document.createElement("select"); sel.setAttribute("aria-label", "Order of bars");
        [["printed", "Printed order"], ["desc", "Largest first"], ["asc", "Smallest first"]].forEach(([v, l]) => { const o = document.createElement("option"); o.value = v; o.textContent = l; if (st.sort === v) o.selected = true; sel.appendChild(o); });
        sel.addEventListener("change", () => { st.sort = sel.value; draw(); });
        bar.appendChild(sel);
        const nt = p.cats.filter(c => c.total).length;
        if (nt) btn(st.totals ? `Hide total rows (${nt})` : `Show total rows (${nt})`, st.totals, () => { st.totals = !st.totals; controls(); draw(); }, "Rows printed as totals are hidden by default so that they do not dwarf the others");
      } else if (S.length > 1) {
        btn("One chart", st.sep === false, () => { st.sep = false; controls(); draw(); });
        btn("Separate charts", st.sep === true, () => { st.sep = true; controls(); draw(); }, "One small chart per series, each with its own scale");
      }
    }
    function legend() {
      leg.innerHTML = "";
      if (S.length > 8) {
        const a = document.createElement("button"); a.type = "button"; a.className = "tc-all"; a.textContent = "All";
        a.onclick = () => { st.on = new Set(S.map((_, k) => k)); if (st.mode === "stack") st.mode = "group"; legend(); controls(); draw(); };
        const z = document.createElement("button"); z.type = "button"; z.className = "tc-all"; z.textContent = "None";
        z.onclick = () => { st.on = new Set(); legend(); draw(); };
        leg.append(a, z);
      }
      let pre = null;
      S.forEach((s, k) => {
        if (s.pre && s.pre !== pre && S.some(x => x.pre !== s.pre)) { const g = document.createElement("span"); g.className = "tc-grp"; g.textContent = s.pre; leg.appendChild(g); }
        pre = s.pre;
        const b = document.createElement("button"); b.type = "button"; b.className = "tc-chip" + (st.on.has(k) ? " on" : "");
        b.setAttribute("aria-pressed", st.on.has(k)); b.title = s.label;
        b.innerHTML = `<i style="background:${color(k)}"></i>`; b.appendChild(document.createTextNode(s.short || s.label));
        b.onclick = () => {
          if (st.on.has(k)) st.on.delete(k); else st.on.add(k);
          if (st.mode === "stack" && p.stackable && ![...st.on].every(x => p.stackable.parts.includes(x))) st.mode = "group";
          legend(); controls(); draw();
        };
        leg.appendChild(b);
      });
    }
    function showTip(evt, html) {
      tip.innerHTML = html; tip.hidden = false;
      const hb = host.getBoundingClientRect(), x = evt.clientX - hb.left, y = evt.clientY - hb.top;
      const w = tip.offsetWidth;
      tip.style.left = Math.max(4, Math.min(x + 12, hb.width - w - 4)) + "px";
      tip.style.top = (y + 14) + "px";
    }
    host.addEventListener("pointerleave", ev => { if (ev.pointerType === "mouse") tip.hidden = true; });
    document.addEventListener("pointerdown", ev => { if (!host.contains(ev.target)) tip.hidden = true; });
    const esc = s => String(s).replace(/[&<>"]/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));

    // highlight the matching printed row in the table, when the table is on screen too
    function flash(i) {
      const sec = host.closest(".tbl"); if (!sec || i == null) return;
      const tr = sec.querySelector(`.tw[data-p="${host.dataset.p}"] tr[data-i="${i}"]`); if (!tr) return;
      sec.querySelectorAll("tr.tc-hl").forEach(x => x.classList.remove("tc-hl")); tr.classList.add("tc-hl");
    }

    function draw() {
      tip.hidden = true; plot.innerHTML = "";
      const W = Math.max(260, plot.clientWidth || host.clientWidth || 600), narrow = W < 520;
      const on = [...st.on].sort((a, b) => a - b);
      if (!on.length) { plot.innerHTML = '<p class="tc-msg">Choose one or more series above.</p>'; return; }
      if (p.kind === "line") {
        if (st.sep === null) {   // series of very different size: separate charts by default
          const mx = on.map(k => Math.max(...S[k].pts.filter(c => c.k === "num").map(c => Math.abs(c.v)), 0)).filter(v => v > 0);
          st.sep = mx.length > 1 && Math.max(...mx) / Math.min(...mx) > 50; controls();
        }
        if (st.sep && on.length > 1) {
          const grid = document.createElement("div"); grid.className = "tc-multi"; plot.appendChild(grid);
          const cw = narrow ? W : Math.floor((W - 12) / 2);
          on.forEach(k => { const box = document.createElement("div"); box.className = "tc-mini"; grid.appendChild(box);
            const h = document.createElement("div"); h.className = "tc-mt"; h.innerHTML = `<i style="background:${color(k)}"></i>` + esc(S[k].label); box.appendChild(h);
            lineChart(box, [k], cw, 170); });
        } else lineChart(plot, on, W, narrow ? 230 : 280);
      } else barChart(plot, on, W, narrow);
    }

    function lineChart(box, on, W, H) {
      const vals = on.flatMap(k => S[k].pts.filter(c => c.k === "num").map(c => c.v));
      if (!vals.length) { const q = document.createElement("p"); q.className = "tc-msg"; q.textContent = "No printed figures in this series."; box.appendChild(q); return; }
      const T = ticks(Math.min(0, ...vals), Math.max(0, ...vals), H > 200 ? 5 : 3), lo = T[0], hi = T[T.length - 1];
      const L = Math.max(...T.map(t => textW(fmt(t), 11))) + 10, R = 10, top = 10, B = 44;
      const svg = el("svg", { viewBox: `0 0 ${W} ${H}`, width: "100%", class: "tc-svg", role: "img" }, box);
      const n = p.x.length, pw = W - L - R, ph = H - top - B;
      const ys = p.x.map(x => x.y);
      const X = p.prop ? (i => L + (n === 1 ? pw / 2 : (ys[i] - ys[0]) / (ys[n - 1] - ys[0]) * pw)) : (i => L + (n === 1 ? pw / 2 : i / (n - 1) * pw));
      const Y = v => top + (hi - v) / (hi - lo) * ph;
      // printed years further apart than the usual step: the years between are not printed, so the join is dashed
      const steps = ys.slice(1).map((y, i) => y - ys[i]).filter(x => x > 0).sort((a, b) => a - b), med = steps.length ? steps[steps.length >> 1] : 1;
      const gapped = (a, b) => p.prop && ys[b] - ys[a] > Math.max(1, med) * 1.5;
      T.forEach(t => { el("line", { x1: L, x2: W - R, y1: Y(t), y2: Y(t), class: t === 0 ? "tc-zero" : "tc-grid" }, svg); txt(svg, L - 6, Y(t) + 4, fmt(t), { class: "tc-ax", "text-anchor": "end" }); });
      // x labels: as many as fit, always the first and last
      const lw = Math.max(...p.x.map(x => textW(x.label, 10.5))) + 8, every = Math.max(1, Math.ceil(n * Math.min(lw, 90) / pw));
      p.x.forEach((x, i) => {
        if (i % every && i !== n - 1) return;
        if (i === n - 1 && i % every && n - 1 - Math.floor((n - 1) / every) * every < every / 2) return;
        txt(svg, X(i), H - B + 16, clip(x.label, 10.5, Math.max(40, every * pw / Math.max(1, n - 1) - 4)), { class: "tc-ax", "text-anchor": i === 0 && n > 1 ? "start" : i === n - 1 && n > 1 ? "end" : "middle" });
      });
      on.forEach(k => {
        const s = S[k], col = color(k);
        let d = "", dd = "", last = -1;
        s.pts.forEach((c, i) => {
          if (c.k !== "num") { last = -1; return; }
          const pt = X(i).toFixed(1) + " " + Y(c.v).toFixed(1);
          if (last >= 0 && gapped(last, i)) { dd += "M" + X(last).toFixed(1) + " " + Y(s.pts[last].v).toFixed(1) + "L" + pt; d += "M" + pt; }
          else d += (last >= 0 ? "L" : "M") + pt;
          last = i;
        });
        if (d) el("path", { d, fill: "none", stroke: col, "stroke-width": 2, "stroke-linejoin": "round" }, svg);
        if (dd) el("path", { d: dd, fill: "none", stroke: col, "stroke-width": 1.5, "stroke-dasharray": "4 4" }, svg);
        s.pts.forEach((c, i) => {
          if (c.k === "num") {
            const lonely = (i === 0 || s.pts[i - 1].k !== "num") && (i === n - 1 || s.pts[i + 1].k !== "num");
            if (n <= 40 || lonely) el("circle", { cx: X(i), cy: Y(c.v), r: lonely ? 3.5 : 2.6, fill: col }, svg);
          } else if (c.k === "illeg") {
            txt(svg, X(i), H - B + 2, "?", { class: "tc-q", fill: col, "text-anchor": "middle" });
          }
        });
      });
      // hover / tap: everything printed at that x
      const hit = el("rect", { x: L, y: top, width: pw, height: ph + 6, fill: "transparent", class: "tc-hit" }, svg);
      const guide = el("line", { y1: top, y2: top + ph, class: "tc-guide", visibility: "hidden" }, svg);
      const at = ev => {
        const r = svg.getBoundingClientRect(), x = (ev.clientX - r.left) * W / r.width;
        let best = 0, bd = 1e9; for (let i = 0; i < n; i++) { const dd = Math.abs(X(i) - x); if (dd < bd) { bd = dd; best = i; } }
        guide.setAttribute("x1", X(best)); guide.setAttribute("x2", X(best)); guide.setAttribute("visibility", "visible");
        showTip(ev, `<b>${esc(p.x[best].label)}</b>` + on.map(k => `<div><i style="background:${color(k)}"></i>${esc(S[k].short || S[k].label)}: ${esc(shown(S[k].pts[best]))}</div>`).join(""));
        if (!p.byRow) flash(S[on[0]].rows[best]); else flash(S[on[0]].rows[0]);
      };
      hit.addEventListener("pointermove", at); hit.addEventListener("pointerdown", at);
      hit.addEventListener("pointerleave", ev => { if (ev.pointerType === "mouse") guide.setAttribute("visibility", "hidden"); });
      svg.setAttribute("aria-label", `Line chart of ${on.length} series over ${n} printed ${p.byRow ? "columns" : "rows"}`);
    }

    function barChart(box, on, W, narrow) {
      const stack = st.mode === "stack" && p.stackable;
      const sk = stack ? p.stackable.parts.filter(k => st.on.has(k)) : on;
      let cats = p.cats.map((c, i) => Object.assign({ k: i }, c)).filter(c => st.totals || !c.total);
      const key = c => { const v = sk.map(k => S[k].pts[c.k]).filter(x => x.k === "num").map(x => x.v); return v.length ? (stack ? v.reduce((a, b) => a + b, 0) : v[0]) : null; };
      if (st.sort !== "printed") {
        const groups = []; cats.forEach(c => { const g = groups.find(x => x.g === c.group); if (g) g.c.push(c); else groups.push({ g: c.group, c: [c] }); });
        groups.forEach(g => g.c.sort((a, b) => { const x = key(a), y = key(b); if (x === null) return 1; if (y === null) return -1; return st.sort === "desc" ? y - x : x - y; }));
        cats = groups.flatMap(g => g.c);
      }
      if (!cats.length) { const q = document.createElement("p"); q.className = "tc-msg"; q.textContent = "Only total rows are printed here — use “Show total rows”."; box.appendChild(q); return; }
      const vals = [];
      cats.forEach(c => {
        if (stack) { let a = 0; sk.forEach(k => { const x = S[k].pts[c.k]; if (x.k === "num") a += x.v; }); vals.push(a); const t = S[p.stackable.total].pts[c.k]; if (t.k === "num") vals.push(t.v); }
        else sk.forEach(k => { const x = S[k].pts[c.k]; if (x.k === "num") vals.push(x.v); });
      });
      if (!vals.length) { const q = document.createElement("p"); q.className = "tc-msg"; q.textContent = "No printed figures in the chosen series."; box.appendChild(q); return; }
      const T = ticks(Math.min(0, ...vals), Math.max(0, ...vals), narrow ? 3 : 5), lo = T[0], hi = T[T.length - 1];
      const labW = narrow ? 0 : Math.min(W * 0.38, Math.max(...cats.map(c => textW(c.label, 12))) + 10);
      const L = narrow ? 6 : labW + 6, R = 34, top = 22;
      const bh = stack ? 14 : Math.max(5, Math.min(13, 26 / sk.length)), band = (stack ? bh : bh * sk.length) + (narrow ? 22 : 8);
      let hasGroup = false, H = top;
      const rowsY = [];
      let g0 = null;
      cats.forEach(c => { if (c.group && c.group !== g0) { H += 20; hasGroup = true; } g0 = c.group; rowsY.push(H); H += band; });
      H += 8;
      const svg = el("svg", { viewBox: `0 0 ${W} ${H}`, width: "100%", class: "tc-svg", role: "img" }, box);
      const pw = W - L - R, Xv = v => L + (v - lo) / (hi - lo) * pw;
      T.forEach(t => { el("line", { x1: Xv(t), x2: Xv(t), y1: top - 4, y2: H - 6, class: t === 0 ? "tc-zero" : "tc-grid" }, svg); txt(svg, Xv(t), top - 9, fmt(t), { class: "tc-ax", "text-anchor": "middle" }); });
      g0 = null;
      cats.forEach((c, ci) => {
        let y = rowsY[ci];
        if (c.group && c.group !== g0) txt(svg, 4, y - 6, clip(c.group, 12, W - 10), { class: "tc-gl" });
        g0 = c.group;
        const by = narrow ? y + 16 : y + 4;
        if (narrow) txt(svg, L, y + 11, clip(c.label, 12, W - 12), { class: "tc-lab" + (c.total ? " tc-tot" : "") });
        else txt(svg, L - 6, by + (stack ? bh : bh * sk.length) / 2 + 4, clip(c.label, 12, labW - 4), { class: "tc-lab" + (c.total ? " tc-tot" : ""), "text-anchor": "end" });
        const tipHtml = () => `<b>${esc((c.group ? c.group + " — " : "") + c.label)}</b>` + (stack ? sk.concat([p.stackable.total]) : sk).map(k => `<div><i style="background:${color(k)}"></i>${esc(S[k].short || S[k].label)}: ${esc(shown(S[k].pts[c.k]))}</div>`).join("") + (stack ? sumNote(c) : "");
        if (stack) {
          let a = 0;
          sk.forEach(k => { const x = S[k].pts[c.k]; if (x.k === "num" && x.v > 0) { el("rect", { x: Xv(a), y: by, width: Math.max(0.5, Xv(a + x.v) - Xv(a)), height: bh, fill: color(k) }, svg); a += x.v; } });
          const miss = sk.filter(k => S[k].pts[c.k].k === "illeg").length;
          const t = S[p.stackable.total].pts[c.k];
          if (t.k === "num") {
            el("line", { x1: Xv(t.v), x2: Xv(t.v), y1: by - 3, y2: by + bh + 3, class: "tc-totmark" }, svg);
            const allNum = sk.every(k => S[k].pts[c.k].k === "num") && sk.length === p.stackable.parts.length;
            if (allNum && Math.abs(a - t.v) > 1e-6 * Math.max(1, Math.abs(t.v))) txt(svg, Math.max(Xv(a), Xv(t.v)) + 5, by + bh - 2, "≠", { class: "tc-neq" });
          }
          if (miss) txt(svg, Xv(a) + 4, by + bh - 2, "?", { class: "tc-q" });
        } else {
          sk.forEach((k, si) => {
            const x = S[k].pts[c.k], yy = by + si * bh;
            if (x.k === "num") { const a = Xv(Math.min(0, x.v)), b = Xv(Math.max(0, x.v)); el("rect", { x: a, y: yy, width: Math.max(0.5, b - a), height: bh - 1, fill: color(k) }, svg); }
            else if (x.k === "illeg") txt(svg, Xv(0) + 4, yy + bh - 2, "?", { class: "tc-q", fill: color(k) });
          });
        }
        const hit = el("rect", { x: 0, y: y, width: W, height: band, fill: "transparent", class: "tc-hit" }, svg);
        hit.addEventListener("pointermove", ev => { showTip(ev, tipHtml()); flash(c.i); });
        hit.addEventListener("pointerdown", ev => { showTip(ev, tipHtml()); flash(c.i); });
      });
      svg.setAttribute("aria-label", `Bar chart of ${cats.length} printed rows`);
    }
    function sumNote(c) {
      const t = S[p.stackable.total].pts[c.k];
      if (t.k !== "num") return "";
      const parts = p.stackable.parts.map(k => S[k].pts[c.k]);
      if (!parts.every(x => x.k === "num")) return `<div class="tc-sum">Parts incomplete in print; not checked against the total.</div>`;
      const a = parts.reduce((s, x) => s + x.v, 0);
      if (Math.abs(a - t.v) <= 1e-6 * Math.max(1, Math.abs(t.v))) return `<div class="tc-sum">Parts add up to the printed total.</div>`;
      return `<div class="tc-sum warn">Parts add up to ${(+a.toFixed(4)).toLocaleString("en-US")}; printed total ${esc(t.s)}.</div>`;
    }

    setView(0);
    let rw = plot.clientWidth;
    if (window.ResizeObserver) new ResizeObserver(() => { if (Math.abs(plot.clientWidth - rw) > 8) { rw = plot.clientWidth; draw(); } }).observe(plot);
    return true;
  }

  // Lazily mount every chart placeholder inside root (rendered when it scrolls near the screen).
  let IO = null;
  function mountAll(root, getTable, opt) {
    const els = [...(root || document).querySelectorAll(".tchart[data-id]:not([data-done])")];
    const go = e => { e.dataset.done = "1"; const t = getTable(e.dataset.id); if (t) mount(e, t, +e.dataset.p, opt); };
    if (!window.IntersectionObserver) { els.forEach(go); return; }
    if (!IO) IO = new IntersectionObserver(es => es.forEach(x => { if (x.isIntersecting) { IO.unobserve(x.target); go(x.target); } }), { rootMargin: "400px" });
    els.forEach(e => { if (e.offsetParent === null && !e.closest("[hidden]")) IO.observe(e); else IO.observe(e); });
  }
  // Whether a table has anything to chart (decides if the Table/Chart switch is shown).
  const chartable = t => (t.parts || []).some(p => !!model(p));
  window.TableCharts = { mount, mountAll, chartable, _cell: cell, _year: yearOf, _model: model, _plan: plan, _views: views, _defaults: defaults };
})();
