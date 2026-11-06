import json
P='p%s'
S='japan-ussbs-war-economy-1946:'
d={
'0196_1':(['manufacturing','transportation'],['shipbuilding'],'annual merchant ship construction'),
'0196_2':(['transportation'],['shipping'],'merchant fleet by size and type'),
'0196_3':(['manufacturing','transportation'],['shipbuilding'],'monthly merchant ship deliveries'),
'0198_1':(['manufacturing','transportation'],['shipbuilding'],'kihansen construction'),
'0199_1':(['transportation','military'],['shipping','petroleum'],'tanker fleet wartime use'),
'0200_1':(['transportation','military'],['shipping','war-and-mobilisation'],'merchant marine condition at war end'),
'0202_1':(['trade'],['foreign-trade'],'exports and imports 1900-43'),
'0203_1':(['trade'],['imports','industrial-output'] if False else ['imports'],'bulk commodity imports'),
'0204_1':(['trade'],['imports'],'quantity and value of imports'),
'0205_1':(['trade'],['imports','coal'],'coal imports by origin'),
'0205_2':(['trade'],['imports','iron-ore'],'iron ore imports'),
'0206_1':(['trade'],['imports'],'bauxite imports; no bauxite tag'),
'0206_2':(['trade'],['imports','iron-and-steel'],'iron and steel imports'),
'0207_1':(['trade'],['imports','iron-and-steel'],'scrap iron imports'),
'0207_2':(['trade'],['imports','lead-and-zinc'],'lead imports'),
'0208_1':(['trade'],['imports','tin'],'tin imports'),
'0208_2':(['trade'],['imports','lead-and-zinc'],'zinc imports'),
'0209_1':(['trade'],['imports','phosphate-rock'],'phosphate imports'),
'0209_2':(['trade'],['imports'],'dolomite magnesite imports'),
'0210_1':(['trade'],['imports','salt'],'salt imports'),
'0210_2':(['trade','agriculture'],['imports','oilseeds'],'soybean cake imports'),
'0211_1':(['trade','agriculture'],['imports','soybeans'],'soybean imports'),
'0211_2':(['trade','agriculture'],['imports','rice'],'rice imports'),
'0212_1':(['trade','agriculture'],['imports','cereals'],'grain and flour imports'),
'0212_2':(['trade'],['imports','rubber'],'raw rubber imports'),
'0213_1':(['manufacturing'],['industrial-output','machinery'],'electrical equipment production'),
'0213_2':(['trade','manufacturing'],['exports','machinery'],'electrical equipment exports'),
'0213_3':(['trade','manufacturing'],['imports','machinery'],'electrical equipment imports'),
'0214_1':(['economy','military'],['construction'],'construction volume army navy'),
'0214_2':(['military','economy'],['construction'],'army construction'),
'0214_3':(['military','economy'],['construction'],'navy construction'),
'0215_1':(['economy'],['construction'],'nonmilitary construction'),
'0215_2':(['manufacturing'],['cement-and-bricks','iron-and-steel'],'building materials output index'),
'0215_3':(['manufacturing'],['cement-and-bricks'],'cement mill capacity'),
'0215_4':(['manufacturing'],['cement-and-bricks','construction'],'cement consumption by user'),
'0216_1':(['manufacturing'],['cement-and-bricks'],'overseas cement production'),
'0216_2':(['trade','manufacturing'],['exports','cement-and-bricks'],'cement exports'),
'0216_3':(['military','manufacturing'],['iron-and-steel','construction'],'rolled steel consumption'),
'0216_4':(['forestry','trade'],['timber','imports'],'lumber production imports exports'),
'0216_5':(['forestry'],['timber'],'lumber consumption by use'),
}
b=json.load(open('../batches/b05.json'))
v=json.load(open('/Users/kml/shell/projects/yearbooks/japanyearbooks/stat-tables-site/build/tags/vocabulary.json'))
T={t['id'] for t in v['topics']};G={t['id'] for t in v['tags']}
out=[]
for r in b:
    k=r['key'].split(':p')[1]
    t,g,w=d[k]
    assert set(t)<=T and set(g)<=G,(k,t,g)
    out.append(dict(key=r['key'],topics=t,tags=g,flags=[],why=w))
assert [o['key'] for o in out]==[r['key'] for r in b]
json.dump(out,open('../results/b05.json','w'),ensure_ascii=False,indent=1)
print(len(out),sum(1 for o in out if o['tags']))
