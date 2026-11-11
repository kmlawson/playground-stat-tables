import json,sys
n=sys.argv[1]
V=json.load(open('../../vocabulary.json'))
T={t['id'] for t in V['topics']};G={t['id'] for t in V['tags']}
B=json.load(open(f'batches/b{n}.json'))
out={}
for l in open(sys.argv[2]):
    l=l.rstrip('\n')
    if not l.strip(): continue
    i,tp,tg,fl,why=l.split('|')
    tp=[x for x in tp.split(',') if x];tg=[x for x in tg.split(',') if x]
    assert all(x in T for x in tp),l
    assert all(x in G for x in tg),l
    out[int(i)]={"topics":tp,"tags":tg,"flags":['text-tables'] if fl=='T' else [],"why":why}
assert sorted(out)==list(range(len(B))),(len(B),sorted(set(range(len(B)))-set(out)))
res=[dict(key=r['key'],**out[i]) for i,r in enumerate(B)]
json.dump(res,open(f'results/b{n}.json','w'),ensure_ascii=False,indent=1)
print(n,len(res),sum(1 for r in res if r['tags']))
