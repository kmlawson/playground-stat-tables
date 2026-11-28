"""Convert old romanisations to the current rule in OUR English layer only.

Scope: build/translations/<slug>.json — fields 't', 'd' and '_chapters' values. NEVER transcriptions
(tables/, directory/, chronology/, toc.json): they keep the printed romanisation (CLAUDE.md hard rule).

Usage: python3 build/romanisation/convert.py [--write] [--only slug1,slug2]
Without --write: preview only, writes ./changes.tsv (slug, key, field, old, new). Review it (word-level) first.
Run survey.py before, and resolve every NOTFOUND/ALT/BOTH use with an entry in SPECIFIC below.
First run: 2026-11-28, 513 strings in 28 files (China/Manchuria Wade-Giles → pinyin).
"""
import glob, json, os, re, sys
SITE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CONV = json.load(open(os.path.join(SITE, 'build/romanisation/conversions.json')))['conversions']
WRITE = '--write' in sys.argv
ONLY = set(sys.argv[sys.argv.index('--only') + 1].split(',')) if '--only' in sys.argv else None

# Entry-specific rewrites, decided against the source tables (applied once; skipped if already applied).
SPECIFIC = {
 ('china-tongji-1935', 'p0749_1', 't'): [('via the Kiangsu Customs', 'via the Jianghai Customs')],   # 江海關
 ('china-tongji-1935', 'p0749_1', 'd'): [('through the Shanghai (Kiangsu) customs', 'through the Jianghai Customs (Shanghai)')],
 ('china-tongji-1947', 'p0132_1', 't'): [('Numbers of Hsiang (or Chen), Pao and Chia', 'Numbers of Townships (or Towns), Bao and Jia')],
 ('china-tongji-1947', 'p0132_1', 'd'): [('Number of hsiang or chen, pao and chia', 'Number of townships or towns, bao and jia')],
 ('manchukuo-tekiyo-1940', 'p0097_1', 'd'): [('Public granaries (Yi-tsang)', 'Charity granaries (yicang)')],   # 義倉
 ('manchukuo-tekiyo-1940', 'p0098_1', 'd'): [('Public granaries (Yi-tsang)', 'Charity granaries (yicang)')],
 ('china-education-1934', 'p0233_2', 'd'): [('(eight hsien, one private)', '(eight county-run, one private)')],
 ('china-education-1934', 'p0783_2', 'd'): [('hsien bureaux), hsien that did', 'county bureaux), counties that did')],
}
# 縣 → county/counties, by phrase (order matters). 'mien-hsien' (麵線, noodles) is protected by the (?<![\w-]).
HSIEN = [
 ('Kiangning Hsien', 'Jiangning County'), ('Shansi Hsien 1933', 'Shansi Counties 1933'), ('Hsien-run', 'County-run'),
 ('Hsien and Municipalities', 'Counties and Municipalities'), ('Hsien and Cities', 'Counties and Cities'),
 ('Hsien Attached to', 'Counties Attached to'), ('Hsien of', 'Counties of'), ('Hsien in Szechwan', 'Counties in Szechwan'),
 ('Hsien Without', 'Counties Without'), ('Provincial and Hsien', 'Provincial and County'),
 ('Self-Government by Hsien', 'Self-Government by County'), ('nine Szechwan hsien', 'nine Szechwan counties'),
 ('number of hsien', 'number of counties'), ('provinces and hsien grouped', 'provinces and counties grouped'),
 ('hsien, cities and bureaux', 'counties, cities and bureaux'), ('its hsien and cities', 'its counties and cities'),
 ('municipalities, hsien and other', 'municipalities, counties and other'), ('hsien/municipal', 'county/municipal'),
 ('By hsien', 'By county'), ('by hsien', 'by county'),
 ('hsien', 'county'),   # last resort: attributive/singular uses — check every one in the preview
]
TOKRX = [(re.compile(r'(?<![\w-])' + re.escape(c['from']) + r'(?![\w])'), c['to'])
         for c in sorted(CONV, key=lambda c: -len(c['from']))]

def convert(slug, key, fld, s):
    for old, new in SPECIFIC.get((slug, key, fld), []):
        if old in s: s = s.replace(old, new)
    if re.search(r'(?<![\w-])hsien\b', s, re.I):
        for old, new in HSIEN: s = re.sub(r'(?<![\w-])' + re.escape(old) + r'\b', new, s)
        assert not re.search(r'(?<![\w-])hsien\b', s, re.I), (slug, key, s)
    for rx, new in TOKRX: s = rx.sub(new, s)
    return s

def fmt_of(raw, d):
    for ind in (1, 2, None, 0):
        for ea in (False, True):
            s = json.dumps(d, ensure_ascii=ea, indent=ind)
            if s == raw: return (ind, ea, '')
            if s + '\n' == raw: return (ind, ea, '\n')
    return None   # hand-formatted file: patch the raw text instead

changes = []
for f in sorted(glob.glob(SITE + '/build/translations/*.json')):
    slug = os.path.basename(f)[:-5]
    if ONLY and slug not in ONLY: continue
    raw = open(f).read(); d = json.loads(raw); fmt = fmt_of(raw, d); newraw = raw; n = 0
    def apply(key, fld, old, setter):
        global newraw, n
        new = convert(slug, key, fld, old)
        if new == old: return
        changes.append((slug, key, fld, old, new)); setter(new); n += 1
        newraw = newraw.replace(json.dumps(old, ensure_ascii=False), json.dumps(new, ensure_ascii=False))
    for k, v in d.items():
        if k == '_chapters':
            for ch in list(v): apply('_ch:' + ch, 'ch', v[ch], lambda x, ch=ch: v.__setitem__(ch, x))
        elif isinstance(v, dict):
            for fld in ('t', 'd'):
                if isinstance(v.get(fld), str): apply(k, fld, v[fld], lambda x, v=v, fld=fld: v.__setitem__(fld, x))
    if n and WRITE:
        out = json.dumps(d, ensure_ascii=fmt[1], indent=fmt[0]) + fmt[2] if fmt else newraw
        assert json.loads(out) == d, slug
        open(f, 'w').write(out)
with open('changes.tsv', 'w') as o:
    for c in changes: o.write('\t'.join(c) + '\n')
print(len(changes), 'strings in', len({c[0] for c in changes}), 'files', '(WRITTEN)' if WRITE else '(preview → ./changes.tsv)')
