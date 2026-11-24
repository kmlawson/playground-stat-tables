import json
d=json.load(open('batches/b06.json'))
M={
'p0140_4':(['finance'],['banking'],'bank exchange business'),
'p0140_5':(['finance'],['mutual-credit','savings-and-loans'],'local financial associations'),
'p0141_2':(['finance'],['banking'],'clearing house bills'),
'p0141_3':(['finance'],['interest-rates','banking'],'bank rates'),
'p0141_4':(['finance'],['interest-rates','banking'],'agri-industrial bank rates'),
'p0142_1':(['finance'],['interest-rates','banking'],'ordinary bank rates'),
'p0142_2':(['finance'],['interest-rates','banking'],'ordinary bank rates'),
'p0142_3':(['finance'],['interest-rates'],'moneylender rates'),
'p0143_1':(['trade','economy'],['prices','cereals'],'grain prices'),
'p0143_2':(['trade','economy'],['prices','rice'],'unhulled rice prices'),
'p0143_3':(['trade','economy'],['prices','rice'],'brown rice prices'),
'p0144_1':(['trade','economy'],['prices','rice'],'polished rice prices'),
'p0145_1':(['trade','economy'],['prices','soybeans'],'soybean prices'),
'p0145_2':(['trade','economy'],['prices'],'commodity prices'),
'p0149_1':(['labour'],['wages'],'wages by trade'),
'p0153_1':(['trade','government'],[],'customs house list'),
'p0154_1':(['trade'],['foreign-trade'],'exports and imports value'),
'p0154_2':(['trade'],['exports','ports'],'exports by port'),
'p0155_1':(['trade'],['imports','ports'],'imports by port'),
'p0155_2':(['trade'],['exports'],'exports by month'),
'p0155_3':(['trade'],['imports'],'imports by month'),
'p0156_1':(['trade'],['foreign-trade'],'trade by country'),
'p0157_1':(['trade'],['exports'],'exports by destination'),
'p0159_1':(['trade'],['imports'],'imports by origin'),
'p0164_1':(['trade','finance'],['gold','silver','foreign-trade'],'gold silver trade'),
'p0165_1':(['trade','finance'],['gold','silver','foreign-trade'],'gold silver by country'),
'p0165_2':(['transportation','trade'],['shipping','ports'],'vessels entering clearing'),
'p0165_3':(['finance','trade'],['customs-revenue'],'customs duties'),
'p0166_1':(['trade'],[],'bonded warehouse goods'),
'p0167_1':(['trade'],['foreign-trade','customs-revenue'],'frontier trade and duties'),
'p0167_2':(['transportation'],['railways'],'railway lines stock'),
'p0167_3':(['transportation'],['railways','route-distances'],'section mileages'),
'p0168_1':(['transportation'],['railways'],'train operations'),
'p0168_2':(['transportation'],['railways'],'rail traffic'),
'p0169_1':(['transportation','finance'],['railways','freight-and-transport-costs'],'rail revenue'),
'p0169_2':(['transportation'],['railways'],'rail traffic by month'),
'p0170_1':(['transportation','finance'],['railways'],'rail revenue by month'),
'p0170_2':(['transportation'],['railways'],'through traffic'),
'p0171_1':(['transportation','trade'],['railways'],'principal freight'),
'p0171_2':(['transportation'],['railways'],'station traffic'),
}
out=[]
for r in d:
    t,g,w=M[r['key'].split(':')[1]]
    out.append({'key':r['key'],'topics':t,'tags':g,'flags':[],'why':w})
v=json.load(open('../../vocabulary.json'))
ids={x['id'] for x in v['tags']}|set(v['pilot_additions']['tags'])|set(v['approved_additions']['tags'])
for o in out:
    for x in o['tags']:
        assert x in ids,x
json.dump(out,open('results/b06.json','w'),ensure_ascii=False,indent=1)
print(len(out),sum(1 for o in out if o['tags']))
