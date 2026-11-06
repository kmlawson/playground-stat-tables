import json,os
base=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
b=json.load(open(base+'/batches/b06.json'))
M="manufacturing";MI="military";EC="economy";L="labour"
D={
'p0217_1':([M],['machinery'],'machine tool output'),
'p0217_2':([M,'trade'],['machinery','imports','exports'],'machine tools output/trade'),
'p0217_3':([M],['machinery'],'machine-tool industry expansion'),
'p0218_1':([M],['machinery'],'machine tool inventory'),
'p0219_1':([MI,M],['industrial-output','war-and-mobilisation'],'munitions output by type'),
'p0221_1':([MI,M],['industrial-output','war-and-mobilisation'],'munitions production indices'),
'p0222_1':([M],['shipbuilding'],'merchant ship value input'),
'p0224_1':([M],['shipbuilding'],'merchant ship input index'),
'p0226_1':([MI,M],['arms-and-arsenals'],'aircraft production value'),
'p0226_2':([MI,M],['navy','shipbuilding'],'naval vessel production value'),
'p0228_1':([MI,M],['navy','shipbuilding'],'naval ship production indices'),
'p0230_1':([MI,M],['navy','shipbuilding'],'navy delivered tonnage'),
'p0231_2':([MI,M],['navy','shipbuilding'],'fleet unit construction'),
'p0232_1':([MI,M],['arms-and-arsenals'],'ammunition production value'),
'p0232_2':([MI],['army','arms-and-arsenals'],'army ordnance output'),
'p0233_1':([MI],['army','arms-and-arsenals'],'army ordnance output'),
'p0234_1':([MI],['navy','arms-and-arsenals'],'naval ordnance indices'),
'p0236_1':([MI],['arms-and-arsenals','war-and-mobilisation'],'war materiel stocks'),
'p0236_2':([M,'trade'],['road-transport','imports'],'motor vehicle production/imports'),
'p0236_3':([M],['road-transport'],'truck production planned/actual'),
'p0236_4':([M],['road-transport'],'motor vehicle output value'),
'p0236_5':([M],['road-transport'],'motor vehicle output index'),
'p0237_1':([MI,M],['army','arms-and-arsenals'],'tank production'),
'p0238_1':([MI,M],['arms-and-arsenals','aviation'],'aircraft production monthly'),
'p0238_2':([MI,M],['arms-and-arsenals','aviation'],'aircraft production indices'),
'p0238_3':([MI,M],['arms-and-arsenals','aviation'],'aircraft by functional type'),
'p0239_1':([MI,M],['arms-and-arsenals','aviation'],'aircraft type shares'),
'p0239_2':([EC,'welfare'],['food-supply-and-rationing'],'civilian goods availability index'),
'p0240_1':([EC],['prices','price-controls'],'official retail price index'),
'p0241_1':([EC],['prices','inflation'],'black market prices'),
'p0242_1':([EC],['prices'],'wholesale prices'),
'p0242_2':(['welfare',EC],['cost-of-living'],'salaried living costs'),
'p0243_1':(['welfare',EC],['cost-of-living'],'workers living cost'),
'p0244_1':([L],['wages'],'factory wages'),
'p0245_1':([L],['wages'],'transport wages'),
'p0245_2':([L],['wages'],'miners wages'),
'p0245_3':(['mining','welfare'],['food-supply-and-rationing','coal'],'miners food and coal output'),
'p0246_1':(['trade',M],['imports','textiles'],'textile raw material imports'),
'p0246_2':([M,'trade'],['textiles','imports','exports'],'cloth production and trade'),
'p0246_3':([M],['textiles'],'cloth production'),
}
v=json.load(open(os.path.expanduser('~/shell/projects/yearbooks/japanyearbooks/stat-tables-site/build/tags/vocabulary.json')))
T={t['id'] for t in v['topics']};G={t['id'] for t in v['tags']}
out=[]
for r in b:
    t,g,w=D[r['key'].split(':')[1]]
    assert set(t)<=T and set(g)<=G and len(t)<=2 and len(g)<=3,r['key']
    out.append({"key":r['key'],"topics":t,"tags":g,"flags":[],"why":w})
os.makedirs(base+'/results',exist_ok=True)
json.dump(out,open(base+'/results/b06.json','w'),ensure_ascii=False,indent=1)
print(len(out),sum(1 for o in out if o['tags']))
