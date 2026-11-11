import json,sys
n=int(sys.argv[1]); spec=sys.argv[2]
v=json.load(open('../../vocabulary.json'))
T={x['id'] for x in v['topics']};G={x['id'] for x in v['tags']}
b=json.load(open(f'batches/b{n:02d}.json'))
S={}
for l in open(spec):
    l=l.strip()
    if not l: continue
    i,t,g,f,w=(l.split('|')+['']*5)[:5]
    t=[x for x in t.split(',') if x];g=[x for x in g.split(',') if x]
    assert all(x in T for x in t),l; assert all(x in G for x in g),l
    S[int(i)]=dict(topics=t,tags=g,flags=['text-tables'] if f else [],why=w)
assert set(S)==set(range(len(b))),(set(range(len(b)))-set(S))
out=[dict(key=r['key'],**S[i]) for i,r in enumerate(b)]
json.dump(out,open(f'results/b{n:02d}.json','w'),ensure_ascii=False,indent=1)
print(n,len(out),sum(1 for o in out if o['tags']))
