import json
b=json.load(open('batches/b02.json'))
A='agriculture';F='forestry'
m={
'p0054_1':(['population','colonial-rule'],['migration','overseas-communities'],'overseas travellers by purpose'),
'p0055_1':([A],['arable-land','land-tenure'],'cultivated area, owner/tenant'),
'p0055_2':([A,'population'],['households','land-tenure'],'farm households by nationality'),
'p0055_3':([A],['rice','crop-production'],'rice area and harvest'),
'p0056_1':([A],['barley','wheat','crop-production'],'barley wheat'),
'p0057_1':([A],['soybeans','crop-production'],'pulses'),
'p0057_2':([A],['cereals','crop-production'],'minor grains'),
'p0058_1':([A],['industrial-crops','cotton','tobacco'],'industrial crops'),
'p0059_1':([A],['horticulture','crop-production'],'vegetables'),
'p0059_2':([A],['horticulture'],'fruit trees'),
'p0060_1':([A],['farm-inputs','fertilisers'],'green manure'),
'p0060_2':([A],['sericulture'],'silkworm rearing'),
'p0061_1':([A],['sericulture','silk'],'tussah silkworm'),
'p0061_2':([A,'education'],['agricultural-extension'],'agricultural institutes'),
'p0061_3':([A],['sericulture'],'cooperative young silkworm rearing'),
'p0061_4':([A],['sericulture'],'silkworm egg production'),
'p0062_1':([A],['sericulture','plant-fibres'],'mulberry seedlings'),
'p0062_2':([A],['livestock'],'breeding bulls by age'),
'p0062_3':([A],['livestock'],'bull breeding services'),
'p0063_1':([A],['livestock','eggs-and-poultry'],'livestock counts'),
'p0063_2':([A],['livestock'],'cattle births slaughter deaths'),
'p0063_3':([A,'trade'],['livestock'],'slaughterhouses'),
'p0064_1':([A],['livestock','leather-and-furs'],'livestock products'),
'p0065_1':([A],['land-reclamation','land-tenure'],'leased reclamation land'),

'p0065_2':(['colonial-rule',A],['land-tenure','agricultural-credit'],'Toyo Takushoku Co. business'),
'p0065_3':(['colonial-rule',A],['settler-migration','land-tenure'],'Toyo Takushoku immigrants and land'),
'p0066_1':([F],['forest-area'],'forest area by ownership'),
'p0066_2':([F],['forest-management'],'protection forests'),
'p0066_3':([F],['forest-management'],'forest lease and sale'),
'p0067_1':([F],['forest-management'],'state forest grants'),
'p0067_2':([F],['forest-management','timber'],'state forest products sales'),
'p0068_1':([F],['afforestation'],'afforestation'),
'p0069_1':([F],['timber','fuelwood-and-charcoal'],'forest products output'),
'p0070_1':([F,'disasters'],['forest-management','fires'],'forest damage'),
'p0071_1':([F],['afforestation'],'commemorative tree planting'),
'p0072_1':([F],['afforestation'],'local-expense afforestation'),
'p0072_2':([F],['afforestation','forest-management'],'tree nurseries'),
'p0073_1':([F],['afforestation'],'private nursery seedlings'),
'p0073_2':([F],['timber','forest-management'],'forestry office logging'),
'p0074_1':([F,'trade'],['timber'],'timber bought and sold'),
}
voc=open('/Users/kml/shell/projects/yearbooks/japanyearbooks/stat-tables-site/build/tags/VOCABULARY.md').read()
out=[]
for r in b:
    k=r['key'];t,g,w=m[k.split(':')[1]]
    for x in g: assert '`'+x+'`' in voc,x
    out.append(dict(key=k,topics=t,tags=g,flags=[],why=w))
assert len(out)==len(b)
json.dump(out,open('results/b02.json','w'),ensure_ascii=False,indent=1)
print(len(out))
