"""Step 2 of the cost page: price the usage recorded by parse_logs.py and write support/cost.html.
Usage: python3 build/cost/make_page.py

Orchestrator turns and sub-agents whose own transcripts survive are priced exactly from their recorded usage.
Sub-agents whose transcripts were deleted are estimated from the size of their final context (F) and number of tool
calls (N) printed in their completion notice, with ratios fitted on the sub-agents whose transcripts survive."""
import json, os, re, sys, collections, datetime
HERE = os.path.dirname(os.path.abspath(__file__))
SITE = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(SITE, 'build'))
import build_site as B
D = json.load(open(os.path.expanduser('~/.cache/stat-tables-cost/parsed.json')))
ADDED = json.load(open(os.path.join(SITE, 'build', 'added_dates.json')))

# USD per million tokens, API list prices (Nov 2026). w5/w1 = cache writes with 5-minute / 1-hour lifetime.
PRICE = {
    'claude-opus-5-5':   dict(i=4.0, o=20.0, cr=0.20, w5=5.0, w1=8.0),
    'claude-sonnet-5-5': dict(i=2.0, o=10.0, cr=0.20, w5=2.5, w1=4.0),
    'claude-haiku-5-5':  dict(i=0.10, o=0.50, cr=0.01, w5=0.125, w1=0.20),   # requests with prompts <= 100K tokens
    'claude-haiku-5-5+': dict(i=0.50, o=2.50, cr=0.05, w5=0.625, w1=1.00),   # requests with longer prompts
}
LABEL = {'claude-opus-5-5': 'Opus', 'claude-sonnet-5-5': 'Sonnet', 'claude-haiku-5-5': 'Haiku'}

def cost(model, t):          # t = [input, write5m, write1h, cache_read, output]
    if model == 'claude-haiku-5-5' and t[0] + t[1] + t[2] + t[3] > 100_000: model += '+'
    p = PRICE.get(model, PRICE['claude-opus-5-5'])
    return (t[0] * p['i'] + t[1] * p['w5'] + t[2] * p['w1'] + t[3] * p['cr'] + t[4] * p['o']) / 1e6

# ---- calibration: sub-agents with both a surviving transcript and a completion notice
cal = collections.defaultdict(lambda: [0, 0, 0, 0, 0, 0])   # model -> [sumF, sumFN, read, write, out, n]
for a in D['agents'].values():
    s = D['sub'].get(a.get('aid'))
    if not s or not a.get('fin'): continue
    F, N, _ = a['fin']; c = cal[s['model']]
    c[0] += F; c[1] += F * N; c[5] += 1
    for x in s['msgs']: c[2] += x[3]; c[3] += x[1] + x[2] + x[0]; c[4] += x[4]
RATIO = {m: dict(read=c[2] / c[1], write=c[3] / c[0], out=c[4] / c[0], n=c[5]) for m, c in cal.items() if c[5] >= 20}
RATIO['claude-haiku-5-5'] = RATIO['claude-sonnet-5-5']

def estimate(model, F, N):
    r = RATIO.get(model, RATIO['claude-opus-5-5'])
    read, write, out = r['read'] * F * N, r['write'] * F, r['out'] * F
    if model != 'claude-haiku-5-5':
        return cost(model, [0, write, 0, read, out])
    # Haiku is dearer per token once a request's prompt passes 100K: the context grows roughly linearly, so the share
    # of cache reads above 100K is 1 - (100K/F)^2 and of writes and output (100K..F)/F.
    hi_r = max(0.0, 1 - (1e5 / F) ** 2) if F else 0; hi_l = max(0.0, (F - 1e5) / F) if F else 0
    lo, hi = PRICE['claude-haiku-5-5'], PRICE['claude-haiku-5-5+']
    return (read * ((1 - hi_r) * lo['cr'] + hi_r * hi['cr']) + write * ((1 - hi_l) * lo['w5'] + hi_l * hi['w5'])
            + out * ((1 - hi_l) * lo['o'] + hi_l * hi['o'])) / 1e6

# ---- books: one row per working folder (some folders hold several site volumes)
REGION = [('japan', 'Japan'), ('china', 'China'), ('korea', 'Korea'), ('taiwan', 'Taiwan'), ('nanyo', 'South Seas'),
          ('mandate', 'South Seas'), ('gyosei', 'South Seas'), ('manch', 'Manchuria'), ('daitoa', 'Japan'),
          ('far', 'East Asia'), ('pacific', 'East Asia')]
def region(slug):
    for p, r in REGION:
        if slug.startswith(p): return r
    return 'Other'
def ntables(slug):
    try:
        d = json.load(open(os.path.join(SITE, 'data', slug + '.json')))
        return len(d) if isinstance(d, list) else len(d.get('tables', []))
    except Exception: return 0
info = {}
for b in B.BOOKS:
    d = b['dir'] if re.match(r'^[A-Za-z][\w-]{3,}$', b.get('dir') or '') else b['slug']
    r = info.setdefault(d, dict(slugs=[], titles=[], tables=0, added=None, made='', region=region(b['slug'])))
    r['slugs'].append(b['slug']); r['titles'].append(b['title']); r['tables'] += ntables(b['slug'])
    a = ADDED.get(b['slug'])
    if a and (not r['added'] or a < r['added']): r['added'] = a
    if b.get('model') and b['model'] not in r['made']: r['made'] = (r['made'] + '; ' if r['made'] else '') + b['model']

rows = collections.defaultdict(lambda: dict(orch=0.0, exact=0.0, est=0.0, n=collections.Counter(), cost_m=collections.Counter(),
                                             nexact=0, nest=0, nnone=0, ts=[], sessions=set()))
for bk, per in D['orch'].items():
    r = rows[bk]
    for m, t in per.items(): r['orch'] += cost(m, t)
    r['ts'] += D['orch_ts'][bk]; r['sessions'] |= set(D['sessions'][bk])
for a in D['agents'].values():
    r = rows[a['book']]; m = a['model']; s = D['sub'].get(a.get('aid'))
    r['n'][m] += 1; r['ts'].append(a['ts']); r['sessions'].add(a['sid'])
    if s:
        c = sum(cost(s['model'], x) for x in s['msgs']); r['exact'] += c; r['nexact'] += 1; r['cost_m'][s['model']] += c
    elif a.get('fin'):
        c = estimate(m, a['fin'][0], a['fin'][1]); r['est'] += c; r['nest'] += 1; r['cost_m'][m] += c
    else:
        r['nnone'] += 1

all_ts = sorted(t for r in rows.values() for t in r['ts'] if t)
LOG_START = all_ts[0]
def day(ts): return ts[:10] if ts else ''
start_dt = datetime.datetime.fromisoformat(LOG_START.replace('Z', '+00:00'))
out = []
for bk, r in rows.items():
    i = info.get(bk)
    ts = sorted(t for t in r['ts'] if t)
    first = ts[0] if ts else ''
    if bk == 'other':
        status, title = 'other', 'Site-wide and other work (not tied to one book)'
    elif not i:
        status, title = 'unpublished', bk.replace('_', ' ')
    else:
        title = ' / '.join(dict.fromkeys(i['titles']))
        added = i['added'] and datetime.datetime.fromisoformat(i['added']).astimezone(datetime.timezone.utc)
        f = datetime.datetime.fromisoformat(first.replace('Z', '+00:00')) if first else None
        if added and added < start_dt + datetime.timedelta(hours=12):
            status = 'before' if r['orch'] + r['exact'] + r['est'] < 20 else 'partial'
        elif f and f < start_dt + datetime.timedelta(hours=24): status = 'partial'
        else: status = 'full'
    total = r['orch'] + r['exact'] + r['est']
    if total < 0.005 and not sum(r['n'].values()): continue
    out.append(dict(
        k=bk, t=title, s=(i or {}).get('slugs', []), rg=(i or {}).get('region', '') if bk != 'other' else '',
        tb=(i or {}).get('tables', 0), ad=day((i or {}).get('added')), f=day(first), l=day(ts[-1] if ts else ''),
        mk=(i or {}).get('made', ''), st=status,
        o=round(r['orch'], 2), ae=round(r['exact'], 2), aq=round(r['est'], 2), c=round(total, 2),
        nO=r['n']['claude-opus-5-5'], nS=r['n']['claude-sonnet-5-5'], nH=r['n']['claude-haiku-5-5'],
        cO=round(r['cost_m']['claude-opus-5-5'], 2), cS=round(r['cost_m']['claude-sonnet-5-5'], 2), cH=round(r['cost_m']['claude-haiku-5-5'], 2),
        x=r['nexact'], e=r['nest'], z=r['nnone'], ss=len(r['sessions'])))
out.sort(key=lambda r: (r['l'], r['c']), reverse=True)

meta = dict(start=day(LOG_START), end=day(all_ts[-1]), sessions=len({s for r in rows.values() for s in r['sessions']}),
            agents=len(D['agents']), exact=sum(r['x'] for r in out), est=sum(r['e'] for r in out), none=sum(r['z'] for r in out),
            ratio={LABEL.get(m, m): {k: round(v, 3) for k, v in r.items()} for m, r in RATIO.items() if m != 'claude-haiku-5-5'},
            built=datetime.date.today().isoformat())
tpl = open(os.path.join(HERE, 'cost_template.html'), encoding='utf-8').read()
html = tpl.replace('__DATA__', json.dumps(out, ensure_ascii=False, separators=(',', ':'))).replace('__META__', json.dumps(meta))
with open(os.path.join(SITE, 'support', 'cost.html'), 'w', encoding='utf-8') as fh: fh.write(html)
print(len(out), 'rows; total $%.0f; exact %d, estimated %d, no record %d agents' % (sum(r['c'] for r in out), meta['exact'], meta['est'], meta['none']))
print('ratios', meta['ratio'])
