import json,sys
n=sys.argv[1]; add=json.loads(sys.argv[2]); new=json.loads(sys.argv[3]) if len(sys.argv)>3 else []
p=f'families/korea-tokei--{n}.json'
d=json.load(open(p))
def ins(f,m):
    ms=f['members']
    i=len(ms)
    while i>0 and ms[i-1].startswith('korea-tokanfu-1939/'): i-=1
    ms.insert(i,m)
cnt=0
for k,ids in add.items():
    for m in ids:
        ins(d['families'][int(k)],'korea-tokanfu-1928/'+m); cnt+=1
for f in new:
    d['families'].append(f); cnt+=len(f['members'])-1
json.dump(d,open(p,'w'),ensure_ascii=False,indent=1)
json.load(open(p))
print(n,len(d['families']),cnt)
