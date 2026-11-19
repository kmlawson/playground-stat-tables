import json,sys,re
n=sys.argv[1]
f=json.load(open(f'families/{n}.json'))
inf={}
for i,fa in enumerate(f['families']):
    for m in fa['members']: inf[m]=i
print(len(f['families']),'families; 1941 members:',sum(1 for m in inf if '1941/' in m))
for l in open(f'listings/{n}.txt'):
    p=l.split(' | ')
    if len(p)<5 or not p[0].startswith('japan-keishicho'):continue
    k=p[0]+'/'+p[1]
    if p[0].endswith('1941') and k not in inf: print('UNPLACED',k,p[4][:90])
