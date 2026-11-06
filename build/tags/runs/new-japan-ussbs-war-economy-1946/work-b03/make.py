import json,re
base='runs/new-japan-ussbs-war-economy-1946/'
d=json.load(open(base+'batches/b03.json'))
M,F,MI,E,T,L='manufacturing','military','mining','economy','trade','labour'
S={
'C-20':([M],['iron-and-steel'],'scrap steel supply'),
'C-21':([M],['iron-and-steel'],'ingot steel output'),
'C-22':([M],['iron-and-steel'],'finished steel output'),
'C-23':([M],['iron-and-steel'],'rolled steel by product'),
'C-24':([M,F],['iron-and-steel','war-and-mobilisation'],'steel distribution to army/navy/civil'),
'C-25':([M],['iron-and-steel','imports'],'steel supply and demand'),
'C-26':([MI],['mineral-production','manganese'],'ferro-alloy ore output; no chromium/nickel tag'),
'C-27':([T,MI],['imports','commodity-origins'],'ferro-alloy ore imports by source'),
'C-28':([M],['iron-and-steel'],'ferro-alloy output'),
'C-29':([M],[],'aluminium supply; no aluminium tag'),
'C-30':([T,MI],['imports','commodity-origins'],'bauxite imports by origin; no bauxite tag'),
'C-31':([T,MI],['imports'],'aluminous shale imports'),
'C-32':([M,MI],[],'aluminium stocks; no aluminium tag'),
'C-33':([M,F],['economic-controls'],'aluminium allotment to categories; no aluminium tag'),
'C-34':([M],[],'magnesium capacity/supply; no magnesium tag'),
'C-35':([M,MI],['copper'],'copper capacity and supply'),
'C-36':([T,MI],['copper','imports','commodity-origins'],'copper ore imports by origin'),
'C-37':([M],['copper'],'refined copper stocks'),
'C-38':([T,M],['copper','imports','commodity-origins'],'electrolytic copper imports by origin'),
'C-39':([M,MI],['lead-and-zinc'],'lead capacity and supply'),
'C-40':([M,MI],['lead-and-zinc'],'zinc capacity and supply'),
'C-41':([M,MI],['tin'],'tin capacity and supply'),
'C-42':([MI],['coal','imports'],'coal production, trade, supply'),
'C-43':([MI],['coal','mineral-production'],'coal production by territory'),
'C-44':([T,MI],['coal','imports','intra-imperial-trade'],'coal imports by source'),
'C-45':([MI,M],['coal'],'coal consumption by industry'),
'C-46':([MI,M],['coal'],'coal consumption shares by industry'),
'C-47':([MI,'transportation'],['coal','shipping','railways'],'coal movement by water and rail'),
'C-48':([MI,L],['coal','labour-productivity','employment-and-unemployment'],'coal labour force and output per worker'),
'C-49':([MI,M],['petroleum'],'liquid fuels production, consumption, imports'),
'C-50':([MI,T],['petroleum','imports'],'crude oil imports, production, stocks'),
'C-51':([T,MI],['petroleum','imports'],'oil imports'),
'C-52':([MI,F],['petroleum'],'liquid fuel consumption army/navy/civil'),
'C-53':([MI,F],['petroleum'],'liquid fuel inventories'),
'C-54':([M,MI],['petroleum'],'refined oil production by type'),
'C-55':([M],['petroleum'],'synthetic oil output'),
'C-56':([M],['petroleum','rubber'],'lubricating oil from rubber'),
'C-57':([M,F],['arms-and-arsenals','chemicals'],'explosives output'),
'C-58':([M,F],['arms-and-arsenals','chemicals'],'explosives Japan vs US'),
'C-59':([M,F],['arms-and-arsenals','chemicals'],'explosives process efficiency'),
}
voc=open('VOCABULARY.md').read()
ids=set(re.findall(r'^\| `([^`]+)`',voc,re.M))
out=[]
for r in d:
    t,g,w=S[r['table_no']]
    assert set(t+g)<=ids,(t,g)
    out.append(dict(key=r['key'],topics=t,tags=g,flags=[],why=w))
assert [o['key'] for o in out]==[r['key'] for r in d]
json.dump(out,open(base+'results/b03.json','w'),ensure_ascii=False,indent=1)
print(len(out),sum(1 for o in out if o['tags']))
