import json,sys
t=sys.argv[1]; pairs=json.loads(sys.argv[2])  # {"famIndex":"id"}
order=['1908','1913','1919','1922','1928','1939']
def ed(m):
    s=m.split('/')[0]
    return next(i for i,o in enumerate(order) if o in s)
fn=f'families/korea-tokei--{t}.json'
d=json.load(open(fn))
for k,v in pairs:
    m='korea-tokanfu-1928/'+v; ms=d['families'][int(k)]['members']
    assert m not in ms
    ms.append(m); ms.sort(key=ed)
json.dump(d,open(fn,'w'),ensure_ascii=False,indent=1)
json.load(open(fn)); print(len(pairs),'added')
