"""Survey old romanisations in OUR English layer and check each against the source table's own characters.

Scope: build/translations/<slug>.json only — fields 't', 'd' and '_chapters' values. Never reads or writes
transcriptions except to look up the characters a table prints. Makes no edits.

Usage: python3 build/romanisation/survey.py [OUT_DIR]   (writes OUT_DIR/report.tsv; default: current directory)
Status per use: OK (expected characters found), ALT:x (only another reading's characters found), BOTH:x,
NOTFOUND (characters absent — read the table before converting), NOSRC (no table file found).
"""
import glob, json, os, re, sys, collections
SITE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ROOT = os.path.dirname(SITE)
CONV = json.load(open(os.path.join(SITE, 'build/romanisation/conversions.json')))['conversions']
out_dir = sys.argv[1] if len(sys.argv) > 1 else '.'
dirs = dict(re.findall(r'"slug":\s*"([^"]+)",\s*"dir":\s*"([^"]+)"', open(SITE + '/build/build_site.py').read()))
forms = sorted(CONV, key=lambda c: -len(c['from']))
rx = re.compile(r'(?<![\w-])(' + '|'.join(re.escape(c['from']) for c in forms) + r')(?![\w])')
by = {c['from']: c for c in CONV}

def flat(x):
    if isinstance(x, str): return x
    if isinstance(x, dict): return ' '.join(flat(v) for v in x.values())
    if isinstance(x, list): return ' '.join(flat(v) for v in x)
    return str(x)

rows, stat = [], collections.defaultdict(collections.Counter)
for f in sorted(glob.glob(SITE + '/build/translations/*.json')):
    slug = os.path.basename(f)[:-5]; d = json.load(open(f))
    tdir = f"{ROOT}/{dirs.get(slug, '?')}/_work/tables"
    items = [('_ch:' + ch, 'ch', en, ch) for ch, en in d.get('_chapters', {}).items()]
    items += [(k, fld, v[fld], None) for k, v in d.items() if k != '_chapters' and isinstance(v, dict)
              for fld in ('t', 'd') if isinstance(v.get(fld), str)]
    for k, fld, text, ch in items:
        toks = list(dict.fromkeys(m.group(1) for m in rx.finditer(text)))
        if not toks: continue
        if ch is not None: cjk = ch
        else:
            p = f"{tdir}/{k}.json"
            if not os.path.exists(p): p = next(iter(glob.glob(f"{tdir}/**/{k}.json", recursive=True)), None)
            cjk = flat(json.load(open(p))) if p else ''
        for tok in toks:
            c = by[tok]
            hit = bool(c['chars']) and bool(re.search(c['chars'], cjk))
            alts = [a for a, chars in c['alt'].items() if re.search(chars, cjk)]
            st = ('NOSRC' if not cjk else 'OK' if hit and not alts else 'BOTH:' + '/'.join(alts) if hit
                  else 'ALT:' + '/'.join(alts) if alts else 'NOTFOUND' if c['chars'] else 'OK')
            stat[tok][st.split(':')[0]] += 1
            rows.append((st, slug, k, fld, tok, c['to'], text))
with open(os.path.join(out_dir, 'report.tsv'), 'w') as o:
    for r in sorted(rows): o.write('\t'.join(r) + '\n')
for tok, s in sorted(stat.items(), key=lambda t: -sum(t[1].values())):
    print(f"{tok:16} → {by[tok]['to']:12} " + ' '.join(f"{k}:{n}" for k, n in s.items()))
print(len(rows), 'uses; report:', os.path.join(out_dir, 'report.tsv'))
print("Also check by hand: build/romanisation/conversions.json 'terms' (Hsien etc.) and 'false_hits'.")
