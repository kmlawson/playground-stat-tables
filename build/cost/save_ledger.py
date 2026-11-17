"""Step 2 of the cost page: merge what parse_logs.py found into the durable ledger build/cost/ledger.json.

Claude Code transcripts do not last: sub-agent transcripts are deleted after each book (CLAUDE.md, clean-up) and old
session logs are pruned. The ledger keeps, for good, every sub-agent launch (book, model, date, task, final context
size, tool calls, duration, and its exact token usage while its transcript still exists) and every session's
orchestrator usage per book and model. Run it BEFORE deleting any transcript:

    nice -n 15 python3 build/cost/parse_logs.py && python3 build/cost/save_ledger.py && python3 build/cost/make_page.py

Merging never loses information: an agent's exact usage, once saved, is kept when its transcript is gone; a
session's orchestrator figures are replaced only by a later, larger reading of the same session.
Session ids are stored as short hashes; nothing in the ledger identifies the user."""
import json, os, hashlib
HERE = os.path.dirname(os.path.abspath(__file__))
LEDGER = os.path.join(HERE, 'ledger.json')
D = json.load(open(os.path.expanduser('~/.cache/stat-tables-cost/parsed.json')))
L = json.load(open(LEDGER)) if os.path.exists(LEDGER) else {'agents': {}, 'orch': {}}
h = lambda sid: hashlib.sha1(sid.encode()).hexdigest()[:10]
LONG = 100_000                                   # Haiku is priced higher on requests with longer prompts

new = exact = 0
for tid, a in D['agents'].items():
    r = L['agents'].get(tid)
    if r is None: r = L['agents'][tid] = {}; new += 1
    r.update(ts=a.get('ts') or r.get('ts'), s=h(a['sid']), book=a['book'], model=a['model'], desc=a.get('desc'))
    if a.get('fin'): r['fin'] = a['fin']         # [final context tokens, tool calls, duration ms] from the completion notice
    sub = D['sub'].get(a.get('aid'))
    if sub:                                      # exact usage [input, write 5m, write 1h, cache read, output]
        lo = [0] * 5; hi = [0] * 5
        for x in sub['msgs']:
            t = hi if x[0] + x[1] + x[2] + x[3] > LONG else lo
            for j in range(5): t[j] += x[j]
        if not r.get('use') or sum(lo) + sum(hi) >= sum(r['use']['lo']) + sum(r['use']['hi']):
            r['use'] = dict(model=sub['model'], n=len(sub['msgs']), lo=lo, hi=hi)
    if r.get('use'): exact += 1
tot = lambda e: sum(sum(u) for b in e.values() for u in b['u'].values())
for sid, e in D.get('orch_sessions', {}).items():
    k = h(sid)
    if k not in L['orch'] or tot(e) >= tot(L['orch'][k]): L['orch'][k] = e
tmp = LEDGER + '.tmp'
json.dump(L, open(tmp, 'w'), ensure_ascii=False, separators=(',', ':'), sort_keys=True)
os.replace(tmp, LEDGER)
by = {}
for r in L['agents'].values(): by[r['model']] = by.get(r['model'], 0) + 1
print(f"ledger: {len(L['agents'])} agent launches ({new} new, {exact} with exact usage) {by}; {len(L['orch'])} sessions; "
      f"{os.path.getsize(LEDGER) // 1024} KB")
