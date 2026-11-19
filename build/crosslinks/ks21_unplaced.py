import json,sys,re
n=sys.argv[1]
fam=json.load(open(f'families/japan-keishicho--{n}.json'))
inf={m:f for f in fam['families'] for m in f['members']}
for l in open(f'listings/japan-keishicho--{n}.txt'):
    p=l.rstrip('\n').split(' | ')
    if p[0]!='japan-keishicho-1941':continue
    k=p[0]+'/'+p[1]
    print(k in inf, k, ' | '.join(p[2:6])[:110])
