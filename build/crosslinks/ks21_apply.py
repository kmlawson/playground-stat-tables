import json,sys
# usage: ks21_apply.py listing  id:famindex ...  (famindex int = existing; "new:Label:slug/id,slug/id" not supported -> use new)
n=sys.argv[1]; p=f'families/japan-keishicho--{n}.json'
d=json.load(open(p)); added=0
for a in sys.argv[2:]:
    if a.startswith('NEW|'):
        _,label,*mem=a.split('|'); d['families'].append({'label':label,'members':sorted(mem,key=lambda m:m),'note':''}); added+=sum(1 for m in mem if '1941' in m); continue
    i,k=a.split(':'); k=int(k); m='japan-keishicho-1941/'+i
    mem=d['families'][k]['members']
    assert m not in mem
    idx=len([x for x in mem if x.split('/')[0]<'japan-keishicho-1941'])
    mem.insert(idx,m); added+=1
json.dump(d,open(p,'w'),ensure_ascii=False,indent=1)
json.load(open(p)); print(n,len(d['families']),'added',added)
