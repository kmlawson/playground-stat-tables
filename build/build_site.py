#!/usr/bin/env python3
"""Build the stat-tables site: a landing page plus one table browser per book.

For each book in BOOKS, reads <book dir>/_work/tables/*.json and writes
<slug>/index.html (self-contained) and data/<slug>.json. Books without tables yet are listed
as "in progress" on the landing page. Scan links point to the online scan where one exists.
"""
import json, glob, os, re, html

SCRIPTS = os.path.dirname(os.path.abspath(__file__))  # build/: scripts, leaf maps, docs (not deployed)
HERE = os.path.dirname(SCRIPTS)  # site root: everything here except build/, CLAUDE.md and .git is deployed
# Folder holding the book folders. A worktree placed elsewhere (e.g. the far-east-1941 branch)
# must set STAT_TABLES_ROOT to the Manchoukuo folder, or relative book dirs resolve wrongly.
ROOT = os.environ.get("STAT_TABLES_ROOT") or os.path.dirname(HERE)

BOOKS = [
    {"slug": "japan-1905", "dir": "Japan_Year_Book_1905", "title": "The Japan Year Book 1905",
     "publisher": "The \"Japan Year Book\" Office, Tokyo, 1905",
     "blurb": "The first edition of The Japan Year Book, compiled during the Russo-Japanese War: geography, population, the Imperial Court, politics, finance, banking, industry, trade, education, the army and navy, communications, a Who's Who (\"Contemporary Worthies\"), diplomacy, the press, Formosa, Korea, and an appended import tariff.",
     "source": "LLM-transcribed from the Internet Archive scan (Google scan of a New York Public Library copy).",
     "gaps": "The dated narrative of the \"Progress of the War\" chapter (pp. 315-347) was transcribed separately and is not included; the statistical tables printed in that chapter (spoils, prisoners, warships lost) are. Advertisements, the contents and the Index were skipped, as were law and treaty texts. The Import Tariff List in the Appendix is given one table per page. The \"Contemporary Worthies\" Who's Who, the Imperial family and the steamship-company sketches are on the Who's Who & Directories page.",
     "scan": "https://archive.org/details/japan-year-book-1905/page/n{leaf}/mode/1up",
     "item": "https://archive.org/details/japan-year-book-1905"},
    {"slug": "japan-1910", "dir": "Japan_Year_Book_1910", "title": "The Japan Year Book 1910",
     "publisher": "The Japan Year Book Office, Tokyo, 1910",
     "blurb": "The fifth annual edition, compiled by Y. Takenob and K. Kawakami: geography, population, the Imperial Court, a Who's Who, arts and crafts, education, religion, justice, agriculture, mining, industry, finance, diplomacy, politics, trade, banking, the army and navy, communications, shipping, railways, the press, Formosa, Karafuto, South Manchuria and Korea.",
     "source": "LLM-transcribed from the Internet Archive scan (Google scan of the 2013 Edition Synapse facsimile, University of Minnesota copy).",
     "gaps": "The scan is low resolution, so more figures are left blank than in later volumes; each blank is explained in a transcriber's note. Advertisements, the contents and the Index were skipped. The Who's Who, the Imperial family and the art and pottery sketches are on the Who's Who & Directories page; the Diary of 1908-9 is on the Chronologies page. Treaty texts and law articles are not transcribed.",
     "scan": "https://archive.org/details/japan-year-book-1910/page/n{leaf}/mode/1up",
     "item": "https://archive.org/details/japan-year-book-1910"},
    {"slug": "japan-1920-21", "dir": "Japan_Year_Book_1920", "title": "The Japan Year Book 1920-21",
     "publisher": "The Japan Year Book Office, Tokyo, 1920",
     "blurb": "The fifteenth annual edition: geography, history, population, the Imperial Court, a Who's Who, education, labour, communications, railways, shipping, banking, the army and navy, diplomacy, trade, agriculture, industry, finance, politics, the colonies, and a business directory.",
     "source": "LLM-transcribed from the Internet Archive scan (Google scan of a University of California copy).",
     "gaps": "Advertisements, the contents pages and the Index contain no tables and were skipped. The Who's Who, Business Directory, Learned & Social Institutions and the Imperial family and charity institutions are on the Who's Who & Directories page; the Diary, Obituary and chronological lists are on the Chronologies page. On printed p. 171 of the Who's Who an entry begins mid-text: its heading was never printed, so the surviving text is recorded in a note, not as an entry.",
     "scan": "https://archive.org/details/japan-year-book-1920/page/n{leaf}/mode/1up",
     "item": "https://archive.org/details/japan-year-book-1920"},
    {"slug": "japan-1930", "dir": "Japan_Year_Book_1930", "title": "The Japan Year Book 1930",
     "publisher": "The Japan Year Book Office, Tokyo, 1930",
     "blurb": "Comprehensive English-language reference on the Japanese Empire in 1930, covering geography, population, government, defence, education, labour, justice, communications, railways, shipping, banking, finance, agriculture, industry, trade, the six premier cities and the colonies.",
     "source": "LLM-transcribed from the Internet Archive scan.",
     "gaps": "Advertisements and the Index contain no tables. The Who's Who, Business Directory and Learned & Social Institutions (Appendices A–C) are transcribed as entries on the Who's Who & Directories page. The shop and restaurant lists in Appendix D are included; the physicians' lists are not. On p. 439 the right edge of the scan cuts off the 1927 export figures, so those cells are blank.",
     "scan": "https://archive.org/details/japan-year-book-1930/page/n{leaf}/mode/1up",
     "item": "https://archive.org/details/japan-year-book-1930"},
    {"slug": "japan-1935", "dir": "Japan_Year_Book_1935", "title": "The Japan Year Book 1935",
     "publisher": "K. Inahara, ed.; Tokyo: The Foreign Affairs Association of Japan, 1935",
     "blurb": "English-language annual on the Japanese Empire in 1935, covering geography, population, government, defence, finance, banking, trade, agriculture, industry, communications, social affairs, education, the colonies and Manchoukuo.",
     "source": "LLM-transcribed from the Internet Archive scan.",
     "gaps": "Only tables and lists are transcribed; prose, the Chronicle of Important Events, the Chronological Index and the Calendar of Annual Events are not. Printed pp. 81 and 683 are missing from the scan (repeat scans of other pages were skipped). The heavy bold type makes 3 and 8 hard to tell apart: such digits are blank unless a printed total settles them, so many cells are empty. The List of Clubs, Societies and Associations is on the Directories page.",
     "scan": "https://archive.org/details/japan-year-book-1935/page/n{leaf}/mode/1up",
     "item": "https://archive.org/details/japan-year-book-1935"},
    {"slug": "japan-1939-40", "dir": "Japan_Year_Book_1939-40", "title": "The Japan Year Book 1939-40",
     "publisher": "The Foreign Affairs Association of Japan, Tokyo, 1939",
     "blurb": "The wartime edition of the standard English-language reference on the Japanese Empire.",
     "source": "LLM-transcribed from the Internet Archive scan.",
     "gaps": "The Internet Archive scan often repeats a leaf in place of the next one, so about 90 printed pages are missing, among them pp. 273–274, 277–278, 283–284 (part of the 1937-38 budget and Banking Tables 1–3), 380–381 (Balance of International Payments), 778–779, 784, 787–788, 793, 796–797, 802–803, 808, 811, 814, 817, 820–821, 825, 830–832, 843–844, 847, 850, 853–854, 861, 866, 869, 873, 876, 879, 886, 888, 893, 896–897, 901, 904, 908–909, 912, 918–919, 928–929, 934, 937, 940–941, 947–948, 951–952 (including the opening of the Karafuto chapter), 956, 959, 962–963, 967, 970–971, 1023, 1026–1027, 1033–1034, 1039, 1123, 1130, 1135–1137 and 1142. Tables that run onto a missing page are incomplete and say so. Page 363 is heavily over-inked, leaving about 90 blank cells in the census table there. Lists are included as well as tables; the Clubs & Societies list is on the directory page. The bibliography, index and advertisements are not transcribed.",
     "scan": "https://archive.org/details/japan-year-book-1939-1940/page/n{leaf}/mode/1up",
     "item": "https://archive.org/details/japan-year-book-1939-1940", "dir_label": "Clubs & Societies Directory"},
    {"slug": "japan-1946-48", "dir": "Japan_Year_Book_1946-48", "title": "The Japan Year Book 1946-48",
     "publisher": "The Foreign Affairs Association of Japan (no place or date on the title page)",
     "blurb": "The first post-war edition, covering occupied Japan.",
     "source": "LLM-transcribed from the Internet Archive scan.",
     "gaps": "The scan is complete: no printed pages are missing and no leaves repeat. Part I runs to p. 614; the Appendix (SCAP directives, the new Constitution and post-war laws, documents of 1945–47, the war-crimes indictment and a List of Emperors) is paged again from 1. The Appendix is almost all legal text, so only its lists are transcribed. A few cells on folding inserts are lost in the fold and are left blank. The index, advertisements and a short run of church-group entries (printed pp. 489–490) are not transcribed.",
     "scan": "https://archive.org/details/japan-year-book-1946-1948/page/n{leaf}/mode/1up",
     "item": "https://archive.org/details/japan-year-book-1946-1948"},
    {"slug": "korea-1929-30", "dir": "Korea_Annual_Report_1929-30",
     "title": "Annual Report on Administration of Chosen 1929-30",
     "publisher": "Government-General of Chosen, Keijo, 1931",
     "blurb": "The Government-General's English-language annual report on colonial Korea: population, finance, banking, trade, education, industry, communications, police, public health and local administration.",
     "source": "LLM-transcribed from the Internet Archive scan.",
     "gaps": "The Internet Archive scan is missing the text page beside each photo plate (printed pp. 66, 74, 82, 92, 96, 100, 104, 140, 152 and 172), as well as the appendix tables of weights and measures and of governors. On p. 13 the Total column is in a different typeface from the rest of the table, which may mean the scan was retouched.",
     "scan": "https://archive.org/details/annualreportonreformsandprogressinchosenkorea192930/page/n{leaf}/mode/1up",
     "item": "https://archive.org/details/annualreportonreformsandprogressinchosenkorea192930"},
    {"slug": "manchoukuo-1942", "dir": ".", "title": "The Manchoukuo Year Book 1942",
     "publisher": "Manchoukuo Year Book Co., Hsinking, 1942",
     "blurb": "Official English-language yearbook of Manchukuo: geography, population, finance, banking, trade, agriculture, mining, industry, transport, labour, education and more.",
     "source": "LLM-transcribed from 498 photographs of the printed volume (two-page spreads).",
     "gaps": "The online Internet Archive copy is the same set of photographs, cropped and in greyscale, so the scan links open the same spread. Pages 502–503 (Mining) and 966–967 (Index) were not photographed. Gaps in table numbering (e.g. Agriculture Tables 2–3 and 11–17) are in the printed book itself.",
     "scan": "https://archive.org/details/manchoukuo-yearbook-1942/page/n{leaf}/mode/1up",
     "item": "https://archive.org/details/manchoukuo-yearbook-1942"},
    {"slug": "far-east-1941", "root": os.environ.get("FAR_EAST_ROOT") or os.path.join(os.path.dirname(ROOT), "The Far East Year Book 1941"),
     "title": "The Far East Year Book 1941",
     "publisher": "Japan-Manchoukuo Year Book Co., Tokyo, 1941",
     "blurb": "Japan, its colonies (Chosen, Taiwan, Karafuto, the South Sea Islands), Manchoukuo and occupied China, with shorter sections on the Philippines, French Indo-China, Thailand, British Malaya, the Netherlands East Indies and British Borneo.",
     "source": "LLM-transcribed from 581 photographs of the printed volume (two-page spreads).",
     "gaps": "Printed pp. 394–395 (Japan, Chemical and Ceramic Industries; Chemical Tables 11–16) were not photographed. One spread (pp. 1118–1119) was photographed twice; the duplicate is ignored. Numbering gaps are in the printed book: Arts and Crafts cites Tables 6–8 but prints only 1–7, and Japan Labor has no Table 11 and two Tables 15. The National Defence Army Districts table is printed in two places (pp. 101 and 111) and is merged here. Maps, charts without figures and running prose are not transcribed. The China railways descriptions and similar name-and-paragraph lists are on the Who's Who & Directories page. Many printed totals do not add up; the figures are kept as printed and each table's notes say where.",
     "scan": "https://archive.org/details/far-east-year-book-1941/{partname}/page/n{leaf}/mode/1up",
     "scan_parts": {1: "Far%20East%20Year%20Book%201941%20Part%201%20Japan", 2: "Far%20East%20Year%20Book%201941%20Part%202"},
     "item": "https://archive.org/details/far-east-year-book-1941"},
    {"slug": "china-1912", "dir": "China_Year_Book_1912", "title": "The China Year Book 1912",
     "publisher": "H. T. Montague Bell and H. G. W. Woodhead (eds.); London: George Routledge & Sons; New York: E. P. Dutton & Co.",
     "blurb": "The first edition of the English-language reference book on China, compiled during the 1911 Revolution.",
     "source": "LLM-transcribed from a scan of the printed volume.",
     "gaps": "Transcribed from a Google scan of the University of Minnesota copy. The scan repeats a run of pages (PDF pages 349–382 duplicate earlier ones); no printed pages are missing. Numbered legal clauses (the Constitution, court and loan regulations, opium agreements) are prose and not transcribed. The mines and companies, the per-railway 'Further Details' and the Government Institutions at Peking are on the Who's Who & Directories page. Many printed totals do not add up; the figures are kept as printed and each table's notes say where.",
     "scan": "https://archive.org/details/china-year-book-1912/page/n{leaf}/mode/1up",
     "item": "https://archive.org/details/china-year-book-1912"},
    {"slug": "china-1922", "dir": "China_Year_Book_1922", "title": "The China Year Book 1921-2",
     "publisher": "H. G. W. Woodhead (ed.), H. T. Montague Bell (assoc. ed.); Tientsin: Tientsin Press",
     "blurb": "The Peking-government-era edition of the English-language reference book on China, covering population, geography, trade, finance, loans, currency, communications, defence, education, Greater China, opium, the customs tariff, the government and a Who's Who.",
     "source": "LLM-transcribed from the Internet Archive scan (University of Toronto copy).",
     "gaps": "No printed pages are missing from the scan. On p. 482 (Postal Statistics, Appendix 2) the Total row runs off the bottom edge of the scan, so its cells are blank. The fold-out on p. 992a (Maritime Customs Revenue of Each Port, 1920) is included. The warship list is printed across facing pages (pp. 542–545) and its two halves were joined line by line. Six tables that run across pages were transcribed with different column layouts on each side and are kept as separate parts (General Loans, pp. 258–263; Treaty Ports, pp. 219–220; Ministry of Foreign Affairs and Legations abroad, pp. 859–863; Salt Revenue staff, pp. 874–875; British Chambers of Commerce, pp. 970–971). Legal texts (the Provisional Criminal Code, treaties, agreements) are transcribed only where they contain tables or lists. The Contents, Index, advertisements and the folding map are not transcribed. The Who's Who, the List of Factories using Foreign Machinery and the Foreign Banks with Branches in China are on the Who's Who & Directories page. Many printed totals do not add up; the figures are kept as printed and each table's notes say where. The tables were read once; they have not been double-checked by a second reading.",
     "scan": "https://archive.org/details/chinayearbook1922shan/page/n{leaf}/mode/1up",
     "item": "https://archive.org/details/chinayearbook1922shan"},
    {"slug": "china-1929-30", "dir": "China_Year_Book_1929-30", "title": "The China Year Book 1929-30",
     "publisher": "H. G. W. Woodhead (ed.); Tientsin: The Tientsin Press",
     "blurb": "The Nationalist-era edition of the English-language reference book on China.",
     "source": "LLM-transcribed from a scan of the printed volume.",
     "gaps": "The scan's page order is scrambled in places (parts of the Who's Who and of Chapter III are bound out of sequence); tables are filed under their printed pages. The first sheet of the fold-out on p. 658 (railway-secured foreign loans) is missing from the scan, so that table starts at sheet 658 b. On Who's Who p. 998 a strip near the right margin is missing from the scan, leaving gaps marked [illegible]. Treaty texts, laws and regulations are transcribed only where they contain tables or lists; numbered articles are prose. The Contents, indexes and advertisements are not transcribed. The Chinese Who's Who (pp. 919–1002) is on the Who's Who page. Many printed totals do not add up; the figures are kept as printed and each table's notes say where.",
     "scan": "https://archive.org/details/china-year-book-1929-30/page/n{leaf}/mode/1up",
     "item": "https://archive.org/details/china-year-book-1929-30"},
    {"slug": "china-1938", "dir": "China_Year_Book_1938", "title": "The China Year Book 1938",
     "publisher": "H. G. W. Woodhead (ed.); Shanghai: North-China Daily News & Herald, 1938",
     "blurb": "The wartime edition of the English-language reference book on China, compiled as the Sino-Japanese war began.",
     "source": "LLM-transcribed from a scan of the printed volume.",
     "gaps": "The Internet Archive copy is borrow-only: the scan links open the right page only while you have the book checked out there. No printed pages are missing from the scan. The Calendar for 1938 is transcribed month by month. The Chinese Who's Who (pp. 142–191) is on the Who's Who page; the 1937 summary of Sino-Japanese hostilities and the 1937 fires are on the Chronologies page. Laws, treaties, regulations and diplomatic documents are transcribed only where they contain tables or lists; numbered articles are prose. The Contents, indexes and advertisements are not transcribed. Very long tables (the Import Tariff, the railway obligations) are split into one table per printed page. Many printed totals do not add up; the figures are kept as printed and each table's notes say where.",
     "scan": "https://archive.org/details/chinayearbook1930000hgww/page/n{leaf}/mode/1up",
     "item": "https://archive.org/details/chinayearbook1930000hgww"},
    {"slug": "china-1937-43", "dir": "China_Handbook_1937-1943", "title": "China Handbook 1937-1943",
     "publisher": "Chinese Ministry of Information; New York: Macmillan, 1943",
     "blurb": "The Chinese government's wartime reference book on Free China, 1937-1943.",
     "source": "LLM-transcribed from the Internet Archive scan (five parts, two-page spreads).",
     "gaps": "The scan is missing printed pp. 444–445 (so Industry and Labor Table 18 is lost) and pp. lii–liii of the Chinese Who's Who. The legal texts (constitutions, laws, regulations) are transcribed only where they contain tables or lists; numbered articles are prose. The book's Contents, Index and folding map of China are not transcribed. The Associations and Societies chapter and the Chinese Who's Who are on the Who's Who & Directories page; the Kuomintang chronology and the Chronology of Major Events, 1937–1943, are on the Chronologies page. Many printed totals do not add up; the figures are kept as printed and each table's notes say where.",
     "scan": "https://archive.org/details/china-handbook-1937-1943/China%20Handbook%201937-1943%20Part%20{part}%20of%205/page/n{leaf}/mode/1up",
     "item": "https://archive.org/details/china-handbook-1937-1943"},
    {"slug": "china-1950", "dir": "China_Handbook_1950",
     "root": os.environ.get("CHINA_1950_ROOT"),
     "title": "China Handbook 1950",
     "publisher": "China Handbook Editorial Board; New York: Rockport Press, 1950",
     "blurb": "The Nationalist government's reference book compiled after its retreat to Taiwan: geography, the provinces, history and a chronology to 1949, government, defence, parties, foreign affairs, the economy, communications, education, health, relief and a Who's Who.",
     "source": "LLM-transcribed from the Internet Archive scan (three parts, two-page spreads).",
     "gaps": "The scan is complete: every printed page from the front matter to p. 786 is present. The contents pages and the index (pp. 787–799) are not transcribed, and neither are running prose, maps and charts without figures. Treaties, agreements, laws, constitutions and statements (much of chapters 6–13, 27 and 31) are prose; only tables and lists printed inside them are transcribed. Each province's summary block (area, population, hsien, capital) in chapter 2 is given as a small table. The Who's Who (chapter 36) is on the Who's Who & Directories page and the Chronology of Major Events, 1911–1949 (chapter 5), on the Chronologies page. Many figures in the tables are printed out of line with their row labels; they were matched by counting, and each table's notes say where. Many printed totals do not add up; the figures are kept as printed and each table's notes say where.",
     "scan": "https://archive.org/details/china-handbook-1950/China%20Handbook%201950%20Part%20{part}%20of%203/page/n{leaf}/mode/1up",
     "item": "https://archive.org/details/china-handbook-1950"},
]


def dl(slug, suffix):
    """Relative path of a download written by build_downloads.py, or None if it hasn't been built."""
    f = f"downloads/{slug}-{suffix}"
    return f if os.path.exists(os.path.join(HERE, f)) else None


def book_dir(book):
    """Books live beside this repo's parent folder, or at an explicit absolute path ("root")."""
    return book.get("root") or os.path.join(ROOT, book["dir"])


def page_key(t):
    m = re.match(r"p(\d)-(\d+)", t["file"]) or re.search(r"(\d+)", t["file"])  # multi-part scans: p{part}-{leaf}
    img = int(m.group(1)) * 10000 + int(m.group(2)) if m and m.lastindex == 2 else (int(m.group(1)) if m else 0)
    n = int(re.search(r"_(\d+)\.json$", t["file"]).group(1))
    return (img, n)


def load(book):
    tables = []
    for f in sorted(glob.glob(os.path.join(book_dir(book), "_work", "tables", "*.json"))):
        try:  # agents may be writing or merging files while we build
            with open(f, encoding="utf-8") as fh:
                t = json.load(fh)
        except (FileNotFoundError, json.JSONDecodeError):
            print("skipped", f)
            continue
        t["file"] = os.path.basename(f)
        t["id"] = t["file"][:-5]
        tables.append(t)
    tables.sort(key=page_key)
    return tables


_LEAFMAPS = {}


def leafmap(book):
    """Optional leafmaps/<slug>.json: {"IMG_5451": 10, ...} or {"IMG_4814": [part, leaf], ...} for books transcribed from photos whose online scan is numbered differently."""
    if book["slug"] not in _LEAFMAPS:
        f = os.path.join(SCRIPTS, "leafmaps", book["slug"] + ".json")
        _LEAFMAPS[book["slug"]] = json.load(open(f, encoding="utf-8")) if os.path.exists(f) else None
    return _LEAFMAPS[book["slug"]]


def scan_links(book, t):
    ims = t.get("images") or [t.get("image")]
    out = []
    for im in ims:
        mp = re.match(r"p(\d)-(\d+)$", im or "")  # multi-part scans: one IA file per part
        if book["scan"] and mp:
            part, leaf = int(mp.group(1)), int(mp.group(2))
            out.append({"label": f"scan part {part}, leaf {leaf}", "url": book["scan"].format(part=part, leaf=leaf)})
            continue
        lm = leafmap(book)
        if book["scan"] and lm is not None and im in lm:  # photo names mapped to the online scan's leaves
            if lm[im] is None:
                pp = t.get("printed_pages") or []  # not in the online scan: show only the printed pages
                out.append({"label": ("pp. " if len(pp) > 1 else "p. ") + "–".join([pp[0], pp[-1]] if len(pp) > 1 else pp), "url": None})
            elif isinstance(lm[im], list):  # [part, leaf] for a scan split into several files
                part, leaf = lm[im]
                out.append({"label": f"scan part {part}, leaf {leaf}", "url": book["scan"].format(partname=book["scan_parts"][part], leaf=leaf)})
            else:
                out.append({"label": f"scan leaf {lm[im]}", "url": book["scan"].format(leaf=lm[im])})
            continue
        m = re.match(r"p(\d+)$", im or "")
        if book["scan"] and m:
            out.append({"label": f"scan leaf {int(m.group(1))}", "url": book["scan"].format(leaf=int(m.group(1)))})
        else:
            out.append({"label": "" if book.get("hide_images") else f"photo {im}", "url": None})
    return out


def edition(book):
    m = re.search(r"(\d{4}(?:\s*[-–]\s*\d{1,4})?)", book["title"])
    return re.sub(r"\s*[-–]\s*", "–", m.group(1)) if m else book["title"]


def crosslinks(all_tables):
    """Links between editions of one series: build/crosslinks/chapters.py (hand-made chapter topics) and
    build/crosslinks/families/*.json (recurring tables). Returns {slug: {"ch": ..., "tb": ...}} for the book pages."""
    import importlib.util
    f = os.path.join(SCRIPTS, "crosslinks", "chapters.py")
    out = {b: {"ch": {}, "tb": {}} for b in all_tables}
    if not os.path.exists(f):
        return out
    spec = importlib.util.spec_from_file_location("xl_chapters", f)
    mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
    ed = {b["slug"]: edition(b) for b in BOOKS}
    for series in mod.SERIES.values():
        for topic, members in series["topics"].items():
            present = [b for b in series["books"] if b in members and b in all_tables]
            if len(present) < 2:
                continue
            for b in present:
                for chap in members[b]:
                    others = [{"s": o, "e": ed[o], "c": members[o]} for o in present if o != b]
                    out[b]["ch"].setdefault(chap, []).append({"t": topic, "o": others})
    byid = {(b, t["id"]): t for b, ts in all_tables.items() for t in ts}
    fams = []
    for ff in sorted(glob.glob(os.path.join(SCRIPTS, "crosslinks", "families", "*.json"))):
        with open(ff, encoding="utf-8") as fh:
            for fam in json.load(fh).get("families", []):
                mem = []
                for m in fam.get("members", []):
                    b, _, tid = m.partition("/")
                    if (b, tid) in byid:
                        mem.append((b, tid))
                    else:
                        print(f"crosslinks: {os.path.basename(ff)}: unknown table {m}")
                fams.append({"label": fam.get("label", ""), "note": fam.get("note", ""), "mem": mem})
    # a chapter under two topics can put one table in two families: merge families that share a table
    owner = {}
    for i, fam in enumerate(fams):
        for key in fam["mem"]:
            if key in owner and owner[key] != i:
                j = owner[key]
                while "into" in fams[j]:
                    j = fams[j]["into"]
                if j != i:
                    for k2 in fams[i]["mem"]:
                        if k2 not in fams[j]["mem"]:
                            fams[j]["mem"].append(k2)
                    if fam["note"] and fam["note"] not in fams[j]["note"]:
                        fams[j]["note"] = (fams[j]["note"] + " " + fam["note"]).strip()
                    fam["into"] = j
                    for k2 in fams[j]["mem"]:
                        owner[k2] = j
                break
            owner[key] = i
    order = {s: i for i, s in enumerate(x["slug"] for x in BOOKS)}
    for fam in fams:
        if "into" in fam:
            continue
        mem = fam["mem"]
        if len({b for b, _ in mem}) < 2:
            continue
        mem.sort(key=lambda x: (ed[x[0]], order[x[0]]))
        for b, tid in mem:
            out[b]["tb"][tid] = {"f": fam["label"], "n": fam["note"],
                                 "o": [{"s": o, "e": ed[o], "id": oid, "t": byid[(o, oid)].get("title") or "",
                                  "p": ", ".join(byid[(o, oid)].get("printed_pages") or [])}
                                       for o, oid in mem if o != b]}
    return out


def cells(tables):
    return sum(len(r) for t in tables for p in t.get("parts", []) for r in p.get("rows", []))


def main():
    os.makedirs(os.path.join(HERE, "data"), exist_ok=True)
    cards, pages = [], []
    for b in BOOKS:
        b["_dir_n"] = build_directory(b)
        b["_chron_n"] = build_chronology(b)
        for key, kind in (("_dir_n", "directory"), ("_chron_n", "chronology")):
            committed = os.path.join(HERE, "data", f'{b["slug"]}-{kind}.json')
            if not b[key] and os.path.exists(committed):  # folder not on this machine: keep the committed page
                with open(committed, encoding="utf-8") as fh:
                    b[key] = len(json.load(fh))
        tables = load(b)
        if not tables:  # book folder not on this machine: keep the committed data rather than dropping the book
            committed = os.path.join(HERE, "data", b["slug"] + ".json")
            if os.path.exists(committed):
                with open(committed, encoding="utf-8") as fh:
                    tables = json.load(fh)
                for t in tables:
                    t["file"] = t["id"] + ".json"
                print(f"{b['slug']}: no tables in {book_dir(b)}; using committed data/{b['slug']}.json")
        for t in tables:
            t["scans"] = scan_links(b, t)
        n, c = len(tables), cells(tables)
        chapters = len({t.get("chapter") for t in tables})
        if tables:
            clean = [{k: v for k, v in t.items() if k not in ("file",)} for t in tables]
            with open(os.path.join(HERE, "data", b["slug"] + ".json"), "w", encoding="utf-8") as fh:
                json.dump(clean, fh, ensure_ascii=False, indent=1)
            pages.append((b, clean, n, c))
        cards.append((b, n, c, chapters))
        print(f"{b['slug']}: {n} tables, {c:,} cells")
    xl = crosslinks({b["slug"]: clean for b, clean, n, c in pages})
    for b, clean, n, c in pages:
            os.makedirs(os.path.join(HERE, "book", b["slug"]), exist_ok=True)
            data = json.dumps(clean, ensure_ascii=False).replace("</", "<\\/")
            doc = (TEMPLATE.replace("__DATA__", data).replace("__COUNT__", str(n))
                   .replace("__XL__", json.dumps(xl[b["slug"]], ensure_ascii=False).replace("</", "<\\/"))
                   .replace("__HIDEIMG__", "true" if b.get("hide_images") else "false")
                   .replace("__XLSX__", f' · <a href="../../{dl(b["slug"], "tables.xlsx")}" style="color:inherit" download>Excel</a>' if dl(b["slug"], "tables.xlsx") else "")
                   .replace("__CELLS__", f"{c:,}").replace("__BOOK__", html.escape(b["title"]))
                   .replace("__SLUG__", b["slug"]).replace("__SOURCE__", "LLM-transcribed")
                   .replace("__DIRLINK__", ('<a class="dirbtn" href="directory.html">Directories</a>' if b.get("_dir_n") else "")
                            + ('<a class="dirbtn" href="chronology.html">Chronologies</a>' if b.get("_chron_n") else "")
                            + (f'<button class="aboutbtn" onclick="document.getElementById(\'about\').showModal()">About</button>'
                               f'<dialog id="about" onclick="if(event.target===this)this.close()"><h3>{html.escape(b["title"])}</h3><div class="pub">{html.escape(b["publisher"])}</div>'
                               f'<p>{html.escape(b["gaps"])}</p><form method="dialog"><button>Close</button></form></dialog>' if b.get("gaps") else "")))
            with open(os.path.join(HERE, "book", b["slug"], "index.html"), "w", encoding="utf-8") as fh:
                fh.write(doc)
    with open(os.path.join(HERE, "index.html"), "w", encoding="utf-8") as fh:
        fh.write(landing(cards))
    books = [{"slug": b["slug"], "title": b["title"], "dir": bool(b.get("_dir_n")), "chron": bool(b.get("_chron_n"))} for b, n, c, ch in cards if n]
    with open(os.path.join(HERE, "search.html"), "w", encoding="utf-8") as fh:
        fh.write(SEARCH.replace("__BOOKS__", json.dumps(books, ensure_ascii=False)))


def landing(cards):
    items = []
    for b, n, c, ch in cards:
        stat = (f"<b>{n}</b> tables · <b>{c:,}</b> cells · {ch} chapters" if n else "<i>transcription in progress</i>")
        if n and b.get("in_progress"):
            stat += " · <i>transcription in progress</i>"
        link = f'<a class="go dirgo" href="book/{b["slug"]}/">Tables →</a>' if n else ""
        if b.get("_dir_n"):
            stat += f' · <b>{b["_dir_n"]:,}</b> directory entries' + (" (in progress)" if b.get("dir_in_progress") else "")
            link += f' <a class="go dirgo" href="book/{b["slug"]}/directory.html">Directories →</a>'
        if b.get("_chron_n"):
            stat += f' · <b>{b["_chron_n"]:,}</b> chronology events'
            link += f' <a class="go dirgo" href="book/{b["slug"]}/chronology.html">Chronologies →</a>'
        item = f' · <a href="{b["item"]}">original scan</a>' if b.get("item") else ""
        grp = "japan" if b["slug"].startswith("japan") else "china" if b["slug"].startswith("china") else "other"
        title = f'<a href="book/{b["slug"]}/" style="color:inherit;text-decoration:none">{html.escape(b["title"])}</a>' if n else html.escape(b["title"])
        items.append((grp, f"""<article><h2>{title}</h2><div class="pub">{html.escape(b["publisher"])}</div>
<div class="stat">{stat}</div><div class="src">LLM-transcribed{item}</div><div class="links">{link}</div></article>"""))
    order = {"far-east": 0, "manchoukuo": 1, "korea": 2}
    other = sorted([(i, h) for i, (g, h) in enumerate(items) if g == "other"],
                   key=lambda x: next((v for k, v in order.items() if k in x[1]), 9))
    names = {"japan": "Japan", "china": "China", "other": "Other"}
    body = {g: "\n".join(h for gg, h in items if gg == g) for g in ("japan", "china")}
    body["other"] = "\n".join(h for _, h in other)
    grids = "".join(f'<section class="grp" id="{g}"><h2 class="grph">{names[g]}</h2><div class="grid">{body[g]}</div></section>'
                    for g in ("japan", "china", "other"))
    return LANDING.replace("__CARDS__", grids)


LANDING = r"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Old Year Book Tables of East Asia</title>
<style>
:root{--bg:#f4f5f3;--panel:#ffffff;--ink:#1b2420;--muted:#5d6a62;--line:#d8ded9;--accent:#1f4a2c;--accent-ink:#ffffff}
@media (prefers-color-scheme: dark){:root:not([data-theme="light"]){--bg:#111814;--panel:#17211b;--ink:#e4ebe6;--muted:#9aa89f;--line:#2c3a31;--accent:#8cc49e;--accent-ink:#0f1a13}}
:root[data-theme="dark"]{--bg:#111814;--panel:#17211b;--ink:#e4ebe6;--muted:#9aa89f;--line:#2c3a31;--accent:#8cc49e;--accent-ink:#0f1a13}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font:16px/1.55 Georgia,"Times New Roman",serif}
.band{background:var(--accent);color:var(--accent-ink)}.band>div{max-width:980px;margin:0 auto;padding:34px 16px 30px}.band h1{font-weight:normal;font-size:30px;margin:0 0 8px}.band .lede{color:var(--accent-ink);opacity:.9;margin:0}
main{max-width:980px;margin:0 auto;padding:26px 16px 60px}
.topnav{margin:18px 0 0;display:flex;gap:8px;flex-wrap:wrap;align-items:center}.jump{display:contents}.jump a{display:inline-block;border:1px solid var(--accent-ink);color:var(--accent-ink);padding:6px 16px;border-radius:5px;text-decoration:none;font-size:15px}.jump a:hover{background:var(--accent-ink);color:var(--accent)}
.grp{scroll-margin-top:12px}.grp{border-top:2px solid var(--line);margin-top:34px;padding-top:6px}.grp:first-child{margin-top:4px}.grph{font-size:14px;letter-spacing:.08em;text-transform:uppercase;color:var(--accent);margin:18px 0 0;font-weight:bold}.grp .grid{margin-top:14px}
.searchbtn{display:inline-block;background:var(--accent-ink);color:var(--accent);font-weight:bold;padding:9px 16px;border-radius:5px;text-decoration:none;font-size:15px}
.lede{color:var(--muted);max-width:720px}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:18px;margin-top:28px}
article{background:var(--panel);border:1px solid var(--line);border-top:3px solid var(--accent);padding:18px 18px 16px;display:flex;flex-direction:column}
h2{font-size:20px;font-weight:normal;margin:0 0 4px}.pub{color:var(--muted);font-size:13px;margin-bottom:8px}
.links{margin-top:auto;display:flex;flex-wrap:wrap;gap:8px;align-items:center}.links .dirgo{margin:0}
.about{font:inherit;font-size:13px;background:transparent;color:var(--accent);border:1px solid var(--accent);border-radius:5px;padding:5px 10px;cursor:pointer;flex-basis:100%;max-width:max-content}
dialog{max-width:min(560px,calc(100vw - 32px));border:1px solid var(--line);border-top:4px solid var(--accent);background:var(--panel);color:var(--ink);padding:18px 20px;border-radius:6px}
dialog::backdrop{background:rgba(0,0,0,.45)}dialog h3{margin:0 0 2px;font-weight:normal;font-size:19px}dialog p{font-size:14.5px}
dialog form button{font:inherit;font-size:14px;background:var(--accent);color:var(--accent-ink);border:0;border-radius:5px;padding:6px 14px;cursor:pointer}.stat{font-size:14px;margin-bottom:6px}.src{font-size:12.5px;color:var(--muted);margin-bottom:12px}
a{color:var(--accent)}.go{font-size:15px;text-decoration:none;font-weight:bold}.dirgo{display:inline-block;margin:8px 8px 0 0;background:var(--accent);color:var(--accent-ink);padding:6px 12px;border-radius:5px;font-size:14px}
.llmwarn{margin:28px 0 0;padding:12px 14px;border:1px solid #8a5a00;border-left:4px solid #8a5a00;background:var(--panel);font-size:14px}
footer{margin-top:24px;font-size:13px;color:var(--muted);border-top:1px solid var(--line);padding-top:14px}
</style></head><body><div class="band"><div>
<h1>Old Year Book Tables of East Asia</h1>
<div class="topnav"><a class="searchbtn" href="search.html">Full Search</a><nav class="jump" id="jump"><a href="#japan" id="j-japan">Japan</a><a href="#china" id="j-china">China</a><a href="#other">Other</a></nav></div>
</div></div>
<main>
<div id="groups">
__CARDS__
</div>
<script>if(Math.random()<.5){const g=document.getElementById("groups");g.insertBefore(document.getElementById("china"),document.getElementById("japan"));
const n=document.getElementById("jump");n.insertBefore(document.getElementById("j-china"),document.getElementById("j-japan"))}</script>
<div class="llmwarn" role="note"><b>Warning:</b> These tables were transcribed by the vision model of Opus 5.5. Before using any of these figures, you must verify specific statistics with the original source which is linked to whenever possible.</div>
<script>document.addEventListener("click",e=>{const b=e.target.closest("[data-about]");if(b){document.getElementById(b.dataset.about).showModal();return}
if(e.target.tagName==="DIALOG")e.target.close()});</script>
<footer>Each table can be downloaded as CSV from its page. Each book can be downloaded whole as an Excel workbook (one sheet per table, with a linked contents sheet) or as JSON; directories are available as Markdown.<br><br>The website was created by Claude Opus 5.5 with <a href="https://muninn.net/">Konrad M. Lawson</a> at the prompt. See: <a href="https://froginawell.net/frog/sources/">Other Resources at Frog in a Well</a></footer>
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
#list a.on,#list a.on:hover{background:var(--accent);color:var(--accent-ink);border-left:3px solid var(--accent)}
#list a.on small{color:var(--accent-ink);opacity:.85}
body.kbd #list a:not(.on):hover{background:transparent}
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
.chgrid{display:grid;grid-template-columns:repeat(auto-fill,minmax(min(100%,calc(var(--chfs,17px)*12)),1fr));gap:calc(var(--chfs,17px)*.6)}
.chbtn{display:block;padding:.65em .8em;border:1px solid var(--line);border-radius:6px;background:var(--panel);color:var(--ink);text-decoration:none;font-weight:bold;font-size:var(--chfs,clamp(16px,.9vw + 9px,21px));line-height:1.25;overflow-wrap:anywhere}
.chbtn:hover{border-color:var(--accent);background:var(--hi)}
.chbtn small{display:block;color:var(--muted);font-weight:normal;font-size:max(11px,.62em);margin-top:.2em}
.chhead a{color:inherit}
.xl{font-size:13.5px;margin:4px 0 12px;color:var(--muted);line-height:1.9}
.xl a{color:var(--accent)}
.xlc a{margin-right:12px;white-space:nowrap}
.xlo{display:inline-flex;align-items:stretch;margin:2px 8px 2px 0;border:1px solid var(--line);border-radius:5px;background:var(--panel);white-space:nowrap;line-height:1.7;overflow:hidden;vertical-align:middle}
.xlo a{padding:1px 9px;display:flex;align-items:center}
.cmpb{font-size:12px;padding:1px 9px;border:0;border-left:1px solid var(--line);border-radius:0;background:var(--hi);color:var(--ink)}
.cmpb:hover{background:var(--accent);color:var(--accent-ink)}
.xln{font-style:italic;line-height:1.4;margin-top:2px}
#cmp{overflow:auto;padding:18px 22px;border-left:1px solid var(--line);min-width:0;background:var(--panel)}
#cmp .cmphead{display:flex;gap:8px;align-items:center;flex-wrap:wrap;margin-bottom:12px}
#cmp .cmphead select{flex:1;min-width:0}
body.cmp #wrap{grid-template-columns:280px minmax(0,1fr) minmax(0,1fr)}
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
.dirbtn{margin-left:auto;background:var(--accent-ink);color:var(--accent)!important;opacity:1!important;font-weight:bold;font-size:14px;padding:6px 14px;border-radius:5px;text-decoration:none;align-self:center}.dirbtn:hover{filter:brightness(.93)}.dirbtn+#toggle,.dirbtn+.dirbtn,.dirbtn+.aboutbtn{margin-left:0}
.ctx{max-width:760px;font-size:14.5px;line-height:1.55;margin:8px 0 12px;padding:9px 12px;border-left:3px solid var(--accent);background:var(--panel)}
.aboutbtn{margin-left:auto;font:inherit;font-size:14px;background:transparent;color:var(--accent-ink);border:1px solid currentColor;border-radius:5px;padding:5px 12px;cursor:pointer;align-self:center}.aboutbtn+#toggle{margin-left:0}
dialog{max-width:min(560px,calc(100vw - 32px));border:1px solid var(--line);border-top:4px solid var(--accent);background:var(--panel);color:var(--ink);padding:18px 20px;border-radius:6px;font-size:14.5px}dialog::backdrop{background:rgba(0,0,0,.45)}dialog h3{margin:0 0 2px;font-weight:normal;font-size:19px}dialog .pub{color:var(--muted);font-size:13px}dialog form button{font:inherit;font-size:14px;background:var(--accent);color:var(--accent-ink);border:0;border-radius:5px;padding:6px 14px;cursor:pointer}
@media (max-width:760px){#wrap,body.cmp #wrap{grid-template-columns:minmax(0,1fr);height:auto}#cmp{border-left:0;border-top:2px solid var(--accent);padding:14px 16px}#side,#main{min-width:0;max-width:100vw}#list a{overflow-wrap:anywhere}.tw{max-height:none}header{padding:12px 16px}header h1{font-size:18px}.dirbtn{margin-left:0}#side{border-right:0;border-bottom:1px solid var(--line)}#list{max-height:40vh}#main{padding:14px 16px}.chgrid{gap:8px}.chbtn{padding:11px 13px}.chbtn small{font-size:12px}}
</style>
</head>
<body>
<header><a href="../../" style="text-decoration:none;font-size:14px">← All books</a><h1>__BOOK__</h1>
<span class="meta">__COUNT__ tables · __CELLS__ cells · __SOURCE__ · <a href="../../data/__SLUG__.json" style="color:inherit">JSON</a>__XLSX__</span>
__DIRLINK__<button id="toggle" title="Toggle light/dark">◐</button></header>
<div id="wrap">
<nav id="side"><div class="ctl">
<input id="q" type="search" placeholder="Search titles, headings, cells…">
<select id="ch"><option value="">All chapters</option></select>
<label style="font-size:13px;color:var(--muted)"><input type="checkbox" id="flag"> only tables with transcriber warnings</label>
<span class="keys">↑ / ↓ keys: previous / next table</span>
</div><div id="list"></div></nav>
<main id="main"></main>
<aside id="cmp" hidden></aside>
</div>
<script>
const T=__DATA__;
const HIDEIMG=__HIDEIMG__;
const XL=__XL__;
const $=s=>document.querySelector(s);
const esc=s=>String(s??"").replace(/[&<>"]/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]));
const isNum=s=>/^[\s(]*[-—–]?[\d.,]+[)*%]*\s*$/.test(s)||/^[—–-]$/.test(s.trim())||s.trim()==="...";
const warnRe=/not reconcile|unreadable|illegible|uncertain|could not|does not/i;
T.forEach(t=>{t._text=[t.title,t.table_no,t.caption_extra,t.context,t.chapter,...(t.parts||[]).flatMap(p=>[p.label,...p.columns,...p.rows.flat()]),...(t.footnotes||[])].join(" ").toLowerCase();
 t._warn=(t.transcriber_notes||[]).some(n=>warnRe.test(n));});
const chapters=[...new Set(T.map(t=>t.chapter||"(no chapter)"))];
chapters.forEach(c=>$("#ch").insertAdjacentHTML("beforeend",`<option>${esc(c)}</option>`));
function label(t){return (t.table_no?`Table ${t.table_no}. `:"")+(t.title||"")+(t.continued?" (continued)":"")}
function renderList(){const q=$("#q").value.trim().toLowerCase(),ch=$("#ch").value,fl=$("#flag").checked;let h="",last=null,n=0;
 T.forEach((t,i)=>{if(ch&&(t.chapter||"(no chapter)")!==ch)return;if(fl&&!t._warn)return;if(q&&!q.split(/\s+/).every(w=>t._text.includes(w)))return;
  const c=t.chapter||"(no chapter)";if(c!==last){h+=`<div class="ch">${esc(c)}</div>`;last=c}
  h+=`<a href="#${t.id}" data-i="${i}">${esc(label(t))}<small>p. ${esc((t.printed_pages||[]).join(", "))}${HIDEIMG?"":" · "+esc(t.image)}${t._warn?" · ⚠":""}</small></a>`;n++});
 $("#list").innerHTML=h||"<p style='padding:10px'>No matches.</p>";mark()}
function hl(s,q){s=esc(s);if(!q)return s;q.split(/\s+/).filter(Boolean).forEach(w=>{s=s.replace(new RegExp("("+w.replace(/[.*+?^${}()|[\]\\]/g,"\\$&")+")","ig"),"<mark>$1</mark>")});return s}
function csv(t){const L=[];(t.parts||[]).forEach(p=>{if(p.label)L.push([p.label]);L.push(p.columns);p.rows.forEach(r=>L.push(r));L.push([])});
 return L.map(r=>r.map(c=>/[",\n]/.test(c??"")?'"'+String(c).replace(/"/g,'""')+'"':(c??"")).join(",")).join("\n")}
function tableHTML(t,q,other){let h=`<section class="tbl" id="t-${t.id}"><h2><a href="#${t.id}">${hl(label(t),q)}</a></h2><div class="sub">${esc(t.chapter||"")} · printed page${(t.printed_pages||[]).length>1?"s":""} ${esc((t.printed_pages||[]).join(", "))}${HIDEIMG?"":` · ${/^p\d/.test(t.image||"")?"scan leaf":"photo"} ${esc((t.images||[t.image]).join(", "))}`}</div>`;
 if(!other)h+=xlTable(t);
 if(t.caption_extra)h+=`<div class="sub"><i>${hl(t.caption_extra,q)}</i></div>`;
 if(t.context)h+=`<p class="ctx"><b>Context.</b> ${hl(t.context,q)}</p>`;
 (t.parts||[]).forEach(p=>{if(p.label)h+=`<div class="part">${hl(p.label,q)}</div>`;
  h+=`<div class="tw"><table><thead><tr>${p.columns.map((c,j)=>`<th class="sortable" data-col="${j}" title="Click to sort">${hl(c,q)}</th>`).join("")}</tr></thead><tbody>`;
  p.rows.forEach((r,ri)=>{const sec=r.length>1&&r.slice(1).every(c=>c==="");h+=`<tr data-i="${ri}"${sec?' class="sec"':""}>`+r.map((c,j)=>`<td class="${j&&isNum(c)?"num":""}${j&&c===""&&!sec?" blank":""}">${hl(c,q)}</td>`).join("")+"</tr>"});
  h+="</tbody></table></div>"});
 if((t.footnotes||[]).length)h+=`<div class="notes"><b>Printed notes</b><ul>${t.footnotes.map(n=>`<li>${hl(n,q)}</li>`).join("")}</ul></div>`;
 if((t.transcriber_notes||[]).length)h+=`<div class="notes"><b>Transcriber's notes</b><ul>${t.transcriber_notes.map(n=>`<li class="${warnRe.test(n)?"warn":""}">${esc(n)}</li>`).join("")}</ul></div>`;
 h+=`<div class="row"><button data-act="dl" data-id="${t.id}">Download CSV</button><button data-act="cp" data-id="${t.id}">Copy as TSV</button></div>`;
 if(!HIDEIMG)h+=`<div class="sub">Source: ${(t.scans||[]).map(s=>s.url?`<a href="${s.url}" target="_blank" rel="noopener">${esc(s.label)}</a>`:esc(s.label)).join(", ")}</div>`;
 h+=`</section>`;
 return h}
// Links to the same chapter / the same recurring table in other editions of the series
function xlChapter(ch){const L=XL.ch[ch];if(!L)return "";
 return `<div class="xl xlc">`+L.map(x=>`<div>${L.length>1?esc(x.t)+" in other editions":"This chapter in other editions"}: `+
  x.o.map(o=>o.c.map(c=>`<a href="../${o.s}/#ch=${encodeURIComponent(c)}">${esc(o.e)}${o.c.length>1?" · "+esc(c):""}</a>`).join("")).join("")+`</div>`).join("")+`</div>`}
function xlTable(t){const x=XL.tb[t.id];if(!x||!x.o.length)return "";const g=[];x.o.forEach(o=>{const l=g.find(z=>z.s===o.s);if(l)l.n++;else g.push({...o,n:1})});
 return `<div class="xl">Similar table in other editions: `+g.map(o=>{const lab=o.e+(o.n>1?` (${o.n} parts)`:"");
  return `<span class="xlo"><a href="../${o.s}/#${encodeURIComponent(o.id)}" title="${esc(o.t)}">${esc(lab)}</a><button class="cmpb" data-cmp="${o.s}/${esc(o.id)}" data-for="${esc(t.id)}" title="Show the ${esc(o.e)} table side by side">Compare</button></span>`}).join("")+
  (x.n?`<div class="xln">${esc(x.n)}</div>`:"")+`</div>`}
// Side-by-side comparison with a table from another edition (loaded from ../../data/<slug>.json)
const BOOKDATA={};let cmpS=null,cmpId=null,cmpT=null,cmpE="",cmpJump=false;
function loadBook(s){return BOOKDATA[s]||(BOOKDATA[s]=fetch("../../data/"+s+".json").then(r=>{if(!r.ok)throw r.status;return r.json()}))}
function closeCmp(){cmpS=cmpId=cmpT=null;document.body.classList.remove("cmp");$("#cmp").hidden=true;$("#cmp").innerHTML=""}
async function showCmp(){if(!cmpS||mode!=="one"){closeCmp();return}
 const pane=$("#cmp"),x=XL.tb[cur];document.body.classList.add("cmp");pane.hidden=false;
 const opts=x?x.o:[];const ms=opts.filter(o=>o.s===cmpS);const pick=ms.find(o=>o.id===cmpId)||ms[0];
 const head=`<div class="cmphead"><select id="cmpsel" aria-label="Compare with">${opts.map(o=>`<option value="${o.s}/${esc(o.id)}"${pick&&o.s===pick.s&&o.id===pick.id?" selected":""}>${esc(o.e)} — ${esc(o.t)}${o.p?` (p. ${esc(o.p.split(", ")[0])})`:""}</option>`).join("")}${pick?"":`<option selected>—</option>`}</select><button id="cmpx">Close ✕</button></div>`;
 if(!pick){pane.innerHTML=head+`<p class="sub">${opts.length?`This table has no counterpart in the ${esc(cmpE)} edition; choose another edition above.`:"This table has no counterpart in other editions."}</p>`;return}
 cmpId=pick.id;cmpE=pick.e;pane.innerHTML=head+`<p class="sub">Loading…</p>`;
 try{const T2=await loadBook(pick.s);const t2=T2.find(z=>z.id===pick.id);if(!t2)throw 0;cmpT=t2;
  if(cmpS!==pick.s||cmpId!==pick.id)return;
  pane.innerHTML=head+`<div class="chhead">${esc(pick.e)} edition · <a href="../${pick.s}/#${encodeURIComponent(pick.id)}">open in that book</a></div>`+tableHTML(t2,"",true).replace(' id="t-',' data-x="');
  pane.scrollTop=0;pane.querySelectorAll("table").forEach(initSort);if(innerWidth<=760&&cmpJump){cmpJump=false;pane.scrollIntoView({block:"start"})}}
 catch(e){pane.innerHTML=head+`<p class="sub">Could not load that table (the page must be served from a web server).</p>`}}
$("#cmp").addEventListener("change",e=>{if(e.target.id!=="cmpsel")return;const v=e.target.value,i=v.indexOf("/");cmpS=v.slice(0,i);cmpId=v.slice(i+1);showCmp()});
$("#cmp").addEventListener("click",e=>{if(e.target.id==="cmpx"){closeCmp();return}const b=e.target.closest("button[data-act]");if(b&&cmpT)act(b,cmpT)});
const LLMWARN=`<div class="llmwarn" role="note"><b>Warning:</b> These tables were transcribed by the vision model of Opus 5.5. Before using any of these figures, you must verify specific statistics with the original source which is linked to whenever possible.</div>`;
function filtered(){const q=$("#q").value.trim().toLowerCase(),ch=$("#ch").value,fl=$("#flag").checked;
 return T.filter(t=>(!ch||(t.chapter||"(no chapter)")===ch)&&(!fl||t._warn)&&(!q||q.split(/\s+/).every(w=>t._text.includes(w))))}
let mode="one",cur=null;
function showHome(){mode="home";cur=null;closeCmp();const n={};T.forEach(t=>{const c=t.chapter||"(no chapter)";n[c]=(n[c]||0)+1});
 $("#main").innerHTML=`<div class="chhead">Contents</div><h2 style="margin-bottom:6px">Chapters</h2><div class="chsum">${T.length} table${T.length===1?"":"s"} in ${chapters.length} chapter${chapters.length===1?"":"s"}. Choose a chapter, or pick a single table from the list.</div><div class="chgrid">`+
  chapters.map(c=>`<a class="chbtn" href="#ch=${encodeURIComponent(c)}">${esc(c)}<small>${n[c]} table${n[c]===1?"":"s"}</small></a>`).join("")+`</div>`+LLMWARN;
 $("#main").scrollTop=0;fitGrid();mark()}
// Desktop: pick the largest button font (12-28px) at which every chapter button fits in the pane without scrolling
function fitGrid(){const g=$(".chgrid");if(!g)return;g.style.removeProperty("--chfs");if(innerWidth<=760)return;
 const m=$("#main"),limit=()=>m.getBoundingClientRect().bottom-parseFloat(getComputedStyle(m).paddingBottom);
 const fits=x=>{g.style.setProperty("--chfs",x+"px");return g.getBoundingClientRect().bottom<=limit()};
 let lo=12,hi=28;if(fits(hi))return;if(!fits(lo))return;
 for(let k=0;k<9;k++){const mid=(lo+hi)/2;if(fits(mid))lo=mid;else hi=mid}
 g.style.setProperty("--chfs",lo.toFixed(2)+"px")}
let fitRaf=0;addEventListener("resize",()=>{if(mode!=="home")return;cancelAnimationFrame(fitRaf);fitRaf=requestAnimationFrame(fitGrid)});
function showOne(id){const t=T.find(x=>x.id===id)||T[0];if(!t){$("#main").innerHTML="<p>No tables yet.</p>";return}
 mode="one";cur=t.id;$("#main").innerHTML=tableHTML(t,$("#q").value.trim())+LLMWARN;$("#main").scrollTop=0;
 document.querySelectorAll("#main table").forEach(initSort);mark();if(cmpS)showCmp()}
function showChapter(ch){const q=$("#q").value.trim();const ts=filtered();mode="chapter";cur=null;closeCmp();
 let h=`<div class="chhead"><a href="#">All chapters</a> · Chapter</div><h2 style="margin-bottom:6px">${esc(ch)}</h2><div class="chsum">${ts.length} table${ts.length===1?"":"s"}${$("#flag").checked||q?" matching the current filters":""}</div>`+xlChapter(ch);
 h+=(ts.map(t=>tableHTML(t,q)).join("")||"<p>No tables match.</p>")+LLMWARN;
 $("#main").innerHTML=h;$("#main").scrollTop=0;document.querySelectorAll("#main table").forEach(initSort);
 if(enterAt&&ts.length){const t=enterAt==="first"?ts[0]:ts[ts.length-1];cur=t.id;const el=document.getElementById("t-"+t.id);if(el&&enterAt==="last")el.scrollIntoView({block:"start"});
  const a=document.querySelector(`#list a[href="#${CSS.escape(t.id)}"]`);if(a)a.scrollIntoView({block:"nearest"})}
 enterAt=null;mark()}
let enterAt=null;
function route(){const h=decodeURIComponent(location.hash.slice(1));
 if(h.startsWith("ch=")){const ch=h.slice(3);if($("#ch").value!==ch){$("#ch").value=ch;renderList()}showChapter(ch);return}
 if(mode==="chapter"&&h&&document.getElementById("t-"+h)){cur=h;document.getElementById("t-"+h).scrollIntoView({block:"start"});mark();return}
 if(!h){if($("#ch").value){$("#ch").value="";renderList()}if(T.length){showHome();return}}
 showOne(h)}
$("#main").addEventListener("click",e=>{const c=e.target.closest("button.cmpb");
 if(c){const v=c.dataset.cmp,i=v.indexOf("/");cmpS=v.slice(0,i);cmpId=v.slice(i+1);cmpJump=true;
  // open the single-table view directly: in chapter view a hash change would only scroll to the table
  if(mode==="one"&&cur===c.dataset.for)showCmp();else{if(decodeURIComponent(location.hash.slice(1))!==c.dataset.for)history.pushState(null,"","#"+c.dataset.for);showOne(c.dataset.for)}return}
 const b=e.target.closest("button[data-act]");if(!b)return;const t=T.find(x=>x.id===b.dataset.id);if(t)act(b,t)});
function act(b,t){
 if(b.dataset.act==="dl"){const bl=new Blob(["﻿"+csv(t)],{type:"text/csv"});const a=document.createElement("a");a.href=URL.createObjectURL(bl);a.download=t.id+".csv";a.click()}
 else navigator.clipboard.writeText((t.parts||[]).map(p=>[p.columns,...p.rows].map(r=>r.join("\t")).join("\n")).join("\n\n"))}
$("#list").addEventListener("click",e=>{const c=e.target.closest(".ch");if(!c)return;location.hash="ch="+encodeURIComponent(c.textContent)});
// Up/Down arrows: previous/next table in the sidebar list (ignored while typing in a field)
document.addEventListener("keydown",e=>{if(e.key!=="ArrowDown"&&e.key!=="ArrowUp")return;if(e.altKey||e.ctrlKey||e.metaKey)return;
 const tag=(document.activeElement&&document.activeElement.tagName)||"";if(/INPUT|SELECT|TEXTAREA/.test(tag))return;
 const links=[...document.querySelectorAll("#list a[href^='#']")];if(!links.length)return;
 document.body.classList.add("kbd");
 let i=links.findIndex(a=>a.classList.contains("on"));const down=e.key==="ArrowDown";
 const ch=$("#ch").value;
 // at either end of a chapter's list, step into the next/previous chapter
 if(ch&&i>-1&&((down&&i===links.length-1)||(!down&&i===0))){
  const opts=[...$("#ch").options].map(o=>o.value).filter(Boolean);const k=opts.indexOf(ch)+(down?1:-1);
  if(k>=0&&k<opts.length){e.preventDefault();enterAt=down?"first":"last";location.hash="ch="+encodeURIComponent(opts[k])}
  return}
 i=i<0?(down?0:links.length-1):Math.min(links.length-1,Math.max(0,i+(down?1:-1)));
 e.preventDefault();location.hash=links[i].getAttribute("href").slice(1);links[i].scrollIntoView({block:"nearest"})});
document.addEventListener("mousemove",()=>document.body.classList.remove("kbd"));
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
 if(ch)location.hash="ch="+encodeURIComponent(ch);else{history.replaceState(null,"",location.pathname);showHome()}});
["q","flag"].forEach(k=>$("#"+k).addEventListener("input",()=>{renderList();if(mode==="chapter")showChapter($("#ch").value)}));
window.addEventListener("hashchange",route);
$("#toggle").onclick=()=>{const r=document.documentElement,d=r.dataset.theme==="dark"||(!r.dataset.theme&&matchMedia("(prefers-color-scheme: dark)").matches);r.dataset.theme=d?"light":"dark"};
renderList();route();
</script>
</body>
</html>
"""


def dir_key(f):
    mp = re.match(r"p(\d)-(\d+)", os.path.basename(f))
    if mp:
        return int(mp.group(1)) * 10000 + int(mp.group(2))
    m = re.search(r"(\d+)", os.path.basename(f))
    return int(m.group(1)) if m else 0


def section_summary(names, last=False):
    """': A, B, C.' from appendix/chapter names, shortened to their top-level part, at most four."""
    parts = []
    for a in names:
        a = re.sub(r"^(Appendix|App\.|Chapter|Ch\.|Table)\s*[A-Z0-9]+\s*[:.—-]\s*", "", a or "").strip()
        if not last:
            a = re.split(r" — |: ", a)[0]
        a = a.strip("[] .")
        if a and a not in parts:
            parts.append(a)
    if not parts:
        return "."
    return ": " + ", ".join(parts[:4]) + (", etc." if len(parts) > 4 else ".")


def build_directory(book):
    """Write <slug>/directory.html from <dir>/_work/directory/*.json; return the entry count."""
    files = sorted(glob.glob(os.path.join(book_dir(book), "_work", "directory", "*.json")), key=dir_key)
    entries = []
    for f in files:
        try:
            with open(f, encoding="utf-8") as fh:
                d = json.load(fh)
        except (FileNotFoundError, json.JSONDecodeError):
            print("skipped", f)
            continue
        leaf = d.get("leaf") or os.path.basename(f)[:-5]
        scan = scan_links(book, {"images": [leaf]})[0]
        for e in d.get("entries", []):
            sec = e.get("section") or ""
            if sec.isupper():
                sec = sec.title()
            entries.append({"a": d.get("appendix") or "", "s": sec, "n": (e.get("name") or "").rstrip(" ,.") + (" " + e["mark"] if e.get("mark") else "") + (f' ({e["rank"]})' if e.get("rank") else ""),
                            "t": e.get("text") or "", "p": e.get("page") or ", ".join(d.get("printed_pages") or []),
                            "l": scan["label"], "u": scan["url"]})
    if not entries:
        return 0
    os.makedirs(os.path.join(HERE, "book", book["slug"]), exist_ok=True)
    with open(os.path.join(HERE, "data", book["slug"] + "-directory.json"), "w", encoding="utf-8") as fh:
        json.dump(entries, fh, ensure_ascii=False, indent=1)
    data = json.dumps(entries, ensure_ascii=False).replace("</", "<\\/")
    desc = f"{len(entries):,} entries" + section_summary(e["a"] for e in entries)
    doc = (DIRTEMPLATE.replace("__DATA__", data).replace("__COUNT__", f"{len(entries):,}").replace("__DESC__", html.escape(desc))
           .replace("__BOOK__", html.escape(book["title"])).replace("__SLUG__", book["slug"])
           .replace("__PROG__", " · <i>transcription in progress</i>" if book.get("dir_in_progress") else "")
           .replace("__MD__", f' · <a href="../../{dl(book["slug"], "directory.md")}" download>Markdown</a>' if dl(book["slug"], "directory.md") else ""))
    with open(os.path.join(HERE, "book", book["slug"], "directory.html"), "w", encoding="utf-8") as fh:
        fh.write(doc)
    print(f"{book['slug']}: {len(entries)} directory entries")
    return len(entries)


def build_chronology(book):
    """Write <slug>/chronology.html from <dir>/_work/chronology/*.json (events lists); return the event count."""
    files = sorted(glob.glob(os.path.join(book_dir(book), "_work", "chronology", "*.json")), key=dir_key)
    events = []
    for f in files:
        try:
            with open(f, encoding="utf-8") as fh:
                c = json.load(fh)
        except (FileNotFoundError, json.JSONDecodeError):
            continue
        scan = scan_links(book, {"images": [c.get("image") or os.path.basename(f)[:-5].split("_")[0]]})[0]
        head = " — ".join(x for x in (c.get("chapter"), c.get("title")) if x)
        for e in c.get("events", []):
            events.append({"a": head, "s": "", "n": e.get("date") or "", "t": e.get("text") or "",
                           "p": e.get("page") or ", ".join(c.get("printed_pages") or []), "l": scan["label"], "u": scan["url"]})
    if not events:
        return 0
    os.makedirs(os.path.join(HERE, "book", book["slug"]), exist_ok=True)
    with open(os.path.join(HERE, "data", book["slug"] + "-chronology.json"), "w", encoding="utf-8") as fh:
        json.dump(events, fh, ensure_ascii=False, indent=1)
    data = json.dumps(events, ensure_ascii=False).replace("</", "<\\/")
    doc = (DIRTEMPLATE.replace("__DATA__", data).replace("__COUNT__", f"{len(events):,}")
           .replace("__BOOK__", html.escape(book["title"])).replace("__SLUG__", book["slug"])
           .replace("__PROG__", " · <i>transcription in progress</i>" if book.get("in_progress") else "")
           .replace("· Directories", "· Chronologies").replace("-directory.json", "-chronology.json")
           .replace(" entries", " events").replace("Filter names, places, firms, words…", "Filter dates, names, places, words…")
           .replace("> names only<", "> dates only<").replace("These entries were", "These events were")
           .replace("__MD__", f' · <a href="../../{dl(book["slug"], "chronology.md")}" download>Markdown</a>' if dl(book["slug"], "chronology.md") else "")
           .replace("__DESC__", html.escape(f"{len(events):,} events" + section_summary((e["a"].split(" — ")[-1] for e in events), last=True))))
    if book["slug"].startswith("japan-"):
        doc = doc.replace('<main><div id="out">', '<main><p style="margin:0 0 14px;font-size:15px">See also <a style="color:var(--accent)" href="https://froginawell.net/reference/empire-chronicle/">Chronicles of the Japanese Empire</a>.</p><div id="out">', 1)
    with open(os.path.join(HERE, "book", book["slug"], "chronology.html"), "w", encoding="utf-8") as fh:
        fh.write(doc)
    print(f"{book['slug']}: {len(events)} chronology events")
    return len(events)


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
<header><a href="./" style="text-decoration:none;font-size:14px">← Tables</a><a href="../../" style="text-decoration:none;font-size:14px">All books</a><h1>__BOOK__ · Directories</h1>
<span class="meta">__DESC____PROG__ · LLM-transcribed · <a href="../../data/__SLUG__-directory.json">JSON</a>__MD__</span>
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
  h+=`<div class="e"><b>${hl(e.n,terms)}</b> <span class="t">${hl(e.t,terms)}</span><div class="m">p. ${esc(e.p)}${e.u?` · <a href="${e.u}" target="_blank" rel="noopener">${esc(e.l)}</a>`:e.l?" · "+esc(e.l):""}</div></div>`});
 $("#out").insertAdjacentHTML("beforeend",h);shown=Math.min(res.length,shown+STEP);$("#more").hidden=shown>=res.length}
const groupOf=e=>e.a+(e.s?" — "+e.s:"");
let tm;$("#q").addEventListener("input",()=>{clearTimeout(tm);tm=setTimeout(run,120)});
sel.addEventListener("change",run);$("#nameonly").addEventListener("change",run);$("#more").addEventListener("click",()=>more());
$("#toggle").addEventListener("click",()=>{const r=document.documentElement;const d=r.dataset.theme?r.dataset.theme==="dark":matchMedia("(prefers-color-scheme: dark)").matches;r.dataset.theme=d?"light":"dark"});
try{const p=new URLSearchParams(location.hash.slice(1));if(p.get("q"))$("#q").value=p.get("q");if(p.get("s"))sel.value=p.get("s")}catch(e){}
run();
</script></body></html>
"""


SEARCH = r"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Full Search · Old Year Book Tables of East Asia</title>
<style>
:root{--bg:#f4f5f3;--panel:#ffffff;--ink:#1b2420;--muted:#5d6a62;--line:#d8ded9;--accent:#1f4a2c;--accent-ink:#ffffff;--hi:#e2ece4;--warn:#8a5a00;--mark:#f3e3a0}
@media (prefers-color-scheme: dark){:root:not([data-theme="light"]){--bg:#111814;--panel:#17211b;--ink:#e4ebe6;--muted:#9aa89f;--line:#2c3a31;--accent:#8cc49e;--accent-ink:#0f1a13;--hi:#1f3527;--warn:#e0a54a;--mark:#5a4d1c}}
:root[data-theme="dark"]{--bg:#111814;--panel:#17211b;--ink:#e4ebe6;--muted:#9aa89f;--line:#2c3a31;--accent:#8cc49e;--accent-ink:#0f1a13;--hi:#1f3527;--warn:#e0a54a;--mark:#5a4d1c}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font:15px/1.5 Georgia,"Times New Roman",serif}
header{padding:14px 18px;background:var(--accent);color:var(--accent-ink);display:flex;gap:14px;align-items:baseline;flex-wrap:wrap}
header a{color:var(--accent-ink);opacity:.88;font-size:14px;text-decoration:none}header h1{font-size:20px;margin:0;font-weight:normal}
header button{margin-left:auto;background:transparent;color:var(--accent-ink);border:1px solid currentColor;border-radius:4px;font:inherit;padding:4px 8px;cursor:pointer}
main{max-width:1000px;margin:0 auto;padding:18px 16px 60px}
.box{background:var(--panel);border:1px solid var(--line);border-top:3px solid var(--accent);padding:14px;display:flex;gap:10px;flex-wrap:wrap}
input,select{font:inherit;font-size:16px;padding:8px 10px;border:1px solid var(--line);background:var(--bg);color:var(--ink);border-radius:4px}
#q{flex:1 1 320px}#scope{flex:0 0 auto}
#status{color:var(--muted);font-size:13px;margin:12px 0 10px}
.kind{font-size:17px;margin:26px 0 4px;color:var(--accent);border-bottom:2px solid var(--accent);padding-bottom:3px}
.bk{font-size:13px;letter-spacing:.06em;text-transform:uppercase;color:var(--accent);margin:18px 0 6px;border-bottom:1px solid var(--line);padding-bottom:3px}
.bk a{color:inherit}
.r{background:var(--panel);border:1px solid var(--line);border-left:3px solid var(--accent);padding:8px 12px;margin:0 0 7px}
.r a.t{font-size:15.5px;color:var(--ink);text-decoration:none;font-weight:bold}.r a.t:hover{text-decoration:underline}
.r .m{font-size:12.5px;color:var(--muted)}.r .m a{color:var(--accent)}
.r .snip{font-size:13px;margin-top:4px;font-family:"Iowan Old Style",Georgia,serif}
.r .snip div{white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
mark{background:var(--mark);color:inherit}
.llmwarn{margin:24px 0 8px;padding:12px 14px;border:1px solid var(--warn);border-left:4px solid var(--warn);background:var(--panel);font-size:14px}
</style></head><body>
<header><a href="./">← All books</a><h1>Full Search</h1><button id="toggle" title="Toggle light/dark">◐</button></header>
<main>
<div class="box"><input id="q" type="search" placeholder="e.g. rice, Dairen, cotton exports, Mitsui, Kato…" autofocus>
<select id="scope" aria-label="Search in">
<option value="all">Everything</option><option value="t">Tables only</option><option value="w">Who's Who only</option>
<option value="d">All directories</option><option value="c">Chronologies only</option></select></div>
<div id="status"></div><div id="out"></div>
<div class="llmwarn" role="note"><b>Warning:</b> These tables were transcribed by the vision model of Opus 5.5. Before using any of these figures, you must verify specific statistics with the original source which is linked to whenever possible.</div>
</main>
<script>
const BOOKS=__BOOKS__;
const $=s=>document.querySelector(s);
const esc=s=>String(s??"").replace(/[&<>"]/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]));
const norm=s=>String(s??"").normalize("NFD").replace(/[̀-ͯ]/g,"").toLowerCase();
function hl(s,terms){s=String(s??"");const n=norm(s);let marks=[];terms.forEach(t=>{let i=0;while(t&&(i=n.indexOf(t,i))>-1){marks.push([i,i+t.length]);i+=t.length}});
 if(!marks.length)return esc(s);marks.sort((a,b)=>a[0]-b[0]);let out="",pos=0;marks.forEach(([a,b])=>{if(a<pos)return;out+=esc(s.slice(pos,a))+"<mark>"+esc(s.slice(a,b))+"</mark>";pos=b});return out+esc(s.slice(pos))}
const WHO=/who.?s who|contemporary worthies/i;
let TB=null,DR=null,CH=null;
async function loadTables(){if(TB)return TB;$("#status").textContent="Loading tables…";
 TB=(await Promise.all(BOOKS.map(b=>fetch("data/"+b.slug+".json").then(r=>r.json()).then(ts=>ts.map(t=>{
  const rows=(t.parts||[]).flatMap(p=>p.rows||[]);
  return {b,t,rows,head:norm([t.title,t.table_no,t.chapter,t.caption_extra].join(" ")),all:norm([t.title,t.table_no,t.chapter,t.caption_extra,t.context,...(t.parts||[]).flatMap(p=>[p.label,...(p.columns||[])]),...rows.map(r=>r.join(" ")),...(t.footnotes||[])].join(" \n "))}}))))).flat();return TB}
async function loadList(kind,flag){$("#status").textContent="Loading "+(kind==="directory"?"directories":"chronologies")+"…";
 return (await Promise.all(BOOKS.filter(b=>b[flag]).map(b=>fetch("data/"+b.slug+"-"+kind+".json").then(r=>r.json()).then(es=>es.map(e=>({b,e,n:norm(e.n),all:norm(e.n+" "+e.t+" "+e.s+" "+e.a)}))).catch(()=>[])))).flat()}
async function loadDirs(){return DR||(DR=await loadList("directory","dir"))}
async function loadChron(){return CH||(CH=await loadList("chronology","chron"))}
const LIMIT=400;
function tablesHTML(res,terms){const by={};res.slice(0,LIMIT).forEach(x=>(by[x.b.slug]=by[x.b.slug]||[]).push(x));let h="";
 BOOKS.forEach(b=>{const xs=by[b.slug];if(!xs)return;h+=`<div class="bk">${esc(b.title)} · ${xs.length}</div>`;
  xs.forEach(x=>{const t=x.t;const lab=(t.table_no?`Table ${t.table_no}. `:"")+(t.title||"");
   const hits=x.rows.filter(r=>terms.some(w=>norm(r.join(" ")).includes(w))).slice(0,3);
   h+=`<div class="r"><a class="t" href="book/${b.slug}/#${encodeURIComponent(t.id)}">${hl(lab,terms)}</a><div class="m">${esc(t.chapter||"")} · p. ${esc((t.printed_pages||[]).join(", "))}${(t.scans||[])[0]&&t.scans[0].url?` · <a href="${t.scans[0].url}" target="_blank" rel="noopener">scan</a>`:""}</div>`+
    (hits.length?`<div class="snip">${hits.map(r=>`<div>${r.map(c=>hl(c,terms)).join(" · ")}</div>`).join("")}</div>`:"")+`</div>`})});return h}
function entriesHTML(res,terms,page,q){const by={};res.slice(0,LIMIT).forEach(x=>(by[x.b.slug]=by[x.b.slug]||[]).push(x));let h="";
 BOOKS.forEach(b=>{const xs=by[b.slug];if(!xs)return;h+=`<div class="bk">${esc(b.title)} · ${xs.length} · <a href="book/${b.slug}/${page}#${new URLSearchParams({q}).toString()}">open in book</a></div>`;
  xs.forEach(({e})=>{h+=`<div class="r"><b>${hl(e.n,terms)}</b> <span class="snip">${hl(e.t,terms)}</span><div class="m">${esc(e.a)}${e.s?" — "+esc(e.s):""} · p. ${esc(e.p)}${e.u?` · <a href="${e.u}" target="_blank" rel="noopener">${esc(e.l)}</a>`:e.l?" · "+esc(e.l):""}</div></div>`})});return h}
const match=(xs,terms)=>xs.filter(x=>terms.every(w=>x.all.includes(w)));
const count=(n,one,many)=>`${n.toLocaleString()} ${n===1?one:many}${n>LIMIT?` (showing ${LIMIT})`:""}`;
async function run(){const q=$("#q").value.trim(),sc=$("#scope").value;const terms=norm(q).split(/\s+/).filter(Boolean);
 try{history.replaceState(null,"",q||sc!=="all"?"#"+new URLSearchParams({q,s:sc}).toString():location.pathname)}catch(e){}
 if(!terms.length){$("#status").textContent="Type to search.";$("#out").innerHTML="";return}
 const parts=[],stat=[];
 if(sc==="all"||sc==="t"){const res=match(await loadTables(),terms);res.sort((a,b)=>terms.filter(w=>b.head.includes(w)).length-terms.filter(w=>a.head.includes(w)).length);
  stat.push(count(res.length,"table","tables"));if(res.length)parts.push((sc==="all"?`<div class="kind">Tables</div>`:"")+tablesHTML(res,terms))}
 if(sc==="all"||sc==="d"||sc==="w"){let res=match(await loadDirs(),terms);if(sc==="w")res=res.filter(x=>WHO.test(x.e.a));
  res.sort((a,b)=>terms.filter(w=>b.n.includes(w)).length-terms.filter(w=>a.n.includes(w)).length);
  stat.push(count(res.length,sc==="w"?"Who's Who entry":"directory entry",sc==="w"?"Who's Who entries":"directory entries"));
  if(res.length)parts.push((sc==="all"?`<div class="kind">Who's Who &amp; directories</div>`:"")+entriesHTML(res,terms,"directory.html",q))}
 if(sc==="all"||sc==="c"){const res=match(await loadChron(),terms);stat.push(count(res.length,"chronology event","chronology events"));
  if(res.length)parts.push((sc==="all"?`<div class="kind">Chronologies</div>`:"")+entriesHTML(res,terms,"chronology.html",q))}
 if(norm($("#q").value.trim())!==norm(q)||$("#scope").value!==sc)return;
 $("#status").textContent=stat.join(" · ");$("#out").innerHTML=parts.join("")||"<p>No matches.</p>"}
let tm;$("#q").addEventListener("input",()=>{clearTimeout(tm);tm=setTimeout(run,200)});$("#scope").addEventListener("change",run);
$("#toggle").addEventListener("click",()=>{const r=document.documentElement;const d=r.dataset.theme?r.dataset.theme==="dark":matchMedia("(prefers-color-scheme: dark)").matches;r.dataset.theme=d?"light":"dark"});
try{const p=new URLSearchParams(location.hash.slice(1));$("#q").value=p.get("q")||p.get("t")||p.get("d")||"";const sc=p.get("s")||(p.get("tab")==="d"?"d":"all");if([...$("#scope").options].some(o=>o.value===sc))$("#scope").value=sc}catch(e){}
run();
</script></body></html>
"""

if __name__ == "__main__":
    main()
