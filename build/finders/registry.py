"""The finder pages (build/finders/<name>/config.json) as the rest of the site sees them: the hub figures/index.html
links them, the Topics index lists them, their topic and tag pages get a banner, table pages and Full Search link
into them. Light on purpose (no gazetteer, no data): build_tags.py and build_site.py import it.
"""
import glob, html, json, os

HERE = os.path.dirname(os.path.abspath(__file__))
SITE = os.path.dirname(os.path.dirname(HERE))


def finders():
    out = []
    for f in sorted(glob.glob(os.path.join(HERE, "*", "config.json"))):
        c = json.load(open(f, encoding="utf-8"))
        c["dir"] = os.path.dirname(f)
        idx = os.path.join(SITE, c["data"], "index.json")
        c["_built"] = os.path.exists(idx)
        out.append(c)
    return out


BTN = ('display:inline-block;padding:8px 14px;border-radius:6px;background:var(--accent);color:var(--accent-ink);'
       'text-decoration:none;font-weight:600;font-size:15px;line-height:1.2')


def topics_buttons(prefix="../"):
    """Buttons for the Topics index, beside "Tables with Map"."""
    return "".join(f' <a href="{prefix}{c["page"]}" style="{BTN}" title="{html.escape(c["blurb"])}">{html.escape(c["title"])} figures →</a>'
                   for c in finders())


def banner(kind, ident, prefix="../"):
    """A short note on a topic or tag page that a finder page covers (kind: "topics" or "tags")."""
    out = ""
    for c in finders():
        if ident in (c.get("topic_ids") if kind == "topics" else c.get("tag_ids")) or []:
            out += (f'<p class="finder-note" style="margin:10px 0 14px;padding:10px 14px;border:1px solid var(--line);'
                    f'border-left:4px solid var(--accent);background:var(--panel);font-size:15px">{html.escape(c["banner"])} '
                    f'<a href="{prefix}{c["page"]}" style="font-weight:600;white-space:nowrap">{html.escape(c["title"])} page →</a></p>')
    return out


_LINKS = {}


def table_links(slug, prefix="../../"):
    """{table id: [[label, href, title]]} for one book: a link from each table to its place on each finder page."""
    out = {}
    for c in finders():
        if c["name"] not in _LINKS:
            p = os.path.join(c["dir"], "table_links.json")
            _LINKS[c["name"]] = json.load(open(p, encoding="utf-8")) if os.path.exists(p) else {}
        for tid, (pid, name) in _LINKS[c["name"]].get(slug, {}).items():
            out.setdefault(tid, []).append([f"{c['title']} across all books", f"{prefix}{c['page']}#p={pid}",
                                            f"Every {c['title'].lower()} figure for {name} in the site's tables, with the source of each"])
    return out
