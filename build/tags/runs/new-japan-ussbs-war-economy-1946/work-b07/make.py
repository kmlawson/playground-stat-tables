import json
P='japan-ussbs-war-economy-1946:'
M={
'p0246_4':(['manufacturing','trade'],['silk','exports','imports'],'raw silk output, trade, stocks'),
'p0246_5':(['manufacturing','trade'],['silk','textiles','exports'],'silk cloth'),
'p0246_6':(['manufacturing'],['silk'],'misc silk statistics'),
'p0247_1':(['manufacturing','trade'],['cotton','imports','exports'],'raw cotton'),
'p0247_2':(['manufacturing','trade'],['cotton','textiles','exports'],'cotton cloth'),
'p0248_1':(['manufacturing','trade'],['wool','imports','exports'],'raw wool'),
'p0248_2':(['manufacturing'],['wool','textiles'],'woolen cloth civilian supply'),
'p0248_3':(['manufacturing','trade'],['rayon','textiles','imports'],'synthetic cloth'),
'p0249_1':(['manufacturing'],['leather-and-furs'],'civilian footwear output'),
'p0249_2':(['trade','manufacturing'],['imports','leather-and-furs'],'leather imports'),
'p0249_3':(['trade','manufacturing'],['exports','leather-and-furs'],'leather exports'),
'p0249_4':(['manufacturing'],['leather-and-furs'],'monthly hides and leather'),
'p0249_5':(['trade','manufacturing'],['rubber','imports'],'crude rubber imports, consumption'),
'p0250_1':(['manufacturing'],['rubber'],'rubber production'),
'p0250_2':(['manufacturing','trade'],['paper-and-pulp','imports','exports'],'pulp'),
'p0251_1':(['manufacturing','trade'],['paper-and-pulp','imports','exports'],'paper'),
'p0251_2':(['agriculture','economy'],['food-supply-and-rationing','cereals','exports'],'staple food supply'),
'p0252_2':(['agriculture'],['crop-production'],'principal foods production'),
'p0252_3':(['agriculture'],['arable-land'],'arable land expansion'),
'p0253_1':(['agriculture'],['arable-land','crop-production'],'arable and crop acreage'),
'p0254_1':(['agriculture'],['rice','wheat','barley'],'per-acre yields'),
'p0254_2':(['trade','agriculture'],['rice','imports'],'rice imports Korea Formosa'),
'p0254_3':(['trade','agriculture'],['sugar','imports'],'net sugar imports'),
'p0254_4':(['agriculture','economy'],['food-supply-and-rationing'],'food stocks'),
'p0254_5':(['military','agriculture'],['food-supply-and-rationing'],'foods allotted to armed services'),
'p0255_1':(['fisheries','trade'],['fish-and-fish-products','imports'],'marine products'),
'p0255_2':(['agriculture','health'],['nutrition','food-supply-and-rationing'],'caloric food sources'),
}
d=json.load(open('batches/b07.json'))
v=json.load(open('../../vocabulary.json'))
ids={t['id'] for t in v['tags']} if isinstance(v['tags'],list) else set(v['tags'])
out=[]
for r in d:
    t,g,w=M[r['key'].split(':')[1]]
    for x in g: assert x in ids,x
    out.append(dict(key=r['key'],topics=t,tags=g,flags=[],why=w))
assert [o['key'] for o in out]==[r['key'] for r in d]
json.dump(out,open('results/b07.json','w'),ensure_ascii=False,indent=1)
print(len(out))
