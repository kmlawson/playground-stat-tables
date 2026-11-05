import json
d=json.load(open('batches/b01.json'))
out=[]
for r in d:
    k=r['key'];n=k.split(':')[1]
    if n=='p0016_2': o=(["economy"],["tourism"],[],"new hotels under construction, rooms")
    elif n=='p0034_1': o=(["transportation"],[],["text-tables"],"photograph captions")
    elif n=='p0037_1': o=(["transportation"],["tourism"],["text-tables"],"tourist bureau objects")
    elif n in('p0037_2','p0037_3','p0037_4','p0038_2'): o=(["transportation"],["tourism"],["text-tables"],"tourist bureau office addresses")
    else: o=(["economy","transportation"],["tourism"],[],"hotel directory with rooms, capacity, charges")
    out.append(dict(key=k,topics=o[0],tags=o[1],flags=o[2],why=o[3]))
assert [x['key'] for x in out]==[r['key'] for r in d]
json.dump(out,open('results/b01.json','w'),ensure_ascii=False,indent=1)
print(len(out))
