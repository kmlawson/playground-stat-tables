import json,sys
n=sys.argv[1]
fam=json.load(open(f'families/{n}.json'))['families']
m={}
for i,f in enumerate(fam):
    for x in f['members']: m[x]=i
for l in open(f'listings/{n}.txt'):
    p=l.rstrip('\n').split(' | ')
    if len(p)<5: continue
    key=p[0]+'/'+p[1]
    if p[0] in('japan-keishicho-1941','japan-keishicho-1940'):
        print(p[0][-4:],key.split('/')[1],m.get(key,'-'),'|',' | '.join(p[3:5]),'|',' | '.join(p[5:7])[:150])
