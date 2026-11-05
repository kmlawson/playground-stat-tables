import json
d=json.load(open('batches/b02.json'))
out=[]
for r in d:
    k=r['key']
    if k.endswith('p0022_1'):
        o=dict(topics=["transportation"],tags=["tourism"],flags=["text-tables"],why="access directions to resort places; textual")
    elif k.endswith('p0026_1'):
        o=dict(topics=["press"],tags=[],flags=["text-tables"],why="publication colophon; publisher and printer")
    else:
        o=dict(topics=["transportation"],tags=["tourism"],flags=[],why="coupon ryokan list with nightly rates: "+r['en']['t'])
    out.append(dict(key=k,**o))
import os;os.makedirs('results',exist_ok=True)
json.dump(out,open('results/b02.json','w'),ensure_ascii=False,indent=1)
assert [o['key'] for o in out]==[r['key'] for r in d]
