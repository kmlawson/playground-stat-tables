import sys,json
n=sys.argv[1]
fam=json.load(open(f'families/japan-keishicho--{n}.json'))
inf={}
for i,f in enumerate(fam['families']):
    for m in f['members']: inf[m]=i
for l in open(f'listings/japan-keishicho--{n}.txt'):
    if l.startswith('#') or not l.strip(): continue
    p=[x.strip() for x in l.split('|')]
    if len(p)<7: print(l[:100]);continue
    s=p[0].replace('japan-keishicho-','');k=p[0]+'/'+p[1]
    print(s,p[1],p[3],'F%s'%inf.get(k,'-'),p[4][:90],'||',p[6][:int(sys.argv[2])])
