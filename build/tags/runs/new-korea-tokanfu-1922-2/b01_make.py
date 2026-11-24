import json
A='agriculture';F='forestry'
m={
'p0006_1':([A,'population'],['arable-land','crop-production','households'],''),
'p0008_1':([A],['arable-land','land-tenure'],''),
'p0009_1':([A,'population'],['households','nationality-and-ethnicity','occupations'],''),
'p0010_1':([A],['rice','crop-production'],''),
'p0011_1':([A],['barley','wheat','cereals'],''),
'p0012_1':([A],['soybeans','crop-production'],''),
'p0013_1':([A],['cereals','crop-production'],''),
'p0014_1':([A],['industrial-crops','plant-fibres','crop-production'],''),
'p0016_1':([A],['horticulture','crop-production'],''),
'p0017_1':([A],['horticulture'],''),
'p0017_2':([A],['fertilisers','crop-production'],'green manure'),
'p0018_1':([A],['sericulture','silk'],''),
'p0019_1':([A],['sericulture','silk'],''),
'p0019_2':([A,'education'],['agricultural-extension'],''),
'p0019_3':([A],['sericulture'],''),
'p0020_1':([A],['sericulture'],''),
'p0020_2':([A],['sericulture','horticulture'],'mulberry seedlings'),
'p0021_1':([A],['livestock'],''),
'p0021_2':([A],['livestock'],''),
'p0022_1':([A],['livestock'],'dairy cattle'),
'p0023_1':([A],['livestock','eggs-and-poultry'],''),
'p0023_2':([A],['livestock'],''),
'p0024_1':([A,'trade'],['livestock'],'slaughterhouses'),
'p0025_1':([A],['livestock','leather-and-furs'],''),
'p0025_2':([A,'colonial-rule'],['arable-land','land-tenure','public-property'],''),
'p0026_1':([A,'colonial-rule'],['arable-land','public-property'],''),
'p0026_2':([A,'colonial-rule'],['arable-land','public-property','land-tenure'],''),
'p0026_3':(['colonial-rule','finance'],['companies','settler-migration','land-tenure'],'Oriental Development Co.'),
'p0026_4':(['colonial-rule','population'],['settler-migration','companies','arable-land'],''),
'p0028_1':([F],['forest-area'],''),
'p0030_1':([F],['forest-area'],''),
'p0030_2':([F],['forest-management','erosion-control'],'protection forest'),
'p0031_1':([F],['forest-management','public-property'],''),
'p0032_1':([F],['forest-management','public-property'],''),
'p0032_2':([F],['timber','forest-management'],''),
'p0033_1':([F],['afforestation'],''),
'p0033_2':([F],['afforestation'],''),
'p0033_3':([F],['afforestation'],''),
'p0034_1':([F],['afforestation','forest-management'],'nurseries'),
'p0036_1':([F],['afforestation'],'seedlings'),
}
d=json.load(open('batches/b01.json'))
v={x['id'] for x in json.load(open('../../vocabulary.json'))['tags']}
tp={x['id'] for x in json.load(open('../../vocabulary.json'))['topics']}
o=[]
for r in d:
    k=r['key'].split(':')[1]; t,g,w=m[k]
    assert set(g)<=v and set(t)<=tp,(k,g,t)
    o.append({'key':r['key'],'topics':t,'tags':g,'flags':[],'why':w or r['en']['t']})
import os;os.makedirs('results',exist_ok=True)
json.dump(o,open('results/b01.json','w'),ensure_ascii=False,indent=1)
print(len(o))
