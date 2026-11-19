import json,sys
L=sys.argv[1]
rows={}
for l in open(f'listings/{L}.txt'):
    if l.startswith('#') or '|' not in l: continue
    p=[x.strip() for x in l.split('|')]
    rows[p[0]+'/'+p[1]]=p
fam=json.load(open(f'families/{L}.json'))['families']
used=set()
for i,f in enumerate(fam):
    print(f'F{i}',f['label'])
    for m in f['members']:
        used.add(m)
        if m.startswith('japan-keishicho-1937') or m.startswith('japan-keishicho-1938') or m.startswith('japan-keishicho-1939'):
            r=rows.get(m); print('   ',m,(r[4][:70] if r else '?'),'|',(r[6][:60] if r else ''))
print('--- unassigned')
for k,p in rows.items():
    if k not in used: print(k,'|',p[4][:80],'|',p[6][:70],'|',p[7][:50])
