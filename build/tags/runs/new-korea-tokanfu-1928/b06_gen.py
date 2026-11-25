import json
d=json.load(open('batches/b06.json'))
M={
'p0162_2':(['transportation'],['railways','tourism'],'railway hotels'),
'p0163_1':(['transportation'],['railways'],'railway warehouses'),
'p0164_1':(['transportation'],['transport-accidents','railways'],'railway casualties'),
'p0164_2':(['transportation','crime-and-justice'],['railways','offences-and-convictions'],'railway offenders'),
'p0164_3':(['transportation','labour'],['railways','wages'],'workshop employees wages'),
'p0165_1':(['transportation'],['railways','trams'],'private lines'),
'p0166_1':(['transportation'],['railways','trams'],'private line traffic'),
'p0167_1':(['transportation'],['railways','construction'],'construction costs'),
'p0168_1':(['transportation'],['railways','trams'],'revenue expenditure'),
'p0169_1':(['transportation'],['railways'],'light railway'),
'p0169_2':(['transportation'],['navigation-aids'],'lights beacons'),
'p0169_3':(['transportation'],['shipping'],'ships'),
'p0170_1':(['transportation'],['shipping'],'designated routes'),
'p0170_2':(['transportation'],['shipping'],'ferry vessels'),
'p0170_3':(['transportation'],['shipping'],'ferry traffic'),
'p0170_4':(['transportation'],['shipping'],'ferry passengers by class'),
'p0171_1':(['transportation'],['shipping'],'ferry by month'),
'p0171_2':(['communications'],['postal-services','telegraph','telephone'],'facilities'),
'p0172_1':(['communications'],['postal-services'],'ordinary mail'),
'p0172_2':(['communications'],['postal-services'],'parcels'),
'p0173_1':(['communications','finance'],['postal-remittances'],'money orders'),
'p0173_2':(['communications','finance'],['postal-remittances'],'foreign money orders'),
'p0173_3':(['finance','communications'],['savings-and-loans'],'postal savings'),
'p0174_1':(['finance','communications'],['savings-and-loans'],'savings flows'),
'p0174_2':(['finance','communications'],['savings-and-loans'],'securities for savers'),
'p0174_3':(['finance','communications'],['postal-remittances','savings-and-loans'],'transfer accounts'),
'p0175_1':(['communications'],['telegraph'],'telegraph lines'),
'p0175_2':(['communications'],['telegraph'],'telegrams'),
'p0176_1':(['communications'],['telephone'],'telephone lines'),
'p0177_1':(['communications'],['telephone'],'local calls'),
'p0177_2':(['communications'],['telephone'],'long-distance calls'),
'p0177_3':(['communications','education'],[],'communications staff training'),
'p0178_1':(['transportation'],['roads-and-bridges'],'road length'),
'p0178_2':(['transportation'],['roads-and-bridges','construction'],'road construction'),
'p0179_1':(['finance','government'],['public-budgets','construction'],'local public works spending'),
'p0179_2':(['utilities'],['water-and-sewerage'],'waterworks'),
'p0180_1':(['finance','government'],['public-budgets','construction'],'public works subsidies'),
'p0181_1':(['transportation'],['ports','construction'],'harbour works'),
'p0182_1':(['disasters'],['floods','disaster-losses'],'flood damage'),
'p0182_2':(['geography','transportation'],['flood-control','river-conservancy'],'river works'),
}
out=[]
for r in d:
  k=r['key'].split(':')[1]; t,g,w=M[k]
  out.append({'key':r['key'],'topics':t,'tags':g,'flags':[],'why':w})
json.dump(out,open('results/b06.json','w'),ensure_ascii=False,indent=1)
v=json.load(open('../../vocabulary.json'))
ids={x['id'] for x in v['tags']}|{x['id'] for x in v['topics']}
print(len(out),sum(1 for o in out if o['tags']),[i for o in out for i in o['topics']+o['tags'] if i not in ids])
