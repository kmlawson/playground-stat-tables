import json
P='japan-ussbs-war-economy-1946:'
M={
'p0096_3':(['manufacturing','economy'],['chemicals'],'synthetic production estimates'),
'p0096_4':(['economy'],['national-income-and-wealth'],'real GNP estimates compared'),
'p0097_1':(['manufacturing','military'],['aviation','industrial-output'],'combat airplane production estimates'),
'p0097_2':(['manufacturing'],['industrial-output'],'aluminum capacity'),
'p0097_3':(['manufacturing'],['industrial-output'],'aluminum requirements'),
'p0098_1':(['manufacturing'],['industrial-output'],'aluminum production'),
'p0100_1':(['economy'],['national-income-and-wealth'],'GNP by component'),
'p0101_1':(['military','finance'],['war-and-mobilisation','public-budgets'],'war expenditures'),
'p0102_1':(['military','finance'],['army','public-budgets'],'army expenditures'),
'p0103_1':(['military','finance'],['navy','public-budgets'],'navy expenditures'),
'p0103_2':(['military','finance'],['public-budgets'],'munitions ministry expenditures'),
'p0103_3':(['military','finance'],['war-and-mobilisation','public-budgets'],'war expenditures by object'),
'p0104_1':(['finance'],['public-budgets'],'national government expenditures'),
'p0104_2':(['finance'],['public-budgets'],'nonwar expenditure derivation'),
'p0105_1':(['finance','government'],['public-budgets','local-government'],'local government expenditures'),
'p0105_2':(['finance','government'],['public-budgets','local-government'],'local expenditure derivation'),
'p0106_1':(['economy','manufacturing'],['national-income-and-wealth'],'private plant and equipment spending'),
'p0106_2':(['economy','utilities'],['construction','housing'],'residential construction derivation'),
'p0107_1':(['trade','finance'],['balance-of-payments'],'balance of payments'),
'p0108_1':(['economy'],['household-budgets','national-income-and-wealth'],'consumer expenditures by category'),
'p0112_1':(['economy','trade'],['prices'],'wholesale price series'),
'p0114_1':(['population','labour'],['occupations','age-and-sex'],'population and labour force by sex and activity'),
'p0115_1':(['population','labour'],['age-and-sex','employment-and-unemployment'],'civilian labour force by age and sex'),
'p0116_1':(['labour','population'],['occupations'],'labour force distribution by activity'),
'p0116_2':(['labour','population'],['occupations'],'labour force distribution by sex'),
'p0117_1':(['labour','manufacturing'],['occupations'],'labour force by industry and sex'),
'p0118_1':(['labour','manufacturing'],['employment-and-unemployment'],'manufacturing workers change'),
'p0118_2':(['labour','military'],['war-and-mobilisation','employment-and-unemployment'],'labour conscription'),
'p0119_1':(['population','labour'],['nationality-and-ethnicity','occupations'],'resident Koreans by occupation'),
'p0119_2':(['labour','population'],['migration','nationality-and-ethnicity'],'Korean contract workers'),
'p0120_1':(['labour'],['nationality-and-ethnicity','employment-and-unemployment'],'Korean Chinese POW workers'),
'p0120_2':(['education','labour'],['students-abroad'][:0]+['schools-and-pupils','war-and-mobilisation'],'students mobilized for work'),
'p0122_1':(['labour'],['employment-and-unemployment','wages'],'employment and earnings index'),
'p0123_1':(['labour'],['employment-and-unemployment','labour-productivity'],'employment and man-hours'),
'p0123_2':(['military'],['army','navy'],'armed forces strength'),
'p0123_3':(['labour','agriculture'],['migration','employment-and-unemployment'],'farm labor to industry'),
'p0124_1':(['trade','mining'],['imports','coal'],'coking coal imports by source'),
'p0125_1':(['trade','mining'],['imports','iron-ore'],'iron ore imports by source'),
'p0126_1':(['mining','trade'],['iron-ore','mineral-production'],'iron ore supply'),
'p0127_1':(['trade','manufacturing'],['imports','iron-and-steel'],'pig iron imports by source'),
}
d=json.load(open('batches/b02.json'));out=[]
for r in d:
    t,g,w=M[r['key'].split(':')[1]]
    out.append({'key':r['key'],'topics':t,'tags':g,'flags':[],'why':w})
json.dump(out,open('results/b02.json','w'),ensure_ascii=False,indent=1)
v=json.load(open('../../vocabulary.json'));ids={x['id'] for x in v['tags']}|{x['id'] for x in v['topics']}
assert all(i in ids for o in out for i in o['topics']+o['tags']),[i for o in out for i in o['topics']+o['tags'] if i not in ids]
print(len(out),sum(1 for o in out if o['tags']))
