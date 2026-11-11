import json,sys
def add(path,pairs,new=()):
    f=json.load(open(path))
    fam=f['families']; cnt=0
    for anchor,mem in pairs:
        for x in fam:
            if anchor in x['members']:
                assert mem not in x['members']
                x['members'].insert(0,mem); cnt+=1; break
        else: print('NO ANCHOR',anchor)
    for label,mems in new:
        fam.append({'label':label,'members':mems,'note':''}); cnt+=len(mems)
    json.dump(f,open(path,'w'),ensure_ascii=False,indent=1)
    json.load(open(path)); print(path,len(fam),cnt)
