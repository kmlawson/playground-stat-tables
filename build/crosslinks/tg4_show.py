import sys,json
n=sys.argv[1]
fam=json.load(open(f'families/korea-tokei--{n}.json'))
used={m:f['label'] for f in fam['families'] for m in f['members']}
for f in fam['families']: print('FAM',f['label'],f['members'])
for l in open(f'listings/korea-tokei--{n}.txt'):
    if l.startswith('#'): print(l.strip());continue
    p=[x.strip() for x in l.split('|')]
    if len(p)<8: continue
    k=p[0]+'/'+p[1]
    print(('*' if k in used else ' '),k.replace('korea-tokanfu-',''),p[2][:12],p[3],p[4][:90],'||',p[6][:110],'||',p[7][:50])
