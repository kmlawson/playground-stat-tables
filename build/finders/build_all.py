"""Build every finder page (build/finders/<name>/) and the hub figures/index.html. Run by build_site.py at the end of
a build (after index.html and the topic pages exist); can also be run alone:

    python3 build/finders/build_all.py

Each finder folder has config.json and build_<name>.py with main(chrome) -> summary dict. See build/finders/README.md.
"""
import html, importlib.util, json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
SITE = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import registry  # noqa: E402


def chrome(prefix="../"):
    """Styles, header band and footer of the home page (index.html), for a page `prefix` below the site root. The
    home page's sort and view tools, which act on its list of books, are left out; its section links point back to it."""
    s = open(os.path.join(SITE, "index.html"), encoding="utf-8").read()
    style = s[s.index("<style>") + 7:s.index("</style>")]
    band = s[s.index('<div class="band">'):s.index("<main>")]
    band = re.sub(r'<span class="tools">.*?</span></span>(?=</div>)', "", band, flags=re.S)
    band = band.replace(' id="jump"', "").replace(' id="j-japan"', "").replace(' id="j-china"', "")
    band = re.sub(r'href="#', 'href="index.html#', band)
    band = re.sub(r'href="(?!https?:|#|/)', 'href="' + prefix, band)
    foot = s[s.index("<footer>"):s.index("</footer>") + 9]
    head = s[:s.index("<title>")]
    return head, style, band, foot


HUB = """__HEAD__<title>Find figures · Old Tables of East Asia</title>
<meta name="description" content="Pages that gather one kind of figure from every table on the site, place by place and year by year.">
<style>
__STYLE__
.fcards{display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:16px;margin:18px 0 30px}
.fcard{display:block;background:var(--panel);border:1px solid var(--line);border-top:3px solid var(--accent);padding:16px 18px;color:var(--ink);text-decoration:none}
.fcard:hover{border-color:var(--accent)}.fcard b{display:block;font-weight:normal;font-size:21px;margin-bottom:4px}.fcard small{display:block;color:var(--muted);font-size:13.5px;margin-top:8px}
.crumbs{font-size:14px;color:var(--muted);margin:0 0 8px}.crumbs a{color:var(--accent);text-decoration:none}
</style></head><body>__BAND__
<main>
<div class="crumbs"><a href="../topics/index.html">Topics</a> › Find figures</div>
<h2 style="font-weight:normal;font-size:28px;margin:4px 0 6px">Find figures</h2>
<p class="lede" style="max-width:760px">Each of these pages gathers one kind of figure from every table on the site, place by place and year by year. Where several tables print the same figure it is shown once, with a link to each table; where they disagree, the figures are shown side by side.</p>
<div class="fcards">__CARDS__</div>
<div class="llmwarn" role="note"><b>Warning:</b> These tables were transcribed by the vision models of Opus 5.5, Sonnet 5.5, or Haiku 5.5 (named on each book's page), and the figures on these pages were gathered from them by machine. Before using any of these figures, you must verify specific statistics with the original source which is linked to whenever possible.</div>
__FOOT__
</main></body></html>
"""


def main():
    done = []
    for c in registry.finders():
        mod_path = os.path.join(c["dir"], f"build_{c['name']}.py")
        spec = importlib.util.spec_from_file_location(f"finder_{c['name']}", mod_path)
        mod = importlib.util.module_from_spec(spec)
        sys.path.insert(0, c["dir"])
        spec.loader.exec_module(mod)
        summary = mod.main(chrome) or {}
        done.append((c, summary))
    head, style, band, foot = chrome("../")
    cards = "".join(f'<a class="fcard" href="{html.escape(os.path.basename(c["page"]))}"><b>{html.escape(c["title"])}</b>{html.escape(c["blurb"])}'
                    f'<small>{s.get("n", 0):,} figures from {s.get("tables", 0):,} tables · {s.get("places", 0):,} places</small></a>'
                    for c, s in done)
    os.makedirs(os.path.join(SITE, "figures"), exist_ok=True)
    page = HUB.replace("__HEAD__", head).replace("__STYLE__", style).replace("__BAND__", band).replace("__FOOT__", foot).replace("__CARDS__", cards)
    open(os.path.join(SITE, "figures", "index.html"), "w", encoding="utf-8").write(page)
    return done


if __name__ == "__main__":
    main()
