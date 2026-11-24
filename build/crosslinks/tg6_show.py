import json,sys,re
n=sys.argv[1]
fam=json.load(open(f'families/{n}.json'))['families']
m={x:i for i,f in enumerate(fam) for x in f['members']}
for f in fam: print('FAM',f['label'],f['members'])
print()
for l in open(f'listings/{n}.txt'):
    if l.startswith('#') or not l.strip(): continue
    p=[x.strip() for x in l.split('|')]
    if len(p)<8: continue
    k=p[0]+'/'+p[1]
    mark=m.get(k,'-')
    t=re.sub(r'\[EN: ?','[',p[4])
    print(mark,k.replace('korea-tokanfu-',''),p[3][:12],t[:90],'||',p[6][:int(sys.argv[2])],'||',p[7][:60])
