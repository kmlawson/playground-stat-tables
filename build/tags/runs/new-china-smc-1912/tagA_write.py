import json,sys
n=int(sys.argv[1]); b=json.load(open(f'batches/b{n:02d}.json'))
spec={}
for l in open(f'tagA_spec{n:02d}.txt'):
    l=l.rstrip('\n')
    if not l.strip(): continue
    i,t,g,f,w=l.split('|'); spec[int(i)]=(t,g,f,w)
assert sorted(spec)==list(range(len(b))),(len(b),[i for i in range(len(b)) if i not in spec])
out=[]
for i,r in enumerate(b):
    t,g,f,w=spec[i]
    out.append({"key":r['key'],"topics":[x for x in t.split(',') if x],"tags":[x for x in g.split(',') if x],"flags":["text-tables"] if f=='T' else [],"why":w})
import os; os.makedirs('results',exist_ok=True)
v=json.load(open('../../vocabulary.json'));ids={x['id'] for x in v['tags']}|{x['id'] for x in v['topics']}
for o in out:
    for x in o['topics']+o['tags']: assert x in ids,(o['key'],x)
    assert 1<=len(o['topics'])<=2 and len(o['tags'])<=3
json.dump(out,open(f'results/b{n:02d}.json','w'),ensure_ascii=False,indent=1)
print(n,len(out),sum(1 for o in out if o['tags']))
