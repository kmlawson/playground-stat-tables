"""Figures that look like a spec mistake rather than a real disagreement, for a person or agent to look at.

    python3 build/finders/population/check.py  ->  build/population/work/outliers.txt

A figure is listed when, for the same place, count and group, it is under 1/4 or over 4x the median of the figures
within 15 years of it (a wrong column, households read as people, a group read as everyone, thousands not multiplied).
Nothing is changed: the answer is a fix to the table's spec.
"""
import os, re, statistics, sys
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import extract as X  # noqa: E402
import build_population as BP  # noqa: E402
import make_previews as MP  # noqa: E402


def outliers():
    """[(src, claim, nearby median)] for figures under 1/4 or over 4x the median of their neighbours."""
    B = MP.books()
    claims, made, _, _ = X.claims(X.load_specs(), {s: BP.edition_year(b) for s, b in B.items()})
    series = defaultdict(list)
    for c in claims:
        series[(c["place"], c["m"], c["g"])].append(c)
    out = []
    for k, cs in series.items():
        if len(cs) < 3:
            continue
        for c in cs:
            near = [d["v"] for d in cs if abs(d["year"] - c["year"]) <= 15 and d is not c]
            if len(near) < 2:
                continue
            med = statistics.median(near)
            if c["v"] < med / 4 or c["v"] > med * 4:
                out.append((c["src"], c, med))
    return out


def key(c):
    """A figure's identity across builds: table, part, row, column."""
    return f"{c['src']}|{c['part']}.{c['row']}.{c['col']}"


def main():
    out = outliers()
    by = defaultdict(list)
    for src, c, med in out:
        by[src].append((c, med))
    with open(os.path.join(HERE, "work", "outliers.txt"), "w") as fh:
        for src, L in sorted(by.items()):
            fh.write(f"## {src} ({len(L)} suspicious)\n")
            for c, med in L[:6]:
                fh.write(f"  r{c['row']} c{c['col']} part{c['part']}: {c['label']!r} {c['m']}/{c['g']} {c['date']} = {c['v']:,}  (nearby median {int(med):,}; place {c['place']})\n")
    print(len(out), "suspicious figures in", len(by), "tables -> work/outliers.txt")


if __name__ == "__main__":
    main()
