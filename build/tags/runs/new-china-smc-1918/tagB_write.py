import json,sys
b=sys.argv[1]
spec=json.load(open(f'tagB_{b}_spec.json'))
d=json.load(open(f'batches/{b}.json'))
voc=json.load(open('../../vocabulary.json'))
T={x['id'] for x in voc['topics']};G={x['id'] for x in voc['tags']}
assert len(spec)==len(d),(len(spec),len(d))
out=[]
for r,s in zip(d,spec):
    t,g,f,w=s
    assert all(x in T for x in t) and all(x in G for x in g),(r['key'],t,g)
    out.append({"key":r['key'],"topics":t,"tags":g,"flags":["text-tables"] if f else [],"why":w})
json.dump(out,open(f'results/{b}.json','w'),ensure_ascii=False,indent=1)
print(b,len(out),sum(1 for o in out if o['tags']))
