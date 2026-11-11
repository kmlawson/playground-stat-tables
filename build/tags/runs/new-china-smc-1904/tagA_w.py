import json,sys
n=sys.argv[1]
spec=json.load(open('tagA_spec%s.json'%n))
d=json.load(open('batches/b0%s.json'%n))
assert len(spec)==len(d),(len(spec),len(d))
out=[]
for r,s in zip(d,spec):
    t,g,f,w=(s+[None]*4)[:4] if len(s)<4 else s
    out.append({"key":r['key'],"topics":t,"tags":g,"flags":f or [],"why":w or ""})
import os
os.makedirs('results',exist_ok=True)
json.dump(out,open('results/b0%s.json'%n,'w'),ensure_ascii=False,indent=1)
print(len(out),sum(1 for o in out if o['tags']))
