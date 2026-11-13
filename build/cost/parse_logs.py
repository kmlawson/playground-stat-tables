"""Step 1 of the cost page (support/cost.html): read the surviving local Claude Code transcripts of this project
and record every orchestrator turn's token usage and every sub-agent launch, each assigned to a book.
Usage: nice -n 15 python3 build/cost/parse_logs.py   (about a minute) -> ~/.cache/stat-tables-cost/parsed.json
Then: python3 build/cost/make_page.py"""
import json, re, os, glob, sys, collections
HERE = os.path.dirname(os.path.abspath(__file__))
SITE = os.path.dirname(os.path.dirname(HERE))
ROOT = os.path.dirname(SITE) + '/'
sys.path.insert(0, os.path.join(SITE, 'build'))
P = os.path.expanduser('~/.claude/projects/') + re.sub(r'[^A-Za-z0-9]', '-', ROOT.rstrip('/')) + '/'
import build_site as B
OUT = os.path.expanduser('~/.cache/stat-tables-cost/parsed.json')
os.makedirs(os.path.dirname(OUT), exist_ok=True)

# ---- book keys: folder names (published or not), site slugs, NDL pids
keys = {}           # token -> dir
for b in B.BOOKS:
    ok = re.match(r'^[A-Za-z][\w-]{3,}$', b.get('dir') or '')     # some volumes live outside the folder tree ('.')
    d = b['dir'] if ok else b['slug']
    keys[b['slug']] = d
    if ok: keys[b['dir']] = d
    m = re.search(r'pid/(\d+)', b.get('item') or '')
    if m: keys['pid/' + m.group(1)] = d
for d in os.listdir(ROOT):
    if os.path.isdir(ROOT + d) and re.match(r'^[A-Z][A-Za-z]+_[A-Za-z0-9_]*\d', d):
        keys.setdefault(d, d)
toks = sorted(keys, key=len, reverse=True)
RX = re.compile(r'(?<![\w-])(' + '|'.join(re.escape(t) for t in toks) + r')(?![\w])')

def book_of(text):
    c = collections.Counter(keys[m.group(1)] for m in RX.finditer(text))
    return c.most_common(1)[0][0] if c else None

def norm_model(m, parent='claude-opus-5-5'):
    m = (m or '').lower()
    if 'haiku' in m: return 'claude-haiku-5-5'
    if 'sonnet' in m: return 'claude-sonnet-5-5'
    if 'opus' in m: return 'claude-opus-5-5'
    if 'fable' in m: return 'claude-fable-5-1'
    return parent

def usage_tuple(u):
    cc = u.get('cache_creation') or {}
    w1h = cc.get('ephemeral_1h_input_tokens') or 0
    wall = u.get('cache_creation_input_tokens') or 0
    return [u.get('input_tokens') or 0, max(wall - w1h, 0), w1h, u.get('cache_read_input_tokens') or 0, u.get('output_tokens') or 0]

NOTE = re.compile(r'<task-id>(\w+)</task-id>.{0,300}?<tool-use-id>(toolu_\w+)</tool-use-id>', re.S)
TOK = re.compile(r'<subagent_tokens>(\d+)</subagent_tokens><tool_uses>(\d+)</tool_uses><duration_ms>(\d+)</duration_ms>')
AID = re.compile(r'agentId: (\w+)')

agents = {}                                        # tool_use_id -> record
orch = collections.defaultdict(lambda: collections.defaultdict(lambda: [0, 0, 0, 0, 0]))  # book -> model -> usage
orch_ts = collections.defaultdict(list)
sessions_of = collections.defaultdict(set)
for f in sorted(glob.glob(P + '*.jsonl')):
    sid = os.path.basename(f)[:-6]
    seen = {}            # msg id -> book
    cur = None
    for line in open(f, encoding='utf-8', errors='replace'):
        try: d = json.loads(line)
        except Exception: continue
        t = d.get('type'); m = d.get('message') or {}
        if '<task-id>' in line:
            s = line.replace('\\n', '\n')
            for blk in s.split('<task-notification>')[1:]:
                n = NOTE.search(blk); k = TOK.search(blk)
                if n and n.group(2) in agents:
                    agents[n.group(2)]['aid'] = n.group(1)
                    if k: agents[n.group(2)]['fin'] = [int(v) for v in k.groups()]
        if not isinstance(m, dict) or t not in ('user', 'assistant'): continue
        if t == 'user':
            c = m.get('content')
            if isinstance(c, str) and not c.startswith('<task-notification>') and '<command-' not in c[:200] and not d.get('isMeta'):
                cur = book_of(c)                     # a new human request: reset unless it names a book
            elif isinstance(c, list):
                for x in c:
                    if not isinstance(x, dict) or x.get('type') != 'tool_result': continue
                    s = json.dumps(x.get('content'), ensure_ascii=False).replace('\\n', '\n')
                    tid = x.get('tool_use_id')
                    if tid in agents:
                        a = AID.search(s)
                        if a: agents[tid]['aid'] = a.group(1)
                        k = TOK.search(s)
                        if k: agents[tid]['fin'] = [int(v) for v in k.groups()]
            continue
        if t != 'assistant': continue
        mid = m.get('id'); content = m.get('content') or []
        txt = json.dumps(content, ensure_ascii=False)
        b = book_of(txt)
        if b: cur = b
        for c in content:
            if isinstance(c, dict) and c.get('type') == 'tool_use' and c.get('name') in ('Agent', 'Task'):
                i = c.get('input') or {}
                ab = book_of((i.get('prompt') or '') + ' ' + (i.get('description') or '')) or cur
                agents[c['id']] = dict(sid=sid, ts=d.get('timestamp'), desc=i.get('description'),
                                       model=norm_model(i.get('model') or ('' if i.get('subagent_type') in (None, 'general-purpose', 'claude', 'fork') else i.get('subagent_type')), m.get('model')),
                                       book=ab or 'other', bg=i.get('run_in_background'))
        if mid in seen: continue
        u = m.get('usage')
        if not u: continue
        bk = b or cur or 'other'
        seen[mid] = bk
        tup = usage_tuple(u)
        acc = orch[bk][m.get('model')]
        for j in range(5): acc[j] += tup[j]
        orch_ts[bk].append(d.get('timestamp'))
        sessions_of[bk].add(sid)

# exact usage from surviving sub-agent transcripts
sub = {}
for f in glob.glob(P + '*/subagents/**/*.jsonl', recursive=True):
    aid = re.sub(r'^agent-', '', os.path.basename(f)[:-6])
    msgs = {}; model = None
    for line in open(f, encoding='utf-8', errors='replace'):
        try: d = json.loads(line)
        except Exception: continue
        m = d.get('message') or {}
        if d.get('type') == 'assistant' and isinstance(m, dict) and m.get('usage'):
            msgs[m.get('id')] = usage_tuple(m['usage']); model = m.get('model')
    if msgs: sub[aid] = dict(model=model, msgs=list(msgs.values()))

json.dump(dict(agents=agents, orch={b: dict(v) for b, v in orch.items()},
               orch_ts={b: [min(v), max(v)] for b, v in orch_ts.items()},
               sessions={b: sorted(v) for b, v in sessions_of.items()}, sub=sub),
          open(OUT, 'w'), ensure_ascii=False)
print(len(agents), 'agent launches;', sum(1 for a in agents.values() if a.get('aid') in sub), 'with transcripts;',
      sum(1 for a in agents.values() if a.get('fin')), 'with final size;', len(orch), 'books with orchestrator turns')
