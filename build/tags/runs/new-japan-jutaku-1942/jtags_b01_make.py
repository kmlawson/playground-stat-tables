import json
d=json.load(open('batches/b01.json'))
P,W,E,L,U=['population'],['welfare'],['economy'],['labour'],['utilities']
m={
'p0007_1':(['population'],['population-totals'],'town size distribution by country'),
'p0008_1':(['population'],['population-totals'],'municipalities and pop by size class'),
'p0008_2':(['population'],['population-totals'],'urban vs non-urban pop'),
'p0009_1':(['welfare','population'],['housing','households'],'households by rooms'),
'p0009_2':(['population','geography'],[],'increase in number of municipalities'),
'p0009_3':(['population'],[],'increase of cities by size'),
'p0010_1':(['welfare','population'],['housing','households'],'households by rooms and persons'),
'p0012_1':(['welfare','population'],['housing','households'],'Tokyo households by rooms/persons'),
'p0012_2':(['welfare','population'],['housing','households'],'Osaka households by rooms/persons'),
'p0013_1':(['welfare','population'],['housing','households'],'city pop, households, houses, vacancies'),
'p0014_1':(['welfare','population'],['housing','households'],'Osaka pop households houses vacant'),
'p0015_1':(['welfare'],['housing'],'rooms and mats per dwelling'),
'p0015_2':(['welfare','economy'],['housing','real-estate'],'rent by type and floor'),
'p0016_1':(['welfare'],['housing'],'site, floor area, rooms per dwelling'),
'p0016_2':(['welfare'],['housing'],'occupants and space per person'),
'p0016_3':(['welfare','economy'],['housing','real-estate'],'rent time series'),
'p0016_4':(['economy','welfare'],['real-estate','construction'],'rent vs building cost'),
'p0017_1':(['welfare'],['housing'],'houses and vacancies industrial cities'),
'p0017_2':(['welfare'],['housing','real-estate'],'households by ownership'),
'p0018_1':(['welfare'],['housing'],'rented houses by floor area'),
'p0019_1':(['welfare'],['housing'],'site, floor area, rooms'),
'p0020_1':(['welfare'],['housing'],'occupants and space per person'),
'p0021_1':(['welfare','economy'],['housing','real-estate'],'rent per house, tsubo, mat'),
'p0022_1':(['welfare'],['housing'],'apartment survey'),
'p0023_1':(['welfare'],['housing'],'boarding house survey'),
'p0024_1':(['welfare'],['housing'],'room rental survey'),
'p0025_1':(['welfare'],['housing'],'dwellings by type, rented'),
'p0025_2':(['welfare'],['housing'],'dwellings by type, owned'),
'p0026_1':(['welfare'],['housing'],'mats per person, rented'),
'p0026_2':(['welfare'],['housing'],'mats per person, owned'),
'p0027_1':(['welfare','economy'],['housing','real-estate'],'rent per mat by house type'),
'p0028_1':(['labour','economy'],['wages','construction'],'building labour wage index'),
'p0028_2':(['economy'],['prices'],'overall wholesale price index'),
'p0028_3':(['economy'],['prices'],'classified index'),
'p0028_4':(['economy','trade'],['prices'],'wholesale price index 8 groups'),
'p0029_1':(['economy','utilities'],['prices','construction'],'building materials price index'),
'p0029_2':(['economy','welfare'],['cost-of-living'],'living cost index overall'),
'p0029_3':(['economy','welfare'],['cost-of-living'],'living cost index by class'),
'p0030_1':(['economy','welfare'],['prices','cost-of-living'],'retail price and living cost index'),
'p0030_2':(['utilities','welfare'],['construction','housing'],'urban housing construction stats'),
}
out=[]
for r in d:
    t,g,w=m[r['key'].split(':')[1]]
    out.append({'key':r['key'],'topics':t,'tags':g,'flags':[],'why':w})
json.dump(out,open('results/b01.json','w'),ensure_ascii=False,indent=1)
ids=set(v['id'] for v in json.load(open('../../vocabulary.json'))['tags'])|set(json.load(open('../../vocabulary.json'))['approved_additions']['tags'])
print(len(out),sum(bool(o['tags']) for o in out),[g for o in out for g in o['tags'] if g not in ids])
