/* daychart.js — "a day in the life" charts for the 國民生活時間調査 (NHK time-use survey, 1941–42) tables.
   Hand-written site script (stat-tables-site). No dependencies.

   Three kinds of table are drawn:
   - 時刻別行爲別人員數百分比表: the share of people doing each activity in each 10-minute slot (午前 + 午後 = 144 slots)
     -> a 24-hour stacked "day ribbon" by activity family, a family can be opened to show its activities, plus a strip
        with the share of people outside the home.
   - 時刻別聽取適否參考表: the share for whom each slot was suitable (甲, 乙) or unsuitable for radio, or who were asleep
     -> the same ribbon with those four bands (the book printed these as charts, 參考圖, without figures).
   - 行爲別一人一日當消費時間量表: hours and minutes per day by activity -> one 24-hour bar per group.

   Like charts.js, a chart is another way of reading the printed table, never a cleaned copy: only printed figures
   are drawn, unreadable cells are left out and marked, rows are not rescaled to 100, labels stay as printed. */
(function () {
  "use strict";
  const NS = "http://www.w3.org/2000/svg";

  // ---- activity families (validated categorical palette, light and dark; stacked bottom -> top) --------------
  const FAM = [
    { k: "sleep", en: "Sleep", ja: "睡眠", c: ["#6250d6", "#9085e9"] },
    { k: "care", en: "Meals & personal care", ja: "食事・身ノ廻リ", c: ["#eda100", "#c98500"] },
    { k: "house", en: "Housework & needlework", ja: "家事・針仕事", c: ["#e87ba4", "#d55181"] },
    { k: "work", en: "Work & commuting", ja: "從業・通勤", c: ["#2a78d6", "#3987e5"] },
    { k: "leisure", en: "Learning & leisure", ja: "勉強・教養・娛樂", c: ["#1baf7a", "#199e70"] },
    { k: "other", en: "Public duties & other", ja: "公務・其他", c: ["#eb6834", "#d95926"] },
  ];
  const ACT = {
    "睡眠": ["sleep", "Sleep"],
    "食事": ["care", "Meals"], "身ノ廻リ": ["care", "Personal care"], "入浴": ["care", "Bathing"], "休息": ["care", "Rest"],
    "家事": ["house", "Housework"], "針仕事": ["house", "Needlework"],
    "從業": ["work", "Work"], "農事": ["work", "Farm work"], "手仕事": ["work", "Handwork"], "内職": ["work", "Piecework at home"],
    "通勤": ["work", "Commuting"], "營業": ["work", "Business"],
    "勉強": ["leisure", "Study"], "教養": ["leisure", "Self-improvement"], "趣味": ["leisure", "Hobbies"],
    "娛樂": ["leisure", "Entertainment"], "運動": ["leisure", "Exercise"], "交際": ["leisure", "Socializing"],
    "公務": ["other", "Public duties"], "其他": ["other", "Other"],
  };
  const RADIO = [   // bottom -> top
    { k: "睡眠", en: "Asleep", c: ["#6250d6", "#9085e9"] },
    { k: "不適", en: "Unsuitable", c: ["#eb6834", "#d95926"] },
    { k: "適(乙)", en: "Suitable while busy", c: ["#8fd9bd", "#14684b"] },
    { k: "適(甲)", en: "Free to listen", c: ["#1baf7a", "#199e70"] },
  ];
  const OUT_C = ["#008300", "#0ca30c"];

  const dark = () => {
    const t = document.documentElement.getAttribute("data-theme");
    if (t) return t === "dark";
    return window.matchMedia && matchMedia("(prefers-color-scheme: dark)").matches;
  };
  const col = c => c[dark() ? 1 : 0];
  const famOf = k => FAM.find(f => f.k === k);
  const esc = s => String(s == null ? "" : s).replace(/[&<>"]/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
  function el(tag, attrs, parent) {
    const e = document.createElementNS(NS, tag);
    for (const k in attrs || {}) e.setAttribute(k, attrs[k]);
    if (parent) parent.appendChild(e);
    return e;
  }
  function txt(parent, x, y, s, attrs) { const t = el("text", Object.assign({ x, y }, attrs || {}), parent); t.textContent = s; return t; }
  // shade of a colour towards the surface (for the activities inside an opened family)
  function shade(hex, f) {
    const s = dark() ? [26, 26, 25] : [252, 252, 251], n = parseInt(hex.slice(1), 16), c = [n >> 16, (n >> 8) & 255, n & 255];
    return "#" + c.map((v, i) => Math.round(v + (s[i] - v) * f).toString(16).padStart(2, "0")).join("");
  }

  // ---- reading cells -----------------------------------------------------------------------------------------
  // a percentage cell -> {v} (dash = 0) | {ill} unreadable | {blank} | {txt}
  function pct(c) {
    const s = String(c == null ? "" : c).normalize("NFKC").trim();
    if (s === "") return { blank: true, s };
    if (s === "[?]") return { ill: true, s };
    if (/^[-–—―ー‐−]+$/.test(s)) return { v: 0, s, dash: true };
    if (/^\d+(\.\d+)?$/.test(s)) return { v: +s, s };
    return { txt: true, s };
  }
  // a printed duration ("14 53.0" = 14 h 53.0 min, "33.5" = 33.5 min, "24 00", "7 56 2" with the point lost) -> hours
  function dur(c) {
    const s = String(c == null ? "" : c).normalize("NFKC").replace(/\s+/g, " ").trim();
    if (s === "") return { blank: true, s };
    if (s === "[?]") return { ill: true, s };
    if (/^[-–—―ー‐−]+$/.test(s)) return { v: 0, s, dash: true };
    let m;
    if ((m = s.match(/^(\d{1,2}) (\d{1,2})\.(\d)$/))) return { v: +m[1] + (+m[2] + m[3] / 10) / 60, s };
    if ((m = s.match(/^(\d{1,2}) (\d{2})$/))) return { v: +m[1] + +m[2] / 60, s };
    if ((m = s.match(/^(\d{1,2}) (\d{1,2}) (\d)$/))) return { v: +m[1] + (+m[2] + m[3] / 10) / 60, s };
    if ((m = s.match(/^(\d{1,2})\.(\d)$/))) return { v: (+m[1] + m[2] / 10) / 60, s };
    if ((m = s.match(/^(\d{1,2}) (\d)$/))) return { v: (+m[1] + m[2] / 10) / 60, s };
    return { txt: true, s };
  }
  const hm = h => { const t = Math.round(h * 60); return Math.floor(t / 60) + "h " + String(t % 60).padStart(2, "0") + "m"; };

  // ---- which tables ------------------------------------------------------------------------------------------
  const TIME = /^\s*\d{1,2}[.:・ ]?\d{0,2}\s*[—–\-]/;
  function slotParts(t) {
    const ps = t.parts || [];
    const am = ps.find(p => /午前/.test(p.label || "")), pm = ps.find(p => /午後/.test(p.label || ""));
    if (!am || !pm) return null;
    if (am.rows.length < 60 || pm.rows.length < 60) return null;
    if (!am.rows.slice(0, 5).some(r => TIME.test(String(r[0])))) return null;
    return [am, pm];
  }
  function kind(t) {
    const ch = t.chapter || "";
    if (/^行爲別一人一日/.test(ch)) return (t.parts || []).length ? "budget" : null;
    const sp = slotParts(t);
    if (!sp) return null;
    return sp[0].columns.some(c => /^適\s*\(甲\)/.test(c)) ? "radio" : (/^時刻別行爲別/.test(ch) ? "act" : null);
  }
  const applies = t => !!kind(t);

  // ---- slot model (both ribbon kinds) ------------------------------------------------------------------------
  // -> {slots:[{lab, part, ri}], series:[{key, name, en, fam, color, v:[...], s:[...], ill:[...], vin, vout}], out:{v,s}}
  function slotModel(t, kd) {
    const [am, pm] = slotParts(t);
    const slots = [];
    [am, pm].forEach((p, pi) => p.rows.forEach((r, ri) => slots.push({ lab: String(r[0]), half: pi, ri, p })));
    const cols = am.columns, n = slots.length;
    const get = (c, i) => { const s = slots[i]; const j = s.p.columns.indexOf(c); return j < 0 ? { blank: true, s: "" } : pct(s.p.rows[s.ri][j]); };
    const series = [];
    let outCol = null;
    if (kd === "radio") {
      RADIO.forEach(R => {
        const c = cols.find(x => x.replace(/\s/g, "") === R.k.replace(/\s/g, ""));
        if (!c) return;
        series.push(mk(R.k, R.en, null, R.c, i => get(c, i)));
      });
      outCol = cols.find(c => c === "外");
      return { slots, series, out: outCol ? slots.map((_, i) => get(outCol, i)) : null, split: false };
    }
    const split = cols.some(c => / — 内$/.test(c));
    const names = [];
    cols.slice(1).forEach(c => {
      const base = split ? c.replace(/ — (内|外)$/, "") : c;
      if (/^全行爲$/.test(base) || (!split && /^(内|外)$/.test(c))) return;
      if (!names.includes(base)) names.push(base);
    });
    if (split) outCol = cols.find(c => /^全行爲 — 外$/.test(c));
    else outCol = cols.find(c => c === "外");
    names.forEach(nm => {
      const a = ACT[nm] || ["other", nm];
      const f = famOf(a[0]);
      if (split) {
        const ci = nm + " — 内", co = nm + " — 外";
        const S = mk(nm, a[1], a[0], f.c, i => sum2(get(ci, i), get(co, i)));
        S.vin = slots.map((_, i) => get(ci, i)); S.vout = slots.map((_, i) => get(co, i));
        series.push(S);
      } else series.push(mk(nm, a[1], a[0], f.c, i => get(nm, i)));
    });
    // keep the printed order inside a family, families in FAM order
    series.sort((x, y) => FAM.findIndex(f => f.k === x.fam) - FAM.findIndex(f => f.k === y.fam));
    return { slots, series, out: outCol ? slots.map((_, i) => get(outCol, i)) : null, split };
    function mk(key, en, fam, c, f) {
      const cells = slots.map((_, i) => f(i));
      return { key, en, fam, c, cells, v: cells.map(x => (x.v == null ? null : x.v)) };
    }
    function sum2(a, b) {
      if (a.ill || b.ill) return { ill: true, s: a.s + " / " + b.s };
      const va = a.v == null ? null : a.v, vb = b.v == null ? null : b.v;
      if (va == null && vb == null) return a.blank && b.blank ? { blank: true, s: "" } : { txt: true, s: a.s + " / " + b.s };
      return { v: (va || 0) + (vb || 0), s: a.s + " / " + b.s };
    }
  }

  // printed time label -> clock text for the tooltip ("7.20—7.30" in 午前 -> "7:20–7:30 a.m.")
  function clock(s) {
    const h = s.half ? "p.m." : "a.m.";
    const a = Math.floor(s.ri / 6), m = (s.ri % 6) * 10, m2 = m + 10;
    const f = (hh, mm) => (mm === 60 ? (hh + 1 || 12) + ":00" : (hh || 12) + ":" + String(mm).padStart(2, "0"));
    return f(a, m) + "–" + f(a, m2) + " " + h;
  }

  // ---- what a table is about (from its uniform printed title) -------------------------------------------------
  const SERIES_BOOKS = ["japan-seikatsu-jikan-nogyo-1943", "japan-seikatsu-jikan-joshi-1943", "japan-seikatsu-jikan-hokyu-1943", "japan-seikatsu-jikan-kouri-1943"];
  const GRP = {
    "農業世帶": "Farm households", "俸給生活者": "Salaried employees", "工場勞務者": "Factory workers",
    "俸給生活者女子家族": "Women of salaried households", "工場勞務者女子家族": "Women of factory households",
    "世帶主・家族": "Shopkeepers & families", "營業使用人": "Shop employees",
  };
  const SERN = { "全國": "Whole country", "地方別": "By region", "官公吏會社員別": "Officials vs company employees", "主要事業別": "By industry",
    "經營規模別": "By size of works", "通勤寄宿別": "Living at home vs in dormitories", "都市別": "By size of city" };
  const PLACE = { "全國": "Whole country", "北海道・東北・北陸": "Hokkaidō, Tōhoku, Hokuriku", "關東": "Kantō", "東山・東海": "Tōsan, Tōkai", "近畿": "Kinki",
    "中國・四國・九州": "Chūgoku, Shikoku, Kyūshū", "北海道": "Hokkaidō", "東北": "Tōhoku", "北陸": "Hokuriku", "東山": "Tōsan", "東海": "Tōkai",
    "中國": "Chūgoku", "四國": "Shikoku", "九州": "Kyūshū", "官公吏": "Government officials", "會社員": "Company employees", "紡織": "Textiles",
    "金屬": "Metals", "機械": "Machinery", "化學": "Chemicals", "大規模": "Large works", "中規模": "Medium works", "小規模": "Small works",
    "通勤": "Living at home", "寄宿": "In dormitories", "大都市": "Large cities", "中都市": "Medium cities", "小都市": "Small cities" };
  const REGG = { "北海道・東北・北陸": 0, "北海道": 0, "東北": 0, "北陸": 0, "關東": 1, "東山・東海": 2, "東山": 2, "東海": 2, "近畿": 3,
    "中國・四國・九州": 4, "中國": 4, "四國": 4, "九州": 4 };
  // validated categorical palette for comparison lines (adjacent pairs; light, dark)
  const LINE = [["#2a78d6", "#3987e5"], ["#eb6834", "#d95926"], ["#1baf7a", "#199e70"], ["#eda100", "#c98500"], ["#e87ba4", "#d55181"],
    ["#008300", "#0ca30c"], ["#6250d6", "#9085e9"], ["#e34948", "#e66767"]];
  const MAR = { "": "", "無配": "unmarried", "有配": "married" };
  const DIMC = new WeakMap();
  function dims(t, slug) {
    if (DIMC.has(t)) return DIMC.get(t);
    const ti = String(t.title || "").replace(/歲/g, "歳").replace(/労/g, "勞").replace(/\s+/g, " ").trim();
    const kd = kind(t);
    const sex = /女子/.test(ti) ? "F" : /男子/.test(ti) ? "M" : "";
    const am = ti.match(/(\d+)歳\s*[—–-]+\s*(\d+)歳|61歳以上/);
    const age = am ? (am[1] ? am[1] + "–" + am[2] : "61+") : "";
    const mm = ti.match(/\((全|無配|有配)\)/);
    const mar = mm && mm[1] !== "全" ? mm[1] : "";
    const gm = ti.match(/(俸給生活者女子家族|工場勞務者女子家族|俸給生活者|工場勞務者|世帶主・家族|營業使用人)/);
    const grp = gm ? gm[1] : /nogyo/.test(slug || "") ? "農業世帶" : "";
    const sm = ti.match(/^(?:I{1,3}|IV|VI|V)\s+(\S+?)\s*\(/);
    let series = sm ? sm[1].replace(/\s/g, "") : (kd === "radio" ? "地方別" : "");
    if (kd === "budget") series = /全國/.test(ti) ? "全國" : (ti.match(/(地方別|都市別|官公吏會社員別|主要事業別|經營規模別|通勤寄宿別)/) || ["", ""])[1];
    let tail = am ? ti.slice(ti.indexOf(am[0]) + am[0].length) : "";
    tail = tail.replace(/\((全|無配|有配)\)/g, "").trim();
    const place = tail || (series === "全國" || /全國/.test(ti) ? "全國" : "");
    const d = { kd, sex, age, mar, grp, series, place, slug: slug || "" };
    DIMC.set(t, d);
    return d;
  }
  const ageKey = a => parseInt(a) || 99;
  const sexEn = s => (s === "M" ? "Men" : s === "F" ? "Women" : "");
  const ageEn = (a, m) => (a ? "aged " + a : "") + (m ? " (" + MAR[m] + ")" : "");
  const placeEn = p => (PLACE[p] ? PLACE[p] + (p !== "全國" && /[^\x00-\x7f]/.test(p) ? " " + p : "") : p);

  // ---- styles ------------------------------------------------------------------------------------------------
  let styled = false;
  function style() {
    if (styled) return; styled = true;
    const st = document.createElement("style");
    st.textContent = `
.tday{position:relative}
.dc-head{display:flex;flex-wrap:wrap;gap:6px 14px;align-items:center;margin:2px 0 8px}
.dc-title{font-size:13px;color:var(--muted)}
.dc-leg{display:flex;flex-wrap:wrap;gap:4px 6px;margin:0 0 6px}
.dc-leg button{display:inline-flex;align-items:center;gap:6px;font-size:12.5px;padding:3px 9px;border-radius:14px;border:1px solid var(--line);background:transparent;color:var(--ink);cursor:pointer;box-shadow:none}
.dc-leg button i{display:inline-block;width:11px;height:11px;border-radius:3px}
.dc-leg button.on{border-color:var(--accent);background:var(--hi)}
.dc-leg button small{color:var(--muted);font-size:11px}
.dc-leg .dc-back{font-weight:600}
.dc-svg{display:block;width:100%;height:auto;overflow:visible;font-family:inherit}
.dc-svg text{font-size:11px;fill:var(--muted)}
.dc-svg .dc-in{font-size:11.5px;font-weight:600}
.dc-svg .dc-cap{font-size:11.5px;fill:var(--ink)}
.dc-grid{stroke:var(--line);stroke-width:1}
.dc-tip{position:absolute;z-index:5;pointer-events:none;background:var(--panel);color:var(--ink);border:1px solid var(--line);border-radius:6px;box-shadow:0 4px 14px rgba(0,0,0,.18);padding:7px 9px;font-size:12px;line-height:1.45;min-width:180px;max-width:300px}
.dc-tip b{font-size:12.5px}
.dc-tip .r{display:flex;gap:6px;align-items:baseline}
.dc-tip .r i{display:inline-block;width:9px;height:9px;border-radius:2px;flex:none;transform:translateY(1px)}
.dc-tip .r span:last-child{margin-left:auto;font-variant-numeric:tabular-nums;padding-left:10px}
.dc-tip .f{padding-left:0;font-weight:600}
.dc-tip .m{padding-left:15px;color:var(--muted)}
.dc-tip .n{margin-top:4px;color:var(--muted);font-size:11.5px}
.dc-tip .w{color:var(--warn)}
.dc-note{font-size:12px;color:var(--muted);margin-top:6px}
.dc-ctl{display:flex;flex-wrap:wrap;gap:6px 14px;align-items:center;margin:2px 0 8px;font-size:13px;color:var(--muted)}
.dc-ctl select{font-size:13px;padding:2px 6px;margin-left:5px;max-width:260px}
.dc-keys{display:flex;flex-wrap:wrap;gap:6px;margin:0 0 8px}
.dc-keys span{font-size:12px;border-left:3px solid var(--accent);background:var(--hi);padding:3px 8px;border-radius:0 6px 6px 0;color:var(--ink)}
.dc-keys span b{font-weight:600;color:var(--muted);margin-right:5px}
.dc-tog{font-size:12.5px;color:var(--muted);display:inline-flex;gap:5px;align-items:center;cursor:pointer}
`;
    document.head.appendChild(st);
  }

  // ---- ribbon ------------------------------------------------------------------------------------------------
  function ribbon(box, t, kd) {
    const M = slotModel(t, kd);
    const n = M.slots.length;
    if (!n || !M.series.length) return false;
    const head = document.createElement("div"); head.className = "dc-head"; box.appendChild(head);
    const leg = document.createElement("div"); leg.className = "dc-leg"; box.appendChild(leg);
    const keys = document.createElement("div"); keys.className = "dc-keys"; box.insertBefore(keys, leg);
    keyMoments(t, kd).forEach(([a, b, why]) => { const sp = document.createElement("span"); sp.title = why; sp.innerHTML = `<b>${esc(a)}</b>${esc(b)}`; keys.appendChild(sp); });
    const plot = document.createElement("div"); box.appendChild(plot);
    const note = document.createElement("div"); note.className = "dc-note"; box.appendChild(note);
    const tip = document.createElement("div"); tip.className = "dc-tip"; tip.hidden = true; box.appendChild(tip);
    let open = null, inout = false;

    const illSlots = new Set();
    M.series.forEach(S => S.cells.forEach((c, i) => { if (c.ill) illSlots.add(i); }));
    const nIll = M.series.reduce((a, S) => a + S.cells.filter(c => c.ill).length, 0);
    const rowSum = i => M.series.reduce((a, S) => a + (S.v[i] || 0), 0);
    let off = 0;
    for (let i = 0; i < n; i++) if (!illSlots.has(i) && Math.abs(rowSum(i) - 100) > 1.5) off++;
    head.innerHTML = `<span class="dc-title">${kd === "radio" ? "Share of persons for whom each 10-minute slot was suitable for listening to the radio" : "Share of persons in each activity, every 10 minutes from midnight to midnight"}</span>` +
      (M.split ? `<label class="dc-tog"><input type="checkbox"> show outdoors (外) inside each band</label>` : "");
    const tog = head.querySelector("input");
    if (tog) tog.onchange = () => { inout = tog.checked; draw(); };
    note.textContent = "Each column is one printed 10-minute row; figures are drawn as printed, not rescaled to 100." +
      (nIll ? ` ${nIll} unreadable cell${nIll > 1 ? "s are" : " is"} left out (marked ▾ above the slot).` : "") +
      (off ? ` ${off} row${off > 1 ? "s do" : " does"} not add to 100 in print.` : "");

    // groups shown in the stack: families (act) or the four radio bands
    function bands() {
      if (kd === "radio") return M.series.map(S => ({ key: S.key, en: S.en, ja: S.key, color: col(S.c), mem: [S] }));
      if (open) {
        const f = famOf(open), mem = M.series.filter(S => S.fam === open);
        return mem.map((S, j) => ({ key: S.key, en: S.en, ja: S.key, color: shade(col(f.c), mem.length > 1 ? j / (mem.length) * 0.62 : 0), mem: [S] }));
      }
      return FAM.map(f => ({ key: f.k, en: f.en, ja: f.ja, color: col(f.c), mem: M.series.filter(S => S.fam === f.k) })).filter(b => b.mem.length);
    }
    const bval = (b, i) => b.mem.reduce((a, S) => a + (S.v[i] || 0), 0);
    const bout = (b, i) => b.mem.reduce((a, S) => a + (S.vout && S.vout[i].v ? S.vout[i].v : 0), 0);

    function legend() {
      leg.innerHTML = "";
      if (kd === "act" && open) {
        const bk = document.createElement("button"); bk.className = "dc-back"; bk.type = "button"; bk.textContent = "← All activities"; bk.onclick = () => { open = null; draw(); }; leg.appendChild(bk);
      }
      bands().forEach(b => {
        const bt = document.createElement("button"); bt.type = "button";
        bt.innerHTML = `<i style="background:${b.color}"></i>${esc(b.en)} <small>${esc(b.ja)}</small>`;
        if (kd === "act" && !open) { bt.title = "Show the activities in this group"; bt.onclick = () => { open = b.key; draw(); }; }
        else bt.style.cursor = "default";
        leg.appendChild(bt);
      });
    }

    function draw() {
      legend();
      plot.innerHTML = "";
      const W = Math.max(320, plot.clientWidth || box.clientWidth || 800), narrow = W < 520;
      const L = narrow ? 30 : 38, R = 8, T = open ? 12 : 34, H1 = narrow ? 210 : 270, gap = 18, H2 = M.out ? (narrow ? 46 : 58) : 0, B = 26;
      const pw = W - L - R, sw = pw / n;
      const svg = el("svg", { viewBox: `0 0 ${W} ${T + H1 + (H2 ? gap + H2 : 0) + B}`, class: "dc-svg", role: "img" }, plot);
      const BS = bands();
      let ymax = 100;
      if (open) { ymax = 0; for (let i = 0; i < n; i++) ymax = Math.max(ymax, BS.reduce((a, b) => a + bval(b, i), 0)); ymax = Math.max(5, Math.ceil(ymax / 10) * 10); }
      else for (let i = 0; i < n; i++) ymax = Math.max(ymax, Math.ceil(rowSum(i) / 5) * 5);
      const y = v => T + H1 - v / ymax * H1;
      // grid
      const step = ymax > 50 ? 25 : ymax > 20 ? 10 : 5;
      for (let v = 0; v <= ymax + 0.01; v += step) {
        el("line", { x1: L, x2: L + pw, y1: y(v), y2: y(v), class: "dc-grid", "stroke-dasharray": v ? "2 3" : "" }, svg);
        txt(svg, L - 5, y(v) + 4, v + "%", { "text-anchor": "end" });
      }
      for (let h = 0; h <= 24; h += 3) {
        const x = L + h * 6 * sw;
        el("line", { x1: x, x2: x, y1: T, y2: T + H1 + (H2 ? gap + H2 : 0), class: "dc-grid", "stroke-dasharray": h % 12 ? "2 3" : "" }, svg);
        const lab = h === 0 || h === 24 ? "midnight" : h === 12 ? "noon" : String(h % 12) + (h < 12 ? " am" : " pm");
        if (!narrow || h % 6 === 0) txt(svg, x, T + H1 + (H2 ? gap + H2 : 0) + 16, lab, { "text-anchor": h === 0 ? "start" : h === 24 ? "end" : "middle" });
      }
      // stacked bands (step paths: each 10-minute slot is one column)
      const base = new Array(n).fill(0);
      const surf = dark() ? "#1a1a19" : "#fcfcfb";
      BS.forEach((b, bi) => {
        const top = [];
        for (let i = 0; i < n; i++) top.push(base[i] + bval(b, i));
        let d = "";
        for (let i = 0; i < n; i++) { const x0 = L + i * sw, x1 = x0 + sw; d += (i ? "L" : "M") + x0.toFixed(2) + "," + y(top[i]).toFixed(2) + "L" + x1.toFixed(2) + "," + y(top[i]).toFixed(2); }
        for (let i = n - 1; i >= 0; i--) { const x0 = L + i * sw, x1 = x0 + sw; d += "L" + x1.toFixed(2) + "," + y(base[i]).toFixed(2) + "L" + x0.toFixed(2) + "," + y(base[i]).toFixed(2); }
        el("path", { d: d + "Z", fill: b.color, stroke: surf, "stroke-width": 1, "stroke-linejoin": "round" }, svg);
        // outdoors part of the band (hatched), when asked for
        if (inout && M.split) {
          let dd = "";
          for (let i = 0; i < n; i++) { const o = bout(b, i); if (!o) continue; const x0 = L + i * sw; dd += `M${x0.toFixed(2)},${y(top[i]).toFixed(2)}h${sw.toFixed(2)}V${y(top[i] - o).toFixed(2)}h${(-sw).toFixed(2)}Z`; }
          if (dd) el("path", { d: dd, fill: "url(#dc-hatch)" }, svg);
        }
        // direct label where the whole label fits inside the band (the band's clear height over the label's width)
        const lab = narrow ? b.en.split(/ [&(]/)[0] : b.en.replace(/ \(.*\)/, "");
        const half = Math.ceil((lab.length * 6.6 + 8) / 2 / sw);
        let best = null;
        for (let c = half; c < n - half; c++) {
          let lo = -Infinity, hi = Infinity;
          for (let i = c - half; i <= c + half; i++) { lo = Math.max(lo, base[i]); hi = Math.min(hi, top[i]); }
          if (hi - lo > (best ? best[1] : 0)) best = [c, hi - lo, (lo + hi) / 2];
        }
        if (best && (best[1] / ymax) * H1 > 17) {
          const t1 = txt(svg, L + (best[0] + 0.5) * sw, y(best[2]) + 4, lab, { "text-anchor": "middle", class: "dc-in", style: "fill:#fff" });
          t1.setAttribute("paint-order", "stroke"); t1.setAttribute("stroke", "rgba(0,0,0,.4)"); t1.setAttribute("stroke-width", "2.5");
        }
        for (let i = 0; i < n; i++) base[i] = top[i];
      });
      if (inout && M.split) {
        const defs = el("defs", {}, svg), pt = el("pattern", { id: "dc-hatch", width: 5, height: 5, patternUnits: "userSpaceOnUse", patternTransform: "rotate(45)" }, defs);
        el("rect", { width: 5, height: 5, fill: "rgba(255,255,255,.18)" }, pt);
        el("line", { x1: 0, y1: 0, x2: 0, y2: 5, stroke: "rgba(255,255,255,.75)", "stroke-width": 2 }, pt);
        svg.insertBefore(defs, svg.firstChild);
      }
      // "most common": the band with the largest printed share in each slot
      if (!open) {
        txt(svg, L, 10, kd === "radio" ? "Largest group in each 10 minutes" : "Most common activity in each 10 minutes", { class: "dc-cap" });
        for (let i = 0; i < n; i++) {
          if (illSlots.has(i)) continue;
          let bb = null, bv = 0;
          BS.forEach(b => { const v = bval(b, i); if (v > bv) { bv = v; bb = b; } });
          if (bb) el("rect", { x: L + i * sw, y: 15, width: sw + 0.3, height: 9, fill: bb.color }, svg);
        }
      }
      // unreadable marks
      illSlots.forEach(i => txt(svg, L + (i + 0.5) * sw, T - 2, "▾", { "text-anchor": "middle", fill: "var(--warn)", style: "font-size:10px;fill:var(--warn)" }));
      // outdoors strip
      if (H2) {
        const y2 = v => T + H1 + gap + H2 - v / 100 * H2;
        txt(svg, L + 4, T + H1 + gap - 4, "Outside the home (外), % of persons", { class: "dc-cap" });
        let d = "", open_ = false;
        for (let i = 0; i < n; i++) {
          const c = M.out[i];
          if (c.v == null) { open_ = false; continue; }
          const x0 = L + i * sw;
          d += (open_ ? "L" : "M") + x0.toFixed(2) + "," + y2(c.v).toFixed(2) + "L" + (x0 + sw).toFixed(2) + "," + y2(c.v).toFixed(2);
          open_ = true;
        }
        el("rect", { x: L, y: T + H1 + gap, width: pw, height: H2, fill: "none", class: "dc-grid" }, svg);
        txt(svg, L - 5, y2(100) + 4, "100", { "text-anchor": "end" });
        txt(svg, L - 5, y2(0), "0", { "text-anchor": "end" });
        el("path", { d, fill: "none", stroke: col(OUT_C), "stroke-width": 2, "stroke-linejoin": "round" }, svg);
        // light fill under the line, broken where unreadable
        let fd = "";
        for (let i = 0; i < n; i++) { const c = M.out[i]; if (c.v == null || !c.v) continue; const x0 = L + i * sw; fd += `M${x0.toFixed(2)},${y2(0).toFixed(2)}V${y2(c.v).toFixed(2)}h${sw.toFixed(2)}V${y2(0).toFixed(2)}Z`; }
        el("path", { d: fd, fill: col(OUT_C), opacity: 0.14 }, svg);
      }
      // hover layer
      const cross = el("rect", { x: 0, y: T, width: Math.max(1, sw), height: H1 + (H2 ? gap + H2 : 0), fill: "var(--ink)", opacity: 0, "pointer-events": "none" }, svg);
      const hit = el("rect", { x: L, y: T, width: pw, height: H1 + (H2 ? gap + H2 : 0), fill: "transparent" }, svg);
      const move = ev => {
        const r = svg.getBoundingClientRect(), sx = (ev.clientX - r.left) * (W / r.width);
        const i = Math.max(0, Math.min(n - 1, Math.floor((sx - L) / sw)));
        cross.setAttribute("x", L + i * sw); cross.setAttribute("opacity", 0.12);
        tip.innerHTML = tipHtml(i, BS);
        tip.hidden = false;
        const br = box.getBoundingClientRect(), tw = tip.offsetWidth, th = tip.offsetHeight;
        let tx = ev.clientX - br.left + 14; if (tx + tw > br.width) tx = ev.clientX - br.left - tw - 14;
        let ty = ev.clientY - br.top - th / 2; ty = Math.max(0, Math.min(ty, br.height - th));
        tip.style.left = Math.max(0, tx) + "px"; tip.style.top = ty + "px";
      };
      hit.addEventListener("pointermove", move); hit.addEventListener("pointerdown", move);
      hit.addEventListener("pointerleave", () => { tip.hidden = true; cross.setAttribute("opacity", 0); });
      svg.setAttribute("aria-label", (kd === "radio" ? "Radio-listening suitability" : "Activities") + " by time of day, " + t.title);
    }

    function tipHtml(i, BS) {
      const s = M.slots[i];
      let h = `<b>${esc(clock(s))}</b> <span style="color:var(--muted)">(printed ${esc(s.lab)}, ${s.half ? "午後" : "午前"})</span>`;
      const fmt = c => (c.ill ? `<span class="w">unreadable</span>` : esc(c.s || "—"));
      [...BS].reverse().forEach(b => {
        const v = bval(b, i);
        if (b.mem.length === 1 && (kd === "radio" || open)) {
          const S = b.mem[0], c = S.cells[i];
          if (!c.ill && !v) return;
          h += `<div class="r f"><i style="background:${b.color}"></i><span>${esc(S.key)} ${esc(S.en)}</span><span>${fmt(c)}${M.split && S.vin ? ` <small style="color:var(--muted)">(内 ${esc(S.vin[i].s)} · 外 ${esc(S.vout[i].s)})</small>` : ""}</span></div>`;
          return;
        }
        const anyIll = b.mem.some(S => S.cells[i].ill);
        if (!v && !anyIll) return;
        h += `<div class="r f"><i style="background:${b.color}"></i><span>${esc(b.en)}</span><span>${v ? +v.toFixed(1) + "%" : ""}</span></div>`;
        b.mem.forEach(S => { const c = S.cells[i]; if (!c.ill && !c.v) return;
          h += `<div class="r m"><span>${esc(S.key)} ${esc(S.en)}</span><span>${fmt(c)}</span></div>`; });
      });
      if (M.out) { const o = M.out[i]; h += `<div class="r" style="margin-top:3px"><i style="background:${col(OUT_C)}"></i><span>Outside the home (外)</span><span>${fmt(o)}</span></div>`; }
      const sm = rowSum(i);
      h += illSlots.has(i) ? `<div class="n w">Some cells unreadable in this row.</div>` :
        Math.abs(sm - 100) > 0.5 ? `<div class="n">Printed figures add to ${+sm.toFixed(1)}%.</div>` : "";
      return h;
    }

    draw();
    let rw = plot.clientWidth;
    if (window.ResizeObserver) new ResizeObserver(() => { if (Math.abs(plot.clientWidth - rw) > 8) { rw = plot.clientWidth; draw(); } }).observe(plot);
    if (window.matchMedia) matchMedia("(prefers-color-scheme: dark)").addEventListener?.("change", draw);
    return true;
  }

  // ---- measures (one number per slot, for comparisons and key moments) ----------------------------------------
  const MODELS = new WeakMap();
  function model(t) { if (!MODELS.has(t)) MODELS.set(t, slotModel(t, kind(t))); return MODELS.get(t); }
  function measures(kd) {
    if (kd === "radio") return [["r:適(甲)", "Free to listen 適(甲)"], ["r:both", "Could listen 適(甲)+適(乙)"], ["r:不適", "Unsuitable 不適"],
      ["r:睡眠", "Asleep 睡眠"], ["out", "Outside the home 外"]];
    const m = FAM.map(f => ["fam:" + f.k, f.en + " (all)"]);
    Object.keys(ACT).forEach(k => m.push(["act:" + k, k + " " + ACT[k][1]]));
    m.push(["out", "Outside the home 外"]);
    return m;
  }
  // value of measure id in slot i of model M; null where not printed or unreadable (left as a gap, never filled)
  function mval(M, id, i) {
    if (id === "out") return M.out ? (M.out[i].v == null ? null : M.out[i].v) : null;
    const [k, a] = id.split(":");
    let mem;
    if (k === "fam") mem = M.series.filter(S => S.fam === a);
    else if (k === "act") mem = M.series.filter(S => S.key === a);
    else if (a === "both") mem = M.series.filter(S => /^適/.test(S.key));
    else mem = M.series.filter(S => S.key === a);
    if (!mem.length) return undefined;     // this table has no such column
    let v = 0;
    for (const S of mem) { const c = S.cells[i]; if (c.ill || c.v == null) return null; v += c.v; }
    return v;
  }
  const startClock = i => { const h = Math.floor((i % 72) / 6), m = (i % 6) * 10; return (h || 12) + ":" + String(m).padStart(2, "0") + (i < 72 ? " a.m." : " p.m."); };
  function keyMoments(t, kd) {
    const M = model(t), n = M.slots.length, out = [];
    const peak = id => { let b = -1, bv = -1; for (let i = 0; i < n; i++) { const v = mval(M, id, i); if (v != null && v > bv) { bv = v; b = i; } } return b < 0 ? null : [b, bv]; };
    if (kd === "act") {
      let wake = null, bed = null, was = null;
      for (let i = 0; i < 72; i++) { const v = mval(M, "fam:sleep", i); if (v == null) continue; if (was != null && was >= 50 && v < 50) { wake = i; break; } was = v; }
      was = null;
      for (let i = 72; i < n; i++) { const v = mval(M, "fam:sleep", i); if (v == null) continue; if (was != null && was < 50 && v >= 50) { bed = i; break; } was = v; }
      if (wake != null) out.push(["Half up by", startClock(wake), "the first slot in which fewer than half are asleep"]);
      if (bed != null) out.push(["Half asleep by", startClock(bed), "the first evening slot in which half or more are asleep"]);
      const w = peak("fam:work"); if (w && w[1] > 0) out.push(["Most at work", startClock(w[0]) + " · " + Math.round(w[1]) + "%", "work, farm work, handwork, piecework and commuting together"]);
      const l = peak("fam:leisure"); if (l && l[1] > 0) out.push(["Most at leisure", startClock(l[0]) + " · " + Math.round(l[1]) + "%", "study, self-improvement, hobbies, entertainment, exercise and socializing together"]);
    } else {
      const f = peak("r:適(甲)"); if (f) out.push(["Most free to listen", startClock(f[0]) + " · " + Math.round(f[1]) + "%", "適(甲): free to listen to the radio"]);
      let best = null, st = null;
      for (let i = 0; i <= n; i++) { const v = i < n ? mval(M, "r:both", i) : null; if (v != null && v >= 50) { if (st == null) st = i; } else if (st != null) { if (!best || i - st > best[1] - best[0]) best = [st, i]; st = null; } }
      if (best) out.push(["Half or more could listen", startClock(best[0]) + " – " + startClock(best[1] % n).replace(/ [ap]\.m\./, "") + (best[1] >= 72 ? " p.m." : " a.m."), "longest run of slots in which 適(甲)+適(乙) is 50% or more"]);
    }
    const o = peak("out"); if (o && o[1] > 0) out.push(["Most outdoors", startClock(o[0]) + " · " + Math.round(o[1]) + "%", "share of persons outside the home (外)"]);
    return out;
  }

  // ---- comparisons: one measure, several related tables ------------------------------------------------------
  function options(t, pool, slug) {
    const d = dims(t, slug), ops = [];
    const P = pool.filter(e => e.d.kd === d.kd);
    const same = (e, ks) => ks.every(k => e.d[k] === d[k]);
    const add = (id, label, lines, how, ref) => { if (lines.length >= 2 && lines.some(e => e.t === t)) ops.push({ id, label, lines, how, ref }); };
    add("age", "By age", P.filter(e => same(e, ["series", "place", "grp", "sex", "slug"]) && (!e.d.mar || e.t === t)).sort((a, b) => ageKey(a.d.age) - ageKey(b.d.age)), "age");
    add("sex", "Men and women", P.filter(e => same(e, ["series", "place", "grp", "age", "mar", "slug"])), "sex");
    add("mar", "Unmarried and married", P.filter(e => same(e, ["series", "place", "grp", "sex", "age", "slug"])), "mar");
    add("grp", "By household type", P.filter(e => same(e, ["series", "place", "sex", "age", "mar", "slug"])), "grp");
    const sers = [...new Set(P.map(e => e.d.series))].filter(x => x && x !== "全國");
    sers.forEach(S => {
      const lines = P.filter(e => e.d.series === S && same(e, ["grp", "sex", "age", "mar", "slug"]));
      const ref = P.find(e => e.d.series === "全國" && same(e, ["grp", "sex", "age", "mar", "slug"]));
      const ls = d.series === "全國" ? lines.concat([{ t, d }]) : lines;
      if (lines.length >= 2) add("ser:" + S, SERN[S] || S, ls, "place", ref && ref.t !== t ? ref : null);
    });
    return ops;
  }
  function lineLabel(e, how) {
    const d = e.d;
    if (how === "age") return (d.age ? d.age : "?") + (d.mar ? " " + MAR[d.mar] : "");
    if (how === "sex") return sexEn(d.sex);
    if (how === "mar") return d.mar ? MAR[d.mar] : "all";
    if (how === "place") return placeEn(d.place);
    if (how === "vol") return GRP[d.grp] || d.grp;
    return GRP[d.grp] || d.grp;
  }
  function lineColors(lines, how, t) {
    const n = lines.length;
    return lines.map((e, k) => {
      if (how === "age") return shade(col(LINE[0]), n > 1 ? 0.72 * (1 - k / (n - 1)) : 0);
      if (how === "place" && e.d.place in REGG) {
        const g = REGG[e.d.place], sib = lines.filter(x => REGG[x.d.place] === g), j = sib.indexOf(e);
        return shade(col(LINE[g]), sib.length > 1 ? j * 0.45 / (sib.length - 1) : 0);
      }
      if (how === "place" && e.d.place === "全國") return "var(--ink)";
      return col(LINE[k % LINE.length]);
    });
  }
  const LOADED = {};
  function loadBook(slug) {
    if (!LOADED[slug]) LOADED[slug] = fetch("../../data/" + slug + ".json").then(r => r.json()).catch(() => []);
    return LOADED[slug];
  }

  function compareView(box, t, kd, ctx) {
    const bar = document.createElement("div"); bar.className = "dc-ctl"; box.appendChild(bar);
    const leg = document.createElement("div"); leg.className = "dc-leg"; box.appendChild(leg);
    const plot = document.createElement("div"); box.appendChild(plot);
    const note = document.createElement("div"); note.className = "dc-note"; box.appendChild(note);
    const tip = document.createElement("div"); tip.className = "dc-tip"; tip.hidden = true; box.appendChild(tip);
    const pool = (ctx.all() || []).filter(u => kind(u) === kd).map(u => ({ t: u, d: dims(u, ctx.slug) }));
    let ops = options(t, pool, ctx.slug);
    const inSeries = SERIES_BOOKS.includes(ctx.slug);
    if (inSeries) ops.push({ id: "vol", label: "Across the four volumes", lines: null, how: "vol" });
    if (!ops.length) { box.innerHTML = `<div class="dc-note">No related tables to compare with.</div>`; return; }
    const ms = measures(kd);
    let op = ops[0], meas = kd === "radio" ? "r:適(甲)" : "fam:sleep";
    const hidden = new Set();
    bar.innerHTML = `<label>Compare <select class="dc-op">${ops.map((o, k) => `<option value="${k}">${esc(o.label)}</option>`).join("")}</select></label>` +
      `<label>Show <select class="dc-ms"></select></label>`;
    const sOp = bar.querySelector(".dc-op"), sMs = bar.querySelector(".dc-ms");
    sOp.onchange = () => { op = ops[+sOp.value]; hidden.clear(); prepare(); };
    sMs.onchange = () => { meas = sMs.value; draw(); };
    let lines = [], colors = [];
    function fillMeasures() {
      const have = ms.filter(([id]) => lines.some(e => { const M = model(e.t); return M.slots.some((_, i) => mval(M, id, i) !== undefined); }));
      sMs.innerHTML = have.map(([id, l]) => `<option value="${id}"${id === meas ? " selected" : ""}>${esc(l)}</option>`).join("");
      if (!have.some(([id]) => id === meas) && have.length) { meas = have[0][0]; sMs.value = meas; }
    }
    function prepare() {
      if (op.how === "vol") {
        plot.innerHTML = `<div class="dc-note">Loading the other volumes…</div>`; leg.innerHTML = "";
        Promise.all(SERIES_BOOKS.map(s => (s === ctx.slug ? Promise.resolve(ctx.all()) : loadBook(s)).then(ts => ({ s, ts })))).then(res => {
          const d = dims(t, ctx.slug), L = [];
          res.forEach(({ s, ts }) => (ts || []).forEach(u => { if (kind(u) !== kd) return; const e = { t: u, d: dims(u, s) };
            if (["series", "place", "sex", "age", "mar"].every(k => e.d[k] === d[k])) L.push(e); }));
          lines = L; colors = lineColors(lines, "vol", t);
          if (lines.length < 2) { plot.innerHTML = `<div class="dc-note">No table with the same group of people (${esc(sexEn(d.sex))} ${esc(ageEn(d.age, d.mar))}, ${esc(placeEn(d.place))}) in the other volumes.</div>`; return; }
          fillMeasures(); draw();
        });
        return;
      }
      lines = op.lines.concat(op.ref ? [op.ref] : []); colors = lineColors(lines, op.how, t);
      if (op.ref) colors[colors.length - 1] = "var(--ink)";
      fillMeasures(); draw();
    }
    function draw() {
      leg.innerHTML = "";
      lines.forEach((e, k) => {
        const b = document.createElement("button"); b.type = "button"; b.className = hidden.has(k) ? "" : "on";
        const lab = (e === op.ref ? "Whole country" : lineLabel(e, op.how)) + (e.t === t ? " ← this table" : "");
        b.innerHTML = `<i style="background:${colors[k]}${e === op.ref ? ";height:3px;border-radius:0" : ""}"></i>${esc(lab)}`;
        b.title = e.t.title + (op.how === "vol" ? " — " + e.d.slug : "");
        b.onclick = () => { if (hidden.has(k)) hidden.delete(k); else hidden.add(k); draw(); };
        leg.appendChild(b);
      });
      plot.innerHTML = "";
      const W = Math.max(320, plot.clientWidth || box.clientWidth || 800), narrow = W < 520;
      const L = narrow ? 30 : 38, R = 8, T = 10, H1 = narrow ? 210 : 260, B = 24, n = 144, pw = W - L - R, sw = pw / n;
      const svg = el("svg", { viewBox: `0 0 ${W} ${T + H1 + B}`, class: "dc-svg", role: "img", "aria-label": "Comparison by time of day" }, plot);
      const series = lines.map((e, k) => { const M = model(e.t); return M.slots.map((_, i) => mval(M, meas, i)); });
      let ymax = 0; series.forEach((v, k) => { if (!hidden.has(k)) v.forEach(x => { if (x != null && x > ymax) ymax = x; }); });
      ymax = Math.max(10, Math.ceil(ymax / 10) * 10);
      const y = v => T + H1 - v / ymax * H1;
      const step = ymax > 50 ? 25 : ymax > 20 ? 10 : 5;
      for (let v = 0; v <= ymax + 0.01; v += step) { el("line", { x1: L, x2: L + pw, y1: y(v), y2: y(v), class: "dc-grid", "stroke-dasharray": v ? "2 3" : "" }, svg); txt(svg, L - 5, y(v) + 4, v + "%", { "text-anchor": "end" }); }
      for (let h = 0; h <= 24; h += 3) { const x = L + h * 6 * sw; el("line", { x1: x, x2: x, y1: T, y2: T + H1, class: "dc-grid", "stroke-dasharray": h % 12 ? "2 3" : "" }, svg);
        const lab = h === 0 || h === 24 ? "midnight" : h === 12 ? "noon" : String(h % 12) + (h < 12 ? " am" : " pm");
        if (!narrow || h % 6 === 0) txt(svg, x, T + H1 + 16, lab, { "text-anchor": h === 0 ? "start" : h === 24 ? "end" : "middle" }); }
      const surf = dark() ? "#1a1a19" : "#fcfcfb";
      const order = lines.map((_, k) => k).sort((a, b) => (lines[a].t === t) - (lines[b].t === t));   // this table on top
      order.forEach(k => {
        if (hidden.has(k)) return;
        const v = series[k]; let d = "", on = false;
        for (let i = 0; i < n; i++) { if (v[i] == null) { on = false; continue; } const x0 = L + i * sw;
          d += (on ? "L" : "M") + x0.toFixed(2) + "," + y(v[i]).toFixed(2) + "L" + (x0 + sw).toFixed(2) + "," + y(v[i]).toFixed(2); on = true; }
        const me = lines[k].t === t;
        if (me) el("path", { d, fill: "none", stroke: surf, "stroke-width": 5.5, "stroke-linejoin": "round" }, svg);
        el("path", { d, fill: "none", stroke: colors[k], "stroke-width": me ? 3 : 1.8, "stroke-linejoin": "round", "stroke-dasharray": lines[k] === op.ref ? "5 4" : "" }, svg);
      });
      const cross = el("line", { x1: 0, x2: 0, y1: T, y2: T + H1, stroke: "var(--ink)", "stroke-width": 1, opacity: 0 }, svg);
      const hit = el("rect", { x: L, y: T, width: pw, height: H1, fill: "transparent" }, svg);
      const ml = (ms.find(m => m[0] === meas) || ["", ""])[1];
      const move = ev => {
        const r = svg.getBoundingClientRect(), sx = (ev.clientX - r.left) * (W / r.width);
        const i = Math.max(0, Math.min(n - 1, Math.floor((sx - L) / sw)));
        cross.setAttribute("x1", L + (i + 0.5) * sw); cross.setAttribute("x2", L + (i + 0.5) * sw); cross.setAttribute("opacity", 0.35);
        const rows = lines.map((e, k) => ({ k, v: series[k][i] })).filter(x => !hidden.has(x.k)).sort((a, b) => (b.v == null ? -1 : b.v) - (a.v == null ? -1 : a.v));
        tip.innerHTML = `<b>${esc(clock(model(t).slots[i]))}</b><div class="n" style="margin:0 0 3px">${esc(ml)}</div>` + rows.map(x => `<div class="r${lines[x.k].t === t ? " f" : ""}"><i style="background:${colors[x.k]}"></i><span>${esc(lines[x.k] === op.ref ? "Whole country" : lineLabel(lines[x.k], op.how))}</span><span>${x.v == null ? '<span class="w">—</span>' : +x.v.toFixed(1) + "%"}</span></div>`).join("");
        tip.hidden = false;
        const br = box.getBoundingClientRect(), tw = tip.offsetWidth, th = tip.offsetHeight;
        let tx = ev.clientX - br.left + 14; if (tx + tw > br.width) tx = ev.clientX - br.left - tw - 14;
        let ty = ev.clientY - br.top - th / 2; ty = Math.max(0, Math.min(ty, br.height - th));
        tip.style.left = Math.max(0, tx) + "px"; tip.style.top = ty + "px";
      };
      hit.addEventListener("pointermove", move); hit.addEventListener("pointerdown", move);
      hit.addEventListener("pointerleave", () => { tip.hidden = true; cross.setAttribute("opacity", 0); });
      const d0 = dims(t, ctx.slug);
      note.textContent = (op.how === "vol" ? `Same group of people (${sexEn(d0.sex)} ${ageEn(d0.age, d0.mar)}, ${placeEn(d0.place)}) in each volume of the survey that prints it. ` : "") +
        "Each line is one printed table; gaps are slots where a figure is unreadable or not printed. Click a name to hide or show its line.";
    }
    prepare();
    let rw = plot.clientWidth;
    if (window.ResizeObserver) new ResizeObserver(() => { if (Math.abs(plot.clientWidth - rw) > 8 && lines.length) { rw = plot.clientWidth; draw(); } }).observe(plot);
  }

  // ---- 24-hour bars (time budgets) ---------------------------------------------------------------------------
  function budget(box, t) {
    const p = t.parts[0];
    const cols = p.columns;
    const ai = cols.map((c, j) => (ACT[c] ? j : -1)).filter(j => j >= 0);
    if (!ai.length) return false;
    const totJ = cols.indexOf("全行爲");
    const ioJ = cols.findIndex(c => /内外/.test(c));
    const labJ = cols.map((c, j) => j).filter(j => j < (totJ >= 0 ? totJ : ai[0]) && j !== ioJ);
    let rows = p.rows.map((r, ri) => ({ r, ri }));
    const hasKei = ioJ >= 0 && rows.some(x => /計/.test(x.r[ioJ]));
    if (hasKei) rows = rows.filter(x => /計/.test(x.r[ioJ]));
    if (!rows.length) return false;
    // carry merged labels down (printed once per group, repeated in the transcription; blanks inherit nothing)
    const lab = x => labJ.map(j => x.r[j]).filter(s => s && s !== "").join(" ");
    const head = document.createElement("div"); head.className = "dc-head"; box.appendChild(head);
    head.innerHTML = `<span class="dc-title">Hours per person per day by activity${hasKei ? " (rows marked 計, indoors + outdoors)" : ""}; each bar is the printed day</span>`;
    const leg = document.createElement("div"); leg.className = "dc-leg"; box.appendChild(leg);
    FAM.forEach(f => { if (!ai.some(j => ACT[cols[j]][0] === f.k)) return; const b = document.createElement("button"); b.type = "button"; b.style.cursor = "default";
      b.innerHTML = `<i style="background:${col(f.c)}"></i>${esc(f.en)} <small>${esc(f.ja)}</small>`; leg.appendChild(b); });
    const plot = document.createElement("div"); box.appendChild(plot);
    const note = document.createElement("div"); note.className = "dc-note"; box.appendChild(note);
    const tip = document.createElement("div"); tip.className = "dc-tip"; tip.hidden = true; box.appendChild(tip);
    let nIll = 0, nTxt = 0;
    const data = rows.map(x => {
      const segs = FAM.map(f => {
        const mem = ai.filter(j => ACT[cols[j]][0] === f.k).map(j => ({ name: cols[j], en: ACT[cols[j]][1], c: dur(x.r[j]) }));
        mem.forEach(m => { if (m.c.ill) nIll++; else if (m.c.txt) nTxt++; });
        return { f, mem, h: mem.reduce((a, m) => a + (m.c.v || 0), 0) };
      }).filter(s => s.mem.length);
      return { label: lab(x), x, segs, tot: totJ >= 0 ? dur(x.r[totJ]) : null, sum: segs.reduce((a, s) => a + s.h, 0) };
    });
    note.textContent = "Bars are built from the printed hours and minutes of each activity; they are not stretched to 24 hours." +
      (nIll ? ` ${nIll} unreadable cell${nIll > 1 ? "s are" : " is"} left out.` : "") + (nTxt ? ` ${nTxt} figure${nTxt > 1 ? "s" : ""} could not be read as a time and ${nTxt > 1 ? "are" : "is"} left out.` : "");
    function draw() {
      plot.innerHTML = "";
      const W = Math.max(320, plot.clientWidth || box.clientWidth || 800), narrow = W < 560;
      const labW = narrow ? 0 : Math.min(W * 0.3, Math.max(...data.map(d => d.label.length * 12)) + 12);
      const L = labW + 6, R = 10, bh = 20, band = bh + (narrow ? 22 : 8), T = 18, H = T + data.length * band + 4;
      const pw = W - L - R, X = h => L + h / 24 * pw;
      const svg = el("svg", { viewBox: `0 0 ${W} ${H}`, class: "dc-svg", role: "img", "aria-label": "Hours per day by activity, " + t.title }, plot);
      for (let h = 0; h <= 24; h += 3) { el("line", { x1: X(h), x2: X(h), y1: T - 4, y2: H, class: "dc-grid", "stroke-dasharray": h % 12 ? "2 3" : "" }, svg); txt(svg, X(h), T - 7, h + "h", { "text-anchor": h === 24 ? "end" : "middle" }); }
      const surf = dark() ? "#1a1a19" : "#fcfcfb";
      data.forEach((d, k) => {
        const y = T + k * band + (narrow ? 16 : 2);
        if (narrow) txt(svg, L, y - 4, d.label, { class: "dc-cap" });
        else txt(svg, L - 6, y + bh / 2 + 4, d.label, { class: "dc-cap", "text-anchor": "end" });
        let a = 0;
        d.segs.forEach(s => {
          if (s.h <= 0) return;
          const x0 = X(a), w = X(a + s.h) - x0;
          el("rect", { x: x0, y, width: Math.max(0.5, w), height: bh, fill: col(s.f.c), stroke: surf, "stroke-width": 1 }, svg);
          const lb = hm(s.h);
          if (w > lb.length * 6.6 + 8) { const t1 = txt(svg, x0 + w / 2, y + bh / 2 + 4, lb, { "text-anchor": "middle", class: "dc-in", style: "fill:#fff" });
            t1.setAttribute("paint-order", "stroke"); t1.setAttribute("stroke", "rgba(0,0,0,.35)"); t1.setAttribute("stroke-width", "2.5"); }
          a += s.h;
        });
        const hit = el("rect", { x: 0, y: y - 2, width: W, height: bh + 4, fill: "transparent" }, svg);
        const show = ev => {
          let h = `<b>${esc(d.label)}</b>`;
          d.segs.forEach(s => { h += `<div class="r f"><i style="background:${col(s.f.c)}"></i><span>${esc(s.f.en)}</span><span>${s.h ? hm(s.h) : ""}</span></div>`;
            s.mem.forEach(m => { h += `<div class="r m"><span>${esc(m.name)} ${esc(m.en)}</span><span>${m.c.ill ? '<span class="w">unreadable</span>' : esc(m.c.s || "—")}</span></div>`; }); });
          h += `<div class="n">Activities add to ${hm(d.sum)}${d.tot && d.tot.s ? `; printed 全行爲 ${esc(d.tot.s)}` : ""}.</div>`;
          tip.innerHTML = h; tip.hidden = false;
          const br = box.getBoundingClientRect(), tw = tip.offsetWidth, th = tip.offsetHeight;
          let tx = ev.clientX - br.left + 14; if (tx + tw > br.width) tx = ev.clientX - br.left - tw - 14;
          let ty = ev.clientY - br.top + 12; if (ty + th > br.height) ty = ev.clientY - br.top - th - 12;
          tip.style.left = Math.max(0, tx) + "px"; tip.style.top = Math.max(0, ty) + "px";
        };
        hit.addEventListener("pointermove", show); hit.addEventListener("pointerdown", show);
        hit.addEventListener("pointerleave", () => { tip.hidden = true; });
      });
    }
    draw();
    let rw = plot.clientWidth;
    if (window.ResizeObserver) new ResizeObserver(() => { if (Math.abs(plot.clientWidth - rw) > 8) { rw = plot.clientWidth; draw(); } }).observe(plot);
    return true;
  }

  // ---- mounting ----------------------------------------------------------------------------------------------
  function mount(box, t, ctx) {
    style();
    const kd = kind(t);
    if (!kd) return false;
    if (kd === "budget") return budget(box, t);
    const tabs = document.createElement("div"); tabs.className = "tc-tabs"; box.appendChild(tabs);
    const day = document.createElement("div"), cmp = document.createElement("div"); cmp.hidden = true;
    box.appendChild(day); box.appendChild(cmp);
    if (!ribbon(day, t, kd)) return false;
    let built = false;
    [["Day", "The whole day, every 10 minutes", day], ["Compare", "One activity across related tables: by age, sex, region, household type or volume", cmp]].forEach(([l, tt, pane], k) => {
      const b = document.createElement("button"); b.type = "button"; b.textContent = l; b.title = tt; if (!k) b.className = "on";
      b.onclick = () => { tabs.querySelectorAll("button").forEach(x => x.classList.toggle("on", x === b)); day.hidden = pane !== day; cmp.hidden = pane !== cmp;
        if (pane === cmp && !built) { built = true; compareView(cmp, t, kd, ctx); } };
      tabs.appendChild(b);
    });
    return true;
  }
  let IO = null;
  function mountAll(root, getTable, getAll) {
    const slug = (location.pathname.match(/\/book\/([^/]+)/) || [])[1] || "";
    const ctx = { all: getAll || (() => []), slug };
    const els = [...(root || document).querySelectorAll(".tday[data-day]:not([data-done])")];
    const go = e => { e.dataset.done = "1"; const t = getTable(e.dataset.day); if (t && !mount(e, t, ctx)) e.classList.add("tc-none"); };
    if (!window.IntersectionObserver) { els.forEach(go); return; }
    if (!IO) IO = new IntersectionObserver(es => es.forEach(x => { if (x.isIntersecting) { IO.unobserve(x.target); go(x.target); } }), { rootMargin: "400px" });
    els.forEach(e => IO.observe(e));
  }
  window.DayChart = { applies, mount, mountAll, _kind: kind, _dur: dur, _model: slotModel, _dims: dims, _options: options, _keys: keyMoments, _mval: mval };
})();
