import json,sys
L=sys.argv[1]; spec=json.loads(sys.argv[2])  # {"add":{"idx":[ids]},"new":[{"label","members","note"}]}
ED=['1925','1935','1937','1938','1939','1940','1942']
key=lambda m:(ED.index(m.split('/')[0].split('-')[-1]),)
fn=f'families/{L}.json'; d=json.load(open(fn))
n=0
for i,ids in spec.get('add',{}).items():
    f=d['families'][int(i)]; f['members']=sorted(f['members']+ids,key=key); n+=len(ids)
for nf in spec.get('new',[]):
    nf.setdefault('note',''); nf['members']=sorted(nf['members'],key=key); d['families'].append(nf); n+=sum('1938' in m for m in nf['members'])
json.dump(d,open(fn,'w'),ensure_ascii=False,indent=1)
json.load(open(fn)); print(L,len(d['families']),'families, added',n)
