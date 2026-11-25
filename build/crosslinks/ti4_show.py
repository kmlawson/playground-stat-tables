import json,sys
t=sys.argv[1]
L={}
for l in open(f'listings/korea-tokei--{t}.txt'):
    p=[x.strip() for x in l.rstrip('\n').split('|')]
    if len(p)>=7 and not l.startswith('#'): L[p[0]+'/'+p[1]]=p
d=json.load(open(f'families/korea-tokei--{t}.json'))
used=set(m for f in d['families'] for m in f['members'])
for i,f in enumerate(d['families']):
    ms=f['members']; last=[m for m in ms if '1939' in m or '1922' in m or '1919' in m][-1]
    print('F',i,f['label'],'|',L[last][4][:60],'|',L[last][6][:70], '|', L[last][7][:50] if len(L[last])>7 else '')
print('--- unplaced 1928')
for k,p in L.items():
    if p[0]=='korea-tokanfu-1928' and k not in used:
        print(k,'|',p[2][:12],'|',p[4][:70],'|',p[6][:90],'|',p[7][:50] if len(p)>7 else '')
