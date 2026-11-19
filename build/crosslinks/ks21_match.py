import json,sys,re
n=sys.argv[1]
fam=json.load(open(f'families/japan-keishicho--{n}.json'))
inf={m:i for i,f in enumerate(fam['families']) for m in f['members']}
def ti(p): 
    t=p[4] if len(p)>4 else ''
    return re.sub(r'^Table \d+\.\s*','',t)
rows={}
for l in open(f'listings/japan-keishicho--{n}.txt'):
    p=l.rstrip('\n').split(' | ')
    rows.setdefault(p[0],[]).append(p)
for p in rows.get('japan-keishicho-1941',[]):
    t=ti(p); jp=t.split(' [')[0]
    c=[q for q in rows.get('japan-keishicho-1940',[]) if ti(q).split(' [')[0]==jp]
    print('41',p[1],t[:90],'| cols:',p[6][:60] if len(p)>6 else '')
    for q in c: print('   40',q[1],ti(q)[:60],'fam',inf.get(q[0]+'/'+q[1]),'| cols:',q[6][:60] if len(q)>6 else '')
    if not c: print('   NO exact 1940')
