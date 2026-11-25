import json,sys
L=sys.argv[1]
fam=json.load(open(f'families/{L}.json'))['families']
used={m for f in fam for m in f['members']}
print('FAMILIES')
for i,f in enumerate(fam):
    print(i,f['label'],'|',' '.join(m.replace('korea-tokanfu-','') for m in f['members']))
print('UNPLACED')
for ln in open(f'listings/{L}.txt',encoding='utf8'):
    if ln.startswith('#') or '|' not in ln: continue
    p=[x.strip() for x in ln.split('|')]
    if p[0]+'/'+p[1] in used: continue
    print(p[0].replace('korea-tokanfu-',''),p[1],'|',p[4][:70],'|',p[6][:60])
