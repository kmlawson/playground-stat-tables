import json,sys
n=sys.argv[1]
L={}
cur=None
for l in open(f'listings/japan-keishicho--{n}.txt'):
    if l.startswith('#') or not l.strip(): continue
    p=[x.strip() for x in l.split('|')]
    L[p[0]+'/'+p[1]]=p
d=json.load(open(f'families/japan-keishicho--{n}.json'))
used=set()
for i,f in enumerate(d['families']):
    print('F%d'%i,f['label'])
    for m in f['members']:
        used.add(m); p=L.get(m)
        print('   ',m.replace('japan-keishicho-',''),p[4][:70] if p else '?')
print('--- 1938')
for k,p in L.items():
    if p[0].endswith('1938'): print(k.replace('japan-keishicho-',''),'|',p[4][:80],'|',p[6][:90],'|',p[7][:50])
print('--- unfamilied others')
for k,p in L.items():
    if k not in used and not p[0].endswith('1938'): print(k.replace('japan-keishicho-',''),'|',p[4][:80])
