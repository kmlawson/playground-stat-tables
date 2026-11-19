import json,re,sys
n='japan-keishicho--crime'
fam=json.load(open(f'families/{n}.json'))['families']
m={x:i for i,f in enumerate(fam) for x in f['members']}
T={'40':{},'41':{}}
for l in open(f'listings/{n}.txt'):
    p=l.rstrip('\n').split(' | ')
    if len(p)>5 and p[0][-4:] in('1940','1941'):
        y=p[0][-2:]; mm=re.match(r'Table (\d+)\. (.*?) \[EN: (.*?)\]',p[4])
        T[y][p[1]]=(int(mm.group(1)) if mm else 0,mm.group(2) if mm else p[4],mm.group(3) if mm else '',p[6][:80])
by40={}
for k,v in T['40'].items(): by40.setdefault(v[1],[]).append(k)
for k,v in T['41'].items():
    c=[x for x in T['40'] if T['40'][x][1]==v[1]]
    print(k,v[0],v[1],'|',v[2][:60],'=>',[(x,m.get('japan-keishicho-1940/'+x)) for x in c], 'FAM1941' if 'japan-keishicho-1941/'+k in m else '')
