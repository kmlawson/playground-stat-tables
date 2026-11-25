import json,sys
n=sys.argv[1]
f=json.load(open(f'families/korea-tokei--{n}.json'))
used=set()
for i,x in enumerate(f['families']):
    print(i,x['label'],[m.replace('korea-tokanfu-','') for m in x['members']])
    used|=set(x['members'])
print('--- unassigned')
for l in open(f'listings/korea-tokei--{n}.txt'):
    if l.startswith('#') or '|' not in l: continue
    p=[s.strip() for s in l.split('|')]
    if p[0]+'/'+p[1] in used: continue
    print(p[0].replace('korea-tokanfu-',''),p[1],'|',p[3],'|',p[4][:80],'|',p[6][:90])
