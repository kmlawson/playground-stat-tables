import json,sys
n=int(sys.argv[1]);B=json.load(open(f'batches/b{n:02d}.json'))
V=json.load(open('../../vocabulary.json'));T={t['id'] for t in V['topics']};G={t['id'] for t in V['tags']}
S={}
for l in open(f'tagA_spec{n:02d}.txt'):
    l=l.strip()
    if not l: continue
    k,t,g,f,w=[x.strip() for x in l.split('|')]
    S[k]=([x for x in t.split(',') if x],[x for x in g.split(',') if x],['text-tables'] if f=='T' else [],w)
out=[]
for r in B:
    s=S[r['key'].split(':')[1]]
    assert all(x in T for x in s[0]) and 1<=len(s[0])<=2,(r['key'],s)
    assert all(x in G for x in s[1]) and len(s[1])<=3,(r['key'],s)
    out.append(dict(key=r['key'],topics=s[0],tags=s[1],flags=s[2],why=s[3]))
assert len(S)==len(B)
import os;os.makedirs('results',exist_ok=True)
json.dump(out,open(f'results/b{n:02d}.json','w'),ensure_ascii=False,indent=1)
print(n,len(out),sum(1 for o in out if o['tags']))
