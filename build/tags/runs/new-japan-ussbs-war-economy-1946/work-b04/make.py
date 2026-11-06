import json
d=json.load(open('batches/b04.json'))
M='manufacturing'
R={
'p0162_1':([M],['salt'],'salt production/consumption'),
'p0162_2':([M,'agriculture'],['fertilisers'],'chemical fertiliser output'),
'p0163_1':([M],['chemicals','fertilisers'],'nitrogen balance'),
'p0165_1':([M],['chemicals'],'ammonia production/distribution'),
'p0166_1':([M],['chemicals'],'nitric acid'),
'p0168_1':([M,'trade'],['rubber','imports'],'crude rubber imports/consumption'),
'p0169_1':([M],['rubber'],'synthetic rubber by company'),
'p0170_1':([M],['chemicals'],'calcium carbide'),
'p0171_1':([M],['fertilisers','chemicals'],'superphosphates'),
'p0171_2':([M],['chemicals'],'carbon disulfide'),
'p0172_1':([M,'trade'],['chemicals'],'naphthalene prod/trade'),
'p0172_2':([M,'trade'],['chemicals'],'acetone prod/trade'),
'p0173_1':([M,'trade'],['chemicals'],'butanol'),
'p0173_2':([M,'trade'],['chemicals'],'glycerine'),
'p0173_3':(['trade'],['imports','fertilisers'],'phosphorite imports by source'),
'p0174_1':([M,'trade'],['fertilisers','chemicals'],'ammonium sulfate, cyanamide'),
'p0175_1':([M],['chemicals'],'caustic soda'),
'p0176_1':([M],['chemicals'],'chlorine'),
'p0178_1':([M],['chemicals'],'sulfuric acid'),
'p0179_1':([M,'military'],['chemicals'],'tetraethyl lead army/navy'),
'p0180_1':([M],['chemicals'],'toluol'),
'p0181_2':([M],['industrial-output'],'organic glass, labour'),
'p0183_1':([M],['chemicals'],'methanol'),
'p0184_2':([M],['alcohol'],'ethyl alcohol'),
'p0185_1':([M],['chemicals'],'soda ash'),
'p0186_1':([M,'trade'],['vegetable-oils'],'fats and oils'),
'p0186_2':([M],['chemicals'],'sodium cyanide'),
'p0187_1':([M],['chemicals'],'benzol'),
'p0187_2':([M],['paper-and-pulp','rayon'],'rayon pulp'),
'p0188_1':([M],['chemicals'],'oxygen'),
'p0188_2':(['utilities'],['electricity','hydroelectricity'],'generation hydro/thermal'),
'p0189_1':(['utilities'],['electricity','hydroelectricity'],'generating capacity'),
'p0189_2':(['transportation'],['railways'],'government rail line lengths'),
'p0190_1':(['transportation'],['railways','trams'],'private rail and tram companies'),
'p0190_2':(['transportation'],['railways'],'freight cars'),
'p0190_3':(['transportation'],['railways'],'locomotives'),
'p0191_1':(['transportation'],['railways'],'rail tonnage, ton-miles'),
'p0191_2':(['transportation'],['railways'],'rail freight by commodity'),
'p0191_3':(['transportation'],['railways'],'haul length, train miles'),
'p0192_1':(['transportation','military'],['shipping','war-and-mobilisation'],'merchant marine in war'),
}
out=[]
for r in d:
    k=r['key'].split(':')[1];t,g,w=R[k]
    out.append(dict(key=r['key'],topics=t,tags=g,flags=[],why=w))
assert len(out)==len(d)==len(R)
json.dump(out,open('results/b04.json','w'),ensure_ascii=False,indent=1)
v=json.load(open('/Users/kml/shell/projects/yearbooks/japanyearbooks/stat-tables-site/build/tags/vocabulary.json'))
ids={x['id'] for x in v['tags']};ts={x['id'] for x in v['topics']}
assert all(set(o['tags'])<=ids and set(o['topics'])<=ts for o in out)
print(len(out),sum(1 for o in out if o['tags']))
