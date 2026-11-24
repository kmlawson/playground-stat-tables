import json
d=json.load(open('batches/b02.json'))
E_=['education']
m={
'p0033_3':(E_,['higher-education','schools-and-pupils'],'medical college status'),
'p0033_4':(E_,['higher-education'],'college property'),
'p0034_1':(E_,['higher-education','vocational-education'],'technical school'),
'p0034_2':(E_,['higher-education','vocational-education'],'technical school property'),
'p0034_3':(E_,['higher-education','vocational-education'],'agri-forestry school'),
'p0034_4':(E_,['higher-education','vocational-education'],'agri-forestry property'),
'p0034_5':(E_,['higher-education','vocational-education'],'commercial school'),
'p0035_2':(E_,['higher-education','vocational-education'],'commercial school property'),
'p0035_3':(E_,['higher-education','mission-schools'],'Severance private medical college'),
'p0035_4':(E_,['higher-education','mission-schools'],'Yonhi private college'),
'p0035_5':(E_,['higher-education'],'Posong private college'),
'p0035_6':(E_,['teacher-training','schools-and-pupils'],'normal school'),
'p0036_1':(E_,['primary-education','schools-and-pupils'],'attached elementary school'),
'p0036_2':(E_,['teacher-training'],'normal school property'),
'p0036_3':(E_,['teacher-training','schools-and-pupils'],'public normal schools'),
'p0036_4':(E_,['teacher-training'],'normal school property'),
'p0036_5':(E_,['teacher-training'],'temporary teacher institutes'),
'p0036_6':(E_,['schools-and-pupils','teachers'],'public misc schools'),
'p0037_1':(E_,['schools-and-pupils','teachers'],'private misc schools'),
'p0038_1':(E_,['traditional-schools','schools-and-pupils'],'sodang village schools'),
'p0039_1':(['education','culture'],['libraries'],'libraries'),
'p0039_2':(E_,['students-abroad','higher-education'],'students supported in Japan'),
'p0040_1':(E_,[],'textbook distribution'),
'p0042_1':(['religion'],['religious-institutions','religious-affiliation'],'shrines temples churches summary'),
'p0043_1':(['religion'],['shinto','buddhism','religious-institutions'],'shrines and temples'),
'p0043_2':(['religion'],['buddhism','religious-institutions'],'temples, monks, nuns'),
'p0044_1':(['religion'],['christianity','religious-institutions'],'churches, mission stations'),
'p0046_1':(['religion'],['religious-affiliation','religious-institutions'],'propagators and believers'),
'p0050_1':(['welfare','government'],['charitable-institutions'],'relief institute staff'),
'p0050_2':(['welfare'],['child-welfare','charitable-institutions'],'nursery division'),
'p0051_1':(['welfare','health'],['poor-relief'],'sick and dead travellers'),
'p0051_2':(['welfare','education'],['special-education','charitable-institutions'],'blind and deaf-mute division'),
'p0053_1':(['health','welfare'],['diseases','poor-relief'],'travellers by illness'),
'p0055_1':(['welfare'],['charitable-institutions'],'Red Cross members'),
'p0055_2':(['welfare'],['charitable-institutions'],'Patriotic Women Assoc members'),
'p0056_1':(['welfare'],['poor-relief'],'imperial relief grants by province'),
'p0056_2':(['welfare','disasters'],['disaster-relief'],'disaster victims relief'),
'p0057_1':(['welfare'],['poor-relief'],'poor relief'),
'p0057_2':(['welfare'],['welfare-institutions','poor-relief'],'relief institutions list'),
'p0060_1':(['government'],['government-offices'],'official salaries'),
}
out=[]
for r in d:
    k=r['key'].split(':')[1]
    t,g,w=m[k]
    out.append({'key':r['key'],'topics':t,'tags':g,'flags':[],'why':w})
v=json.load(open('../../vocabulary.json'))
T={x['id'] for x in v['topics']};G={x['id'] for x in v['tags']}
for o in out:
    assert all(x in T for x in o['topics']),o
    assert all(x in G for x in o['tags']),o
assert [o['key'] for o in out]==[r['key'] for r in d]
json.dump(out,open('results/b02.json','w'),ensure_ascii=False,indent=1)
print(len(out),sum(1 for o in out if o['tags']))
