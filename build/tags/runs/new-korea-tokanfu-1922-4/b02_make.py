import json
d=json.load(open('batches/b02.json'))
R={
'p0019_1':(['communications'],['postal-services'],'postal matter'),
'p0019_2':(['finance','communications'],['savings-and-loans'],'postal savings'),
'p0019_3':(['utilities'],['electricity'],'electric enterprises'),
'p0019_4':(['finance','colonial-rule'],['public-budgets'],'special account revenue budget'),
'p0019_5':(['finance','colonial-rule'],['public-budgets'],'special account expenditure budget'),
'p0020_1':(['finance'],['taxation'],'taxes'),
'p0020_2':(['finance','agriculture'],['state-monopolies','ginseng'],'red ginseng monopoly'),
'p0020_3':(['finance','government'],['public-budgets','local-government'],'local expenses budget'),
'p0021_1':(['agriculture','utilities'],['irrigation'],'irrigation associations'),
'p0021_2':(['education','finance'],['education-finance'],'school associations budgets'),
'p0021_3':(['education'],['schools-and-pupils'],'schools and pupils'),
'p0022_1':(['welfare','health'],['charitable-institutions','medical-services'],'relief hospital'),
'p0022_2':(['religion'],['shinto','buddhism','religious-institutions'],'shrines and temples'),
'p0022_3':(['religion'],['religious-institutions'],'religious propagation'),
'p0022_4':(['health'],['medical-services'],'hospitals physicians'),
'p0022_5':(['health'],['diseases','epidemics'],'infectious disease'),
'p0023_1':(['utilities','health'],['water-and-sewerage'],'waterworks'),
'p0023_2':(['crime-and-justice'],['courts'],'courts and cases'),
'p0023_3':(['crime-and-justice','government'],['police'],'police offices'),
'p0023_4':(['crime-and-justice','government'],['police'],'police officials'),
'p0023_5':(['crime-and-justice'],['prisons'],'prisons'),
'p0023_6':(['population','education'],['languages','language-education'],'Japanese-language comprehension'),
'p0025_1':(['transportation'],['railways'],'railway mileage'),
'p0026_1':(['transportation'],['railways'],'railway land and rolling stock'),
'p0026_2':(['transportation'],['railways'],'train operating results'),
'p0027_1':(['transportation'],['railways'],'passenger freight traffic'),
'p0027_2':(['transportation','finance'],['railways'],'transport revenue'),
'p0028_1':(['transportation'],['railways'],'through traffic'),
'p0029_1':(['transportation','trade'],['railways','freight-and-transport-costs'],'freight tons'),
'p0030_1':(['transportation'],['railways'],'station traffic'),
'p0035_1':(['transportation','finance'],['railways','construction'],'railway construction costs'),
'p0036_1':(['transportation','finance'],['railways','construction'],'construction cost allotments'),
'p0037_1':(['transportation','finance'],['railways'],'repair works cost'),
'p0037_2':(['transportation','finance'],['railways'],'railway revenue expenditure'),
'p0037_3':(['transportation','finance'],['railways'],'railway investment'),
'p0038_1':(['transportation','trade'],['railways','tourism'],'railway hotels'),
'p0038_2':(['transportation','trade'],['railways','warehousing'],'railway warehouses'),
'p0039_1':(['transportation','health'],['transport-accidents','railways'],'railway casualties'),
'p0040_1':(['transportation','crime-and-justice'],['railways','offences-and-convictions'],'railway law violators'),
'p0040_2':(['transportation','labour'],['railways','wages'],'railway workshop employees wages'),
}
out=[]
for r in d:
    t,g,w=R[r['key'].split(':')[1]]
    out.append(dict(key=r['key'],topics=t,tags=g,flags=[],why=w))
json.dump(out,open('results/b02.json','w'),ensure_ascii=False,indent=1)
v=json.load(open('../../vocabulary.json'))
ids={x['id'] for x in v['topics']}|{x['id'] for x in v['tags']}
print(len(out),[i for o in out for i in o['topics']+o['tags'] if i not in ids])
