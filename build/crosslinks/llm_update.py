"""llm_update.py build|write <series> <new slug> — Similar-tables update mode through the llm CLI (NU1.txt rules), for
books the user puts on the llm CLI (first used for japan-tokei-1930, 2026-11-26).
build: one job per listing of the series that holds tables of the new edition; the prompt carries the listing and the
existing families (numbered). The reply lists only additions, which write merges: existing families are never
reshuffled, members are kept in edition order, ids are checked against the listing."""
import glob, json, os, re, sys
H = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, H); import chapters as C
series, new = sys.argv[2], sys.argv[3]
BOOKS = C.SERIES[series]['books']; NAME = C.SERIES[series]['name']
J = f'{H}/llm_{new}'; os.makedirs(J, exist_ok=True)
PROMPT = """You are adding a newly finished edition to an existing cross-edition table matching, so a website can link "similar tables" between editions and show them side by side.

The listing below covers one topic of {NAME}; editions (slugs, in order): {BOOKS}. Table numbers differ between editions, so match on content, not number.
The NEW edition is {NEW}: its tables are the ones to place. Listing lines:  slug | id | chapter | printed pages | title | caption | column headings | first-column row labels

EXISTING FAMILIES (numbered; never remove or reshuffle them):
{FAMS}

For each table of {NEW}: add it to the existing family it matches, or create a new family with a matching table from another edition that is not yet in any family, or leave it out.
Same recurring table = same subject AND the same kind of breakdown (e.g. "population by prefecture", "imports by commodity", "births by year") AND comparable measures; years, units, title wording, column order and row counts may differ. Not the same: a different breakdown, a sub-population, a different measure. A table of the new edition goes into at most one family, and a family takes at most one table per edition.
Labels are short neutral English names; "note" only for something a reader should know.

Return ONLY a JSON object (no markdown fences):
{{"add": [{{"family": <number of the existing family>, "member": "{NEW}/<id>"}}], "new": [{{"label": "...", "members": ["<slug>/<id>", ...], "note": ""}}]}}

LISTING:
{LISTING}"""
if sys.argv[1] == 'build':
    jobs = []
    for lf in sorted(glob.glob(f'{H}/listings/{series}--*.txt')):
        L = open(lf).read()
        if new + ' |' not in L and f'{new} |' not in L and not re.search(rf'^{re.escape(new)}\s*\|', L, re.M): continue
        x = os.path.basename(lf)[:-4]; ff = f'{H}/families/{x}.json'
        fams = json.load(open(ff))['families'] if os.path.exists(ff) else []
        F = '\n'.join(f'{i}. {f["label"]}: ' + ', '.join(f['members']) for i, f in enumerate(fams)) or '(none yet)'
        jobs.append({'imgs': [], 'model': 'claude-sonnet-5.5', 'options': {'max_tokens': 64000}, 'stream': True, 'timeout': 3600, 'listing': x,
                     'prompt': PROMPT.format(NAME=NAME, BOOKS=', '.join(BOOKS), NEW=new, FAMS=F, LISTING=L), 'out': f'{J}/{x}.json'})
    json.dump(jobs, open(f'{J}/jobs.json', 'w'), ensure_ascii=False); print(len(jobs), 'jobs')
if sys.argv[1] == 'write':
    for j in json.load(open(f'{J}/jobs.json')):
        x = j['listing']; ff = f'{H}/families/{x}.json'
        D = json.load(open(ff)) if os.path.exists(ff) else {'listing': x, 'families': []}
        ids = set(re.findall(r'^(\S+) \| (\S+) \|', open(f'{H}/listings/{x}.txt').read(), re.M))
        ok = {f'{a}/{b}' for a, b in ids}
        s = open(j['out']).read().strip() if os.path.exists(j['out']) else ''; s = re.sub(r'^```(json)?\s*|\s*```$', '', s)
        try: r = json.loads(s[s.find('{'):])
        except Exception: print(x, 'unreadable reply'); continue
        used = {m for f in D['families'] for m in f['members']}; na = nn = bad = 0
        order = lambda m: (BOOKS.index(m.split('/')[0]), m)
        for a in r.get('add', []):
            m = a.get('member'); i = a.get('family')
            if m not in ok or m in used or not isinstance(i, int) or not 0 <= i < len(D['families']) \
               or any(y.split('/')[0] == m.split('/')[0] for y in D['families'][i]['members']): bad += 1; continue
            D['families'][i]['members'] = sorted(D['families'][i]['members'] + [m], key=order); used.add(m); na += 1
        for f in r.get('new', []):
            ms = [m for m in f.get('members', []) if m in ok and m not in used]
            if len(ms) < 2 or not any(m.startswith(new + '/') for m in ms) or len({m.split('/')[0] for m in ms}) < len(ms): bad += 1; continue
            D['families'].append({'label': f.get('label', ''), 'members': sorted(ms, key=order), 'note': f.get('note', '')}); used |= set(ms); nn += 1
        json.dump(D, open(ff, 'w'), ensure_ascii=False, indent=1)
        print(f'{x}: {na} added to families, {nn} new families, {bad} rejected')
