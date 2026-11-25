import json,sys
L=sys.argv[1]
fam=json.load(open(f'families/{L}.json'))['families']
used={m for f in fam for m in f['members']}
lines={}
for ln in open(f'listings/{L}.txt',encoding='utf8'):
    if ln.startswith('#') or '|' not in ln: continue
    p=[x.strip() for x in ln.split('|')]
    lines[p[0]+'/'+p[1]]=p
print('FAMILIES')
for i,f in enumerate(fam):
    print(i,f['label'],'|',' '.join(m.replace('korea-tokanfu-','') for m in f['members']))
print('UNPLACED (all editions)')
for k,p in lines.items():
    if k not in used:
        print(k.replace('korea-tokanfu-',''),'|',' | '.join(x[:90] for x in p[2:8]))
