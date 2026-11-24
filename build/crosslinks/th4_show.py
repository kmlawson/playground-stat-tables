import json,sys
n=sys.argv[1]
f=json.load(open(f'families/{n}.json'))
inf=set()
for x in f['families']:
    print(x['label'],'|',[m.replace('korea-tokanfu-','') for m in x['members']]); inf.update(x['members'])
print('--- 1922 lines')
for l in open(f'listings/{n}.txt'):
    p=l.split('|')
    if p[0].strip().startswith('korea-tokanfu-1922'):
        k=p[0].strip()+'/'+p[1].strip()
        print('IN' if k in inf else 'NEW',l.strip()[:300])
print('--- other-edition ungrouped')
for l in open(f'listings/{n}.txt'):
    p=l.split('|')
    k=p[0].strip()+'/'+p[1].strip()
    if not p[0].strip().startswith('korea-tokanfu-1922') and k not in inf: print(l.strip()[:200])
