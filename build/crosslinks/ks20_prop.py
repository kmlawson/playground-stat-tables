import json,sys,re
n=sys.argv[1]
f=json.load(open(f'families/{n}.json'))
inf={}
for i,fa in enumerate(f['families']):
    for m in fa['members']: inf[m]=i
T={}
for l in open(f'listings/{n}.txt'):
    p=l.split(' | ')
    if len(p)<7 or not p[0].startswith('japan-keishicho'):continue
    T[p[0]+'/'+p[1]]=p
def jt(p):
    t=p[4].split(' [EN')[0]; return re.sub(r'^Table \d+\.\s*','',t).strip()
by={}
for k,p in T.items():
    if p[0].endswith('1940'): by.setdefault(jt(p),[]).append(k)
for k,p in T.items():
    if p[0].endswith('1941') and k not in inf:
        c=by.get(jt(p),[])
        print(k,jt(p),'->',[(x,inf.get(x)) for x in c])
