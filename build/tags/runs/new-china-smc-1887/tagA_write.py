import json,sys
b=sys.argv[1]
spec=json.load(open(sys.argv[2]))
recs=json.load(open(f'batches/{b}.json'))
voc=json.load(open('../../vocabulary.json'))
T={t['id'] for t in voc['topics']};G={t['id'] for t in voc['tags']}
assert len(spec)==len(recs),(len(spec),len(recs))
out=[]
for r,s in zip(recs,spec):
  tp,tg,fl,why=s
  assert all(x in T for x in tp) and all(x in G for x in tg),s
  out.append({"key":r['key'],"topics":tp,"tags":tg,"flags":fl,"why":why})
import os;os.makedirs('results',exist_ok=True)
json.dump(out,open(f'results/{b}.json','w'),ensure_ascii=False,indent=1)
print(b,len(out),sum(1 for o in out if o['tags']))
