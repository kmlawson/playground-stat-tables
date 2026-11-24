import sys,json,re
n=sys.argv[1]; mode=sys.argv[2]
fam=json.load(open(f'families/korea-tokei--{n}.json'))
used={m for f in fam['families'] for m in f['members']}
cur=''
for l in open(f'listings/korea-tokei--{n}.txt'):
    if l.startswith('## '): cur=l[3:].strip().replace('korea-tokanfu-','');continue
    p=[x.strip() for x in l.split('|')]
    if len(p)<8: continue
    k=p[0]+'/'+p[1]
    if mode=='new' and cur!='1913': continue
    if mode=='old' and cur=='1913': continue
    t=re.sub(r'\[EN: (Table \d+: )?','[',p[4])
    t=re.sub(r'^Table \d+\. ','',t)
    print(('*' if k in used else ' ')+cur+'/'+p[1],t[:110],'||',p[6][:int(sys.argv[3])],'||',p[7][:40])
