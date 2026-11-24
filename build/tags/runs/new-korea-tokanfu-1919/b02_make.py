import json
d=json.load(open('batches/b02.json'))
A={
'p0069_2':(['agriculture','population'],['nationality-and-ethnicity','households'],'farm households by race'),
'p0070_1':(['agriculture'],['rice'],'rice acreage and yield'),
'p0071_1':(['agriculture'],['barley','wheat'],'barley wheat'),
'p0072_1':(['agriculture'],['crop-production'],'pulses; no pulse tag'),
'p0073_1':(['agriculture'],['cereals'],'millet etc'),
'p0073_2':(['agriculture'],['industrial-crops','cotton'],'cotton and other industrial crops'),
'p0075_1':(['agriculture'],['horticulture'],'sweet potato, potato, vegetables'),
'p0076_1':(['agriculture'],['horticulture'],'fruit trees'),
'p0076_2':(['agriculture'],['farm-inputs'],'green manure cultivation'),
'p0077_1':(['agriculture'],['sericulture'],'silkworms mulberry'),
'p0077_2':(['agriculture'],['sericulture'],'tussah silkworms'),
'p0078_1':(['agriculture','education'],['agricultural-extension'],'agri training institutes'),
'p0078_2':(['agriculture'],['sericulture'],'cooperative silkworm rearing'),
'p0078_3':(['agriculture'],['sericulture'],'silkworm egg production'),
'p0078_4':(['agriculture'],['sericulture'],'mulberry seedlings'),
'p0079_1':(['agriculture'],['livestock'],'breeding bulls'),
'p0079_2':(['agriculture'],['livestock'],'bull servicing'),
'p0080_1':(['agriculture'],['livestock'],'dairy cattle'),
'p0080_2':(['agriculture'],['livestock','eggs-and-poultry'],'livestock and poultry'),
'p0081_1':(['agriculture'],['livestock'],'cattle births slaughter'),
'p0081_2':(['agriculture'],['livestock'],'slaughterhouses'),
'p0082_1':(['agriculture'],['livestock','leather-and-furs'],'livestock products, hides'),
'p0082_2':(['agriculture'],['land-tenure'],'state land leases'),
'p0083_1':(['agriculture'],['land-tenure'],'state land grants'),
'p0083_2':(['agriculture'],['land-tenure'],'state land leases by purpose'),
'p0083_3':(['colonial-rule','finance'],['companies'],'Oriental Development Co business'),
'p0083_4':(['colonial-rule','agriculture'],['settler-migration'],'ODC settlers and allotments'),
'p0084_1':(['forestry'],['forest-area'],'forest area'),
'p0084_2':(['forestry'],['forest-area','erosion-control'],'protection forests'),
'p0085_1':(['forestry'],['forest-management'],'forest leases and sales'),
'p0085_2':(['forestry'],['forest-management'],'state forest transfers'),
'p0086_1':(['forestry'],['timber','forest-management'],'state forest products disposal'),
'p0086_2':(['forestry'],['afforestation'],'state afforestation'),
'p0086_3':(['forestry'],['afforestation'],'local afforestation'),
'p0087_1':(['forestry'],['afforestation'],'commemorative planting'),
'p0087_2':(['forestry'],['afforestation'],'tree nurseries'),
'p0088_1':(['forestry'],['afforestation'],'seedling distribution'),
'p0089_1':(['forestry'],['afforestation'],'private nurseries'),
'p0090_1':(['forestry','education'],['afforestation'],'school forests'),
'p0090_2':(['forestry'],['timber'],'felling and sawing'),
}
out=[]
for r in d:
    t,g,w=A[r['key'].split(':')[1]]
    out.append({'key':r['key'],'topics':t,'tags':g,'flags':[],'why':w})
v=json.load(open('../../vocabulary.json'))
s=json.dumps(v)
for o in out:
    for x in o['tags']+o['topics']:
        assert '"%s"'%x in s,x
json.dump(out,open('results/b02.json','w'),ensure_ascii=False,indent=1)
print(len(out),sum(1 for o in out if o['tags']))
