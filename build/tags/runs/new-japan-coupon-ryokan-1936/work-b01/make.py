import json
d='/Users/kml/shell/projects/yearbooks/japanyearbooks/stat-tables-site/build/tags/runs/new-japan-coupon-ryokan-1936/'
b=json.load(open(d+'batches/b01.json'))
out=[]
for r in b:
    if r['key'].endswith(':p0001_1'):
        o=dict(topics=['transportation','economy'],tags=['tourism'],flags=['text-tables'],why='tourist bureau offices, addresses, phones')
    else:
        o=dict(topics=['economy','transportation'],tags=['tourism'],flags=[],why='ryokan directory with nightly rates')
    out.append(dict(key=r['key'],**o))
json.dump(out,open(d+'results/b01.json','w'),ensure_ascii=False,indent=1)
assert [o['key'] for o in out]==[r['key'] for r in b]
print(len(out))
