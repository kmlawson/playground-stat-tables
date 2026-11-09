"""Population figures out of the transcribed tables, read by the specs in build/finders/population/specs/ (TASK.md).

Every figure comes from a cell of a table in data/<slug>.json, exactly as transcribed: nothing is read again, filled,
smoothed or corrected. A cell that is empty, "[?]", a dash, a ditto mark or not a plain number gives no claim.

claims(): list of dicts {place (id), label, date, year, approx, m, g, b, n, v, src (slug:id), part, row, col}
and the places made up on the way (labels the gazetteer does not know), and the labels that were not placed.
"""
import json, os, re, sys, unicodedata
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
from finderlib import *  # noqa: E402,F401,F403
from finderlib import _resolve  # noqa: E402,F401


FDIR = os.path.dirname(os.path.abspath(__file__))     # build/finders/population (finderlib's HERE is build/finders)


def load_specs():
    return L.load_specs(FDIR)


import finderlib as L  # noqa: E402

CITYRX = re.compile(r"市|都市|區|\bcity\b|\bcities\b|municipal|\bwards?\b|\btowns?\b", re.I)
GROUPS = {"all", "japanese", "korean", "chinese", "taiwanese", "aborigine", "islander", "ainu", "manchu", "mongol", "foreign"}


def claims(specs, editions):
    out, made, unplaced, problems = [], {}, Counter(), Counter()
    for key, s in specs.items():
        if "x" not in s:
            continue
        slug, tid = key.split(":", 1)
        t = table(slug, tid)
        if not t:
            problems["no table " + key] += 1
            continue
        ed = editions.get(slug)
        for x in s["x"]:
            try:
                part = (t.get("parts") or [])[int(x.get("part", 0))]
            except (IndexError, ValueError, TypeError):
                problems["no part " + key] += 1
                continue
            rows = part.get("rows") or []
            mult = x.get("mult") or 1
            base = {"m": x.get("m", "total"), "g": (x.get("g") or "all").lower(), "b": x.get("b"), "n": x.get("n")}
            within = x.get("in")
            wid = ctx_id(within) if within else None
            pt = x.get("pt")
            rp = {str(k): v for k, v in (x.get("rp") or {}).items()}
            rdd = {str(k): v for k, v in (x.get("rd") or {}).items()}
            only = set(x.get("only") or []) or None
            lc = int(x.get("lc", 0))
            mode = x.get("rows", "places")
            cityish = bool(CITYRX.search(" ".join(str(z or "") for z in (t.get("title"), t.get("chapter"), t.get("caption_extra"), x.get("n"), part.get("label")))))

            def emit(place_label, by_agent, date, r, c, col):
                cell = rows[r][c] if r < len(rows) and c < len(rows[r]) else None
                v = number(cell, col.get("mult", mult))
                if v is None:
                    return
                lab = place_label
                if lab is None or str(lab).strip() in ("", "-"):
                    return
                if by_agent:
                    # the stated kind first; a ward or town named by the agent never falls back to a wider match
                    # ('東區 (Nagoya)' is not Nagoya), except for the standard names of whole units
                    # Tokyo, Ōsaka, Kyōto … name a city and a prefecture: a table about a city (its title, chapter,
                    # caption or note says 市 / city / ward) means the city
                    ept = pt or ("city" if cityish and IX["cities"].get(F.city(str(lab)))
                                 and not re.search(r"府|縣|県|道|-fu\b|-ken\b|prefecture", str(lab), re.I) else None)
                    pid, how = resolve(lab, ept, within) if ept else (None, None)
                    if not pid and pt in ("ward", "district", "town", "city"):
                        pid = IX["top"].get(F.prov(str(lab))) or IX["top"].get(F.base(str(lab)))
                        how = "top" if pid else None
                    elif not pid:
                        pid, how = resolve(lab, None, within)
                else:
                    if TOTALRX.match(unicodedata.normalize("NFKC", str(lab)).strip()):
                        if pt in ("prefecture", "province", "island", "colony") and wid:
                            pid, how = wid, "total"
                        else:
                            return
                    else:
                        pid, how = resolve(lab, pt, within)
                if pid == "-":
                    return
                if not pid:
                    unplaced[(str(lab).strip(), pt or "", within or "", region_key(within))] += 1
                    pid = custom_place(lab, pt, wid, made)
                if not date:
                    problems["no date " + key] += 1
                    return
                g = (col.get("g") or base["g"] or "all").lower()
                out.append({"place": pid, "label": str(lab).strip(), "date": date[0], "year": date[1], "approx": date[2],
                            "m": col.get("m") or base["m"], "g": g, "b": col.get("b") or base["b"], "n": col.get("n") or base["n"],
                            "v": v, "src": key, "part": int(x.get("part", 0)), "row": r, "col": c, "cell": rows[r][c],
                            "mult": col.get("mult", mult)})

            cols = x.get("cols") or []
            if mode == "cells":
                for cl in x.get("cells") or []:
                    try:
                        d = norm_date(cl.get("d") or x.get("d"), ed)
                        emit(cl.get("p") or x.get("p"), True, d, int(cl["r"]), int(cl["c"]), cl)
                    except (KeyError, ValueError, TypeError):
                        problems["bad cell " + key] += 1
                continue
            if not cols:
                ncol = max((len(r) for r in rows), default=0)
                if ncol == 2:
                    cols = [{"c": 1 - lc}]
                else:
                    problems["no cols " + key] += 1
                    continue
            prev = None
            for r, row in enumerate(rows):
                if only and r not in only:
                    continue
                if str(r) in rp and rp[str(r)] in ("-", "", None):
                    continue
                lab = row[lc] if lc < len(row) else None
                if mode == "dates":
                    if str(r) in rdd:
                        d = norm_date(rdd[str(r)], ed)
                    else:
                        d = date_of(lab, prev)
                    prev = d
                    if not d:
                        continue
                    for col in cols:
                        emit(col.get("p") or rp.get(str(r)) or x.get("p"), True, d, r, int(col["c"]), col)
                else:
                    for col in cols:
                        d = norm_date(col.get("d") or x.get("d"), ed)
                        if str(r) in rp:
                            emit(rp[str(r)], True, d, r, int(col["c"]), col)
                        else:
                            emit(lab, False, d, r, int(col["c"]), col)
    move(out, problems)
    return out, made, unplaced, problems


def move(out, problems):
    """place_moves.json: figures a spec puts at one place that belong to another (Kwantung printed together with the
    Railway Zone), moved by table and year range. A move that matches nothing is reported as a problem."""
    p = os.path.join(FDIR, "place_moves.json")
    if not os.path.exists(p):
        return
    for mv in json.load(open(p)).get("moves", []):
        y0, y1, n = mv.get("from_year", 0), mv.get("until", 9999), 0
        for c in out:
            if c["src"] == mv["t"] and c["place"] == mv["from"] and y0 <= c["year"] <= y1:
                c["place"] = mv["to"]
                n += 1
        if not n:
            problems["place move matched nothing " + mv["t"]] += 1
