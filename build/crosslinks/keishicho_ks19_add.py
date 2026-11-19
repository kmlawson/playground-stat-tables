import json,sys
# usage: add.py listing idx:id ...   (new family: "new:Label:slug/id:slug/id")
n=sys.argv[1]; p=f'families/{n}.json'
d=json.load(open(p))
def ed(m): return m.split('/')[0]
for a in sys.argv[2:]:
    if a.startswith('new:'):
        _,lab,*ms=a.split(':'); d['families'].append({'label':lab,'members':sorted(ms,key=ed),'note':''}); continue
    i,m=a.split(':',1)
    if not m.startswith('japan'): m='japan-keishicho-1941/'+m
    f=d['families'][int(i)]['members']
    if m in f: continue
    k=len(f)
    for j,x in enumerate(f):
        if ed(x)>ed(m): k=j;break
    f.insert(k,m)
json.dump(d,open(p,'w'),ensure_ascii=False,indent=1)
json.load(open(p))
