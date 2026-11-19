import json,re,sys
n='public-health'
L={}
for l in open(f'listings/japan-keishicho--{n}.txt'):
    if l.startswith('#') or not l.strip(): continue
    p=[x.strip() for x in l.split('|')]; L[p[0]+'/'+p[1]]=p
def jt(p):
    t=re.sub(r'\[EN:.*','',p[4]); t=re.sub(r'^Table \d+\.\s*','',t); return t.strip()
d=json.load(open(f'families/japan-keishicho--{n}.json'))
idx={}
for i,f in enumerate(d['families']):
    for m in f['members']:
        if not m.endswith('1938') and '1938' not in m.split('/')[0]:
            idx.setdefault(jt(L[m]),set()).add(i)
for k,p in L.items():
    if p[0].endswith('1938'):
        c=idx.get(jt(p),set())
        print(k.split('/')[1], sorted(c), jt(p)[:40], '|', re.search(r'EN: (.*?)\]',p[4]).group(1)[:60] if 'EN:' in p[4] else '')
