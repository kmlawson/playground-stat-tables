import json,sys
n=sys.argv[1]
d=json.load(open(f'families/korea-tokei--{n}.json'))
placed={m for f in d['families'] for m in f['members']}
sec=None
for l in open(f'listings/korea-tokei--{n}.txt'):
    if l.startswith('## '): sec=l[3:].strip(); continue
    p=[x.strip() for x in l.split('|')]
    if len(p)<5: continue
    if p[0]+'/'+p[1] in placed: continue
    print(p[0].replace('korea-tokanfu-',''),p[1],p[3],p[4][:90],'||',p[5][:50],'||',(p[6] if len(p)>6 else '')[:110],'||',(p[7] if len(p)>7 else '')[:70])
