import json
b=json.load(open('batches/b03.json'))
M={
'p0090_3':(['forestry'],['timber'],0,'log rafting volume'),
'p0091_1':(['forestry','trade'],['timber'],0,'timber purchases/sales'),
'p0091_2':(['government','fisheries'][:0] or ['government','forestry'][:1]+['culture'][:0] or ['government'],['hunting'],0,'hunting licences'),
'p0092_1':(['fisheries'],['fishing'],0,'fishery households'),
'p0092_2':(['fisheries'],['fishing'],0,'fishing vessels'),
'p0093_1':(['fisheries'],['fishing'],0,'fishing gear'),
'p0094_1':(['fisheries','government'],['fishing-rights-and-licences'],0,'fishery licences'),
'p0095_1':(['fisheries'],['fishing'],0,'boats and catch'),
'p0095_2':(['fisheries'],['fish-and-fish-products'],0,'catch by species'),
'p0096_1':(['fisheries'],['aquaculture'],0,'culture area'),
'p0097_1':(['fisheries','manufacturing'],['fish-and-fish-products'],0,'marine products'),
'p0097_2':(['fisheries'],['whaling'],0,'whaling'),
'p0097_3':(['fisheries','trade'],['fish-and-fish-products'],0,'fish markets'),
'p0097_4':(['fisheries'],['fishing'],0,'associations with member and fund figures'),
'p0098_1':(['mining','manufacturing'],['salt'],0,'state salt production'),
'p0098_2':(['trade','mining'],['salt','imports'],0,'salt imports'),
'p0099_1':(['mining','government'],['mining-rights-and-concessions'],0,'mining applications'),
'p0099_2':(['mining','government'],['mining-rights-and-concessions'],0,'applications by mineral'),
'p0100_1':(['mining','government'],['mining-rights-and-concessions'],0,'permits by mineral'),
'p0101_1':(['mining'],['mining-rights-and-concessions'],0,'mining claims area'),
'p0102_1':(['mining'],['mining-rights-and-concessions','nationality-and-ethnicity'],0,'claims by nationality'),
'p0103_1':(['mining'],['mining-rights-and-concessions'],0,'working/idle claims'),
'p0105_1':(['mining'],['mining-rights-and-concessions','nationality-and-ethnicity'],0,'claims by nationality'),
'p0106_1':(['mining'],['mineral-production'],0,'mineral output'),
'p0107_1':(['mining'],['mineral-production','nationality-and-ethnicity'],0,'output by nationality'),
'p0108_1':(['mining'],['mineral-production'],0,'output by mine'),
'p0109_1':(['mining','government'],[],0,'mining office staff/engines'),
'p0110_1':(['trade','finance'],['companies'],0,'companies'),
'p0112_1':(['finance'],['insurance-and-pensions'],0,'insurance'),
'p0115_1':(['trade'],['markets-and-exchanges'],0,'markets'),
'p0116_1':(['manufacturing','trade'],['tobacco'],0,'tobacco'),
'p0117_1':(['trade'],['measurement-and-units'],0,'weights sellers'),
'p0117_2':(['trade'],['measurement-and-units'],0,'weights sales'),
'p0118_1':(['manufacturing'],['industrial-output'],0,'factories'),
'p0119_1':(['manufacturing'],['industrial-output'],0,'industrial product value'),
'p0119_2':(['utilities'],['electricity'],0,'electric utilities'),
'p0119_3':(['manufacturing','government'],['printing'],0,'printing office'),
'p0119_4':(['education','manufacturing'],['vocational-education'],0,'industrial training institutes'),
'p0120_1':(['finance'],['banking'],0,'bank offices'),
'p0120_2':(['finance'],['currency'],0,'currency in circulation'),
}
out=[]
for r in b:
  t,g,f,w=M[r['key'].split(':')[1]]
  out.append({'key':r['key'],'topics':t,'tags':g,'flags':['text-tables'] if f else [],'why':w})
v=json.load(open('../../vocabulary.json'))
T={x['id'] if isinstance(x,dict) else x for x in (v['topics'] if isinstance(v['topics'],list) else v['topics'].values())}
G={x['id'] for x in v['tags']} if isinstance(v['tags'],list) else set(v['tags'])
for o in out:
  assert all(x in T for x in o['topics']) and all(x in G for x in o['tags']),o
assert [o['key'] for o in out]==[r['key'] for r in b]
json.dump(out,open('results/b03.json','w'),ensure_ascii=False,indent=1)
print(len(out),sum(1 for o in out if o['tags']))
