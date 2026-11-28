"""Write the place-name glossary as a SQLite database (data/place-names.sqlite), for querying and building upon.

Every form is kept: each printed label exactly as printed, with the book and table it comes from (attestations),
the cleaned form and the romanisation system it was sorted into (forms), the name it belongs to (names: present-day,
main, former name or other form) and the place (places). Same-name places in different regions are linked
(namesakes); the same-name checks and the rejected matches are kept too (checks, suspects).

    sqlite3 data/place-names.sqlite "SELECT * FROM v_forms WHERE form = '安東'"
    sqlite3 data/place-names.sqlite "SELECT * FROM v_namesakes"
"""
import datetime, os, sqlite3

SYSTEMS = [("tc", "Chinese characters, traditional", "Hani"), ("sc", "Chinese characters, simplified", "Hani"),
           ("jo", "Japanese, old character forms (kyūjitai)", "Hani"), ("jn", "Japanese, new character forms (shinjitai)", "Hani"),
           ("ko", "Korean (Hangul)", "Hang"), ("py", "Pinyin", "Latn"), ("wg", "Wade-Giles", "Latn"),
           ("oth", "Postal or other romanisation", "Latn"), ("hep", "Hepburn", "Latn"), ("mr", "McCune–Reischauer", "Latn"),
           ("mn", "Mongolian, romanised", "Latn"), ("mns", "Mongolian script", "Mong"), ("std", "Adopted standard form", "Latn")]

SCHEMA = """
CREATE TABLE meta (key TEXT PRIMARY KEY, value TEXT);
CREATE TABLE systems (key TEXT PRIMARY KEY, label TEXT, script TEXT);
CREATE TABLE places (place_id TEXT PRIMARY KEY, heading TEXT, kind TEXT, region TEXT, parent_id TEXT,
  lat REAL, lon REAL, today TEXT, today_hangul TEXT, whg_place_id INTEGER, whg_title TEXT, whg_match TEXT,
  wikipedia TEXT, wikidata TEXT, wikipedia_match TEXT, n_books INTEGER);
CREATE TABLE names (name_id INTEGER PRIMARY KEY, place_id TEXT REFERENCES places, name_key TEXT, status TEXT, note TEXT, seq INTEGER,
  first_year INTEGER, last_year INTEGER);
CREATE TABLE forms (form_id INTEGER PRIMARY KEY, place_id TEXT REFERENCES places, name_id INTEGER REFERENCES names,
  form TEXT, system TEXT REFERENCES systems, attested INTEGER, in_tables INTEGER, sources TEXT, n_books INTEGER,
  first_year INTEGER, last_year INTEGER);
CREATE TABLE attestations (form_id INTEGER REFERENCES forms, kind TEXT, book TEXT, year INTEGER, table_id TEXT, as_printed TEXT, n INTEGER, url TEXT);
CREATE TABLE namesakes (place_id TEXT REFERENCES places, other_place_id TEXT REFERENCES places, name_key TEXT);
CREATE TABLE checks (outcome TEXT, place_id TEXT, moved_to TEXT, as_printed TEXT, book TEXT, table_id TEXT, table_region TEXT, n INTEGER);
CREATE TABLE suspects (place_id TEXT, heading TEXT, as_printed TEXT, book TEXT, n INTEGER);
CREATE INDEX forms_form ON forms(form);
CREATE INDEX forms_place ON forms(place_id);
CREATE INDEX att_form ON attestations(form_id);
CREATE VIEW v_forms AS
  SELECT f.form, s.label AS system, n.status, n.note, p.heading, p.kind, p.region, p.place_id, f.attested, f.in_tables, f.sources, f.n_books
  FROM forms f JOIN systems s ON s.key = f.system JOIN names n ON n.name_id = f.name_id JOIN places p ON p.place_id = f.place_id;
CREATE VIEW v_namesakes AS
  SELECT ns.name_key, a.heading, a.region, a.place_id, b.heading AS other_heading, b.region AS other_region, b.place_id AS other_place_id
  FROM namesakes ns JOIN places a ON a.place_id = ns.place_id JOIN places b ON b.place_id = ns.other_place_id;
"""


def write(entries, db_forms, checks, suspects, path, books=None):
    books = books or {}
    tmp = path + ".tmp"
    if os.path.exists(tmp):
        os.replace(tmp, tmp + ".old")       # never left behind by a normal run; replaced, not deleted
    con = sqlite3.connect(tmp)
    con.executescript(SCHEMA)
    con.executemany("INSERT INTO meta VALUES (?,?)", [
        ("doc", __doc__.split("\n\n")[0]),
        ("rule", "in_tables = 1: printed in a table of our books. attested = 1: printed in a table or used in our English "
                 "translations. attested = 0: added on request (2026-11-28) and marked 'added: …' in sources: Hangul, "
                 "McCune–Reischauer and Hepburn from reference data, pinyin of Chinese names with an unambiguous reading, and names from the lead infoboxes of English Wikipedia articles (article checked by coordinates or by the map's own link)."),
        ("built", datetime.date.today().isoformat()),
        ("site", "https://froginawell.net/reference/old-tables/places.html")])
    con.executemany("INSERT INTO systems VALUES (?,?,?)", SYSTEMS)
    name_id = {}
    nid = 0
    for e in entries:
        ll = e.get("ll") or [None, None]
        w = e.get("whg") or {}
        wp = e.get("wp") or {}
        con.execute("INSERT INTO places VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                    (e["id"], e["en"], e["k"], e["r"], e.get("up") or None, ll[0], ll[1], e.get("today"), e.get("today_ko"),
                     w.get("pid"), w.get("title"), w.get("how"), wp.get("title"), wp.get("qid"), wp.get("how"), e["nb"]))
        for seq, r in enumerate(e["rows"]):
            nid += 1
            name_id[(e["id"], r["core"])] = nid
            y = r.get("yrs") or [None, None]
            con.execute("INSERT INTO names VALUES (?,?,?,?,?,?,?,?)", (nid, e["id"], r["core"], r["status"], r["note"] or None, seq, y[0], y[1]))
        for s in e.get("same", []):
            con.execute("INSERT INTO namesakes VALUES (?,?,?)", (e["id"], s["id"], s["cjk"]))
    fid = 0
    for pid, c, form, col, info in db_forms:
        n = name_id.get((pid, c))
        if n is None:
            n = next((v for (p, cc), v in name_id.items() if p == pid), None)
        fid += 1
        added = any(str(s).startswith("added") for s in info["src"])
        ys = [books.get(b, {}).get("year") for (kind, b, _t, _l) in info["prov"] if kind in ("table", "translation")]
        ys = [y for y in ys if isinstance(y, int)]
        con.execute("INSERT INTO forms VALUES (?,?,?,?,?,?,?,?,?,?,?)",
                    (fid, pid, n, form, col, 0 if added else 1, 1 if "table" in info["src"] else 0,
                     ", ".join(sorted(info["src"])), len(info["books"]), min(ys) if ys else None, max(ys) if ys else None))
        for (kind, book, tid, label), k in sorted(info["prov"].items()):
            url = f"book/{book}/#{tid}" if kind in ("table", "translation") else None
            con.execute("INSERT INTO attestations VALUES (?,?,?,?,?,?,?,?)",
                        (fid, kind, book, books.get(book, {}).get("year"), tid, label, k, url))
    con.executemany("INSERT INTO checks VALUES (?,?,?,?,?,?,?,?)", [k + (n,) for k, n in sorted(checks.items())])
    con.executemany("INSERT INTO suspects VALUES (?,?,?,?,?)", [k + (n,) for k, n in sorted(suspects.items())])
    con.commit()
    con.execute("VACUUM")
    con.close()
    os.replace(tmp, path)
