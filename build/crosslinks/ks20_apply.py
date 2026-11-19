import json,sys,re,collections
n=sys.argv[1]
extra={ # manual 1941 -> 1940 title-less assignments by existing member
'public-health':{'p0079_2':'japan-keishicho-1940/p0080_2','p0092_2':'japan-keishicho-1939/p0092_3','p0092_4':'japan-keishicho-1940/p0093_4'},
'factories-and-buildings':{'p0070_1':'japan-keishicho-1940/p0071_1','p0070_2':'japan-keishicho-1940/p0071_2'},
'licensed-trades':{'p0049_1':'japan-keishicho-1940/p0050_1','p0050_1':'japan-keishicho-1940/p0051_1'},
}.get(n.split('--')[1],{})
newfam={'public-health':[('Livestock infectious diseases by city and district',['japan-keishicho-1940/p0093_3','japan-keishicho-1941/p0092_3'],'')]}.get(n.split('--')[1],[])
fp=f'families/{n}.json'
f=json.load(open(fp))
order=['1925','1935','1937','1938','1939','1940','1941','1942']
key=lambda m:order.index(m.split('/')[0][-4:])
inf={m:i for i,fa in enumerate(f['families']) for m in fa['members']}
T={}
for l in open(f'listings/{n}.txt'):
    p=l.split(' | ')
    if len(p)<7 or not p[0].startswith('japan-keishicho'):continue
    T[p[0]+'/'+p[1]]=p
jt=lambda p:re.sub(r'^Table \d+\.\s*','',p[4].split(' [EN')[0]).strip()
by={}
for k,p in T.items():
    if p[0].endswith('1940'):by.setdefault(jt(p),[]).append(k)
used={m for _,ms,_ in newfam for m in ms}
added=0
for k,p in T.items():
    if not p[0].endswith('1941') or k in inf or k in used: continue
    cand=extra.get(p[1])
    if cand is None:
        c=[x for x in by.get(jt(p),[]) if x in inf]
        cand=c[0] if len(c)==1 else None
    if cand is None or cand not in inf: print('skip',k);continue
    fa=f['families'][inf[cand]]
    fa['members'].append(k);fa['members'].sort(key=key);added+=1
for lab,ms,note in newfam:
    d={'label':lab,'members':ms};
    if note:d['note']=note
    d['note']=d.get('note','');f['families'].append(d);added+=len(ms)
json.dump(f,open(fp,'w'),ensure_ascii=False,indent=1)
json.load(open(fp))
print(n,len(f['families']),'families; 1941 added',added)
