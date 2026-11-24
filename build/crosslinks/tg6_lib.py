import json
ED=['korea-tokanfu-1908','korea-tokanfu-1913','korea-tokanfu-1919','korea-tokanfu-1939']
def apply(name, adds, news):
    p=f'families/{name}.json'
    d=json.load(open(p))
    fams=d['families']
    used={m for f in fams for m in f['members']}
    key=lambda m:ED.index(m.split('/')[0])
    cnt=0
    for label,mem in adds.items():
        f=[f for f in fams if f['label']==label][0]
        for m in mem:
            assert m not in used,m
            used.add(m); cnt+=1
        f['members']=sorted(f['members']+mem,key=key)  # stable
    for label,mem,*note in news:
        for m in mem:
            assert m not in used,m
            used.add(m)
        e={'label':label,'members':sorted(mem,key=key)}
        if note: e['note']=note[0]
        fams.append(e); cnt+=len(mem)
    json.dump(d,open(p,'w'),ensure_ascii=False,indent=1)
    json.load(open(p))
    print(name,len(fams),'families; added',cnt)
