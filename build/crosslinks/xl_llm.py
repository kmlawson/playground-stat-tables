"""xl_llm.py <series> [--new slug,slug,...] [--run N]: match recurring tables with Sonnet through the llm CLI, one call per
listing. Writes llm_jobs/<series>/<listing>.prompt (task + existing families + listing), runs them (../../../../_pipeline/run.py),
then merges each reply into families/<listing>.json, keeping existing members (update mode) and checking every member."""
import json, os, re, sys, glob, subprocess
H = os.path.dirname(os.path.abspath(__file__)); ser = sys.argv[1]
new = sys.argv[sys.argv.index('--new') + 1].split(',') if '--new' in sys.argv else []
N = int(sys.argv[sys.argv.index('--run') + 1]) if '--run' in sys.argv else 8
RUN = os.path.abspath(os.path.join(H, '..', '..', '..', '_pipeline', 'run.py'))
D = os.path.join(H, '..', '..', 'data')
TASK = '''You are matching recurring statistical tables across editions of the same series, so a website can link "similar tables" between editions and show them side by side.
Below is one LISTING: every table in one topic from each edition, one line per table:
  slug | id | chapter | printed pages | title | caption | column headings | first-column row labels
{mode}
Same recurring table = same subject AND the same kind of breakdown (e.g. "population by prefecture", "imports by country", "births by year") AND comparable measures; years, units, title wording, column order, row counts and language may differ. NOT the same: a different breakdown, sub-population, region or unit of analysis. A family must span at least two editions; include two or more tables from one edition only when that edition split the same table into pieces. A table belongs to at most one family. Be conservative: a wrong link is worse than a missing one.
Return ONLY JSON (no prose, no fences): {{"families": [{{"label": "<short neutral English name>", "members": ["<slug>/<id>", ...], "note": ""}}]}} — ALL families for this listing (existing ones with any new members added, plus new ones), members copied exactly from the listing as slug/id, in edition order.
'''
UPD = 'EXISTING FAMILIES (keep every existing member in its family; do not remove or reshuffle; only add tables of the NEW editions {new} — to an existing family they match, or to a new family with a matching unplaced table):\n{fam}\n'
NEW = 'Build the families from scratch over all editions in the listing.\n'
os.makedirs(os.path.join(H, 'llm_jobs', ser), exist_ok=True); jobs = []
for lf in sorted(glob.glob(os.path.join(H, 'listings', ser + '--*.txt'))):
    x = os.path.basename(lf)[:-4]; ff = os.path.join(H, 'families', x + '.json')
    fam = json.load(open(ff)).get('families', []) if os.path.exists(ff) else []
    mode = UPD.format(new=', '.join(new), fam=json.dumps(fam, ensure_ascii=False)) if fam and new else NEW
    p = os.path.join(H, 'llm_jobs', ser, x + '.prompt'); open(p, 'w').write(TASK.format(mode=mode) + '\nLISTING:\n' + open(lf).read())
    jobs.append({'imgs': [], 'prompt_file': p, 'model': 'claude-sonnet-5.5', 'out': os.path.join(H, 'llm_jobs', ser, x + '.out')})
jf = os.path.join(H, 'llm_jobs', ser, 'jobs.json'); json.dump(jobs, open(jf, 'w'))
import concurrent.futures as cf, time
def go(j):
    if os.path.exists(j['out']) and os.path.getsize(j['out']) > 0: return 'skip'
    for t in range(5):
        r = subprocess.run(['llm', '-m', j['model'], '--no-stream', '--no-log', '-o', 'max_tokens', '32000'], input=open(j['prompt_file']).read(), capture_output=True, text=True, timeout=1800)
        if r.returncode == 0 and r.stdout.strip(): open(j['out'], 'w').write(r.stdout); return 'ok'
        time.sleep(30 * (t + 1))
    open(j['out'] + '.err', 'w').write(r.stderr[-500:]); return 'fail'
with cf.ThreadPoolExecutor(N) as ex: print(list(ex.map(go, jobs)).count('ok'), 'ok')
ids = {}
def ok(m):
    s, _, i = m.partition('/')
    if s not in ids:
        f = os.path.join(D, s + '.json'); ids[s] = {t['id'] for t in json.load(open(f))} if os.path.exists(f) else set()
    return i in ids[s]
tot = 0
for j in jobs:
    x = os.path.basename(j['out'])[:-4]; ff = os.path.join(H, 'families', x + '.json')
    try:
        s = open(j['out']).read(); s = s[s.find('{'):s.rfind('}') + 1]; got = json.loads(s)['families']
    except Exception as e: print('UNPARSED', x, e); continue
    old = json.load(open(ff)).get('families', []) if os.path.exists(ff) else []
    oldm = {m for f in old for m in f['members']}
    out = []; seen = set()
    for f in got:
        mem = [m for m in f.get('members', []) if ok(m) and (m not in seen or m in oldm)]
        seen |= set(mem)
        if len({m.split('/')[0] for m in mem}) >= 2: out.append({'label': f.get('label', ''), 'members': mem, 'note': f.get('note', '')})
    lost = oldm - {m for f in out for m in f['members']}
    if lost and new:  # the reply dropped existing members: keep the old families and add only new-edition-only families
        out = old + [f for f in out if not set(f['members']) & oldm]
    json.dump({'listing': x, 'families': out}, open(ff, 'w'), ensure_ascii=False, indent=1)
    tot += sum(len(f['members']) for f in out)
    print(x, len(out), 'families')
print('members', tot)
