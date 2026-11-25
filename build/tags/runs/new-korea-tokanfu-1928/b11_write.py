import json
d=json.load(open('batches/b11.json'))
H='higher-education';S='schools-and-pupils';P='public-property';T='teacher-training'
R=[(['education'],[H,S],'private colleges'),(['education'],[H,S],'entrants/graduates'),(['education'],[H,S],'withdrawals'),
(['education'],[H,S],'univ prep course'),(['education','finance'],[P,H],'prep assets'),(['education'],[H,S,'teachers'],'univ chairs staff students'),
(['education'],[H,S],'univ movements'),(['education','finance'],[P,H],'univ assets'),(['education'],[T,S],'normal school'),
(['education','finance'],[P,T],'normal school assets'),(['education'],[T,S],'public normal schools'),(['education','finance'],[P,T],'normal school assets'),
(['education'],[T,S],'teacher institutes'),(['education'],[S],'public misc schools'),(['education'],[S],'private misc schools'),
(['education','religion'],[S],'religious misc schools'),(['education'],['traditional-schools',S],'sodang'),(['education'],['students-abroad'],'students in Japan'),
(['education','culture'],['libraries'],'libraries'),(['education'],['books'],'textbook distribution'),
(['religion'],['religious-institutions','shinto','buddhism'],'shrines and temples'),(['religion'],['buddhism','religious-institutions'],'temples monks'),
(['religion'],['religious-institutions','buddhism','christianity'],'churches by denomination'),(['religion'],['religious-affiliation','religious-institutions'],'preachers believers'),
(['welfare','government'],['welfare-institutions','charitable-institutions'],'relief institute staff'),(['welfare'],['child-welfare','charitable-institutions'],'orphanage'),
(['welfare','education'],['special-education','charitable-institutions'],'blind and deaf'),(['welfare'],['poor-relief'],'travellers aid'),
(['welfare','health'],['diseases','poor-relief'],'sick travellers by illness'),(['welfare'],['charitable-institutions'],'Red Cross members'),
(['welfare'],['charitable-institutions'],'women association members'),(['welfare'],['poor-relief','imperial-household'],'imperial relief grants'),
(['welfare','disasters'],['disaster-relief'],'disaster victim relief'),(['welfare'],['poor-relief'],'destitute relief'),
(['welfare'],['welfare-institutions'],'social work facilities'),(['government'],['government-offices','wages'],'officials salaries'),
(['government'],['government-offices','wages'],'salaries by office'),(['government'],['government-offices','local-government','wages'],'provincial fund staff'),
(['government'],['local-government','wages'],'city/county staff'),(['government','education'],['teachers','wages'],'school association staff')]
assert len(R)==len(d)
out=[{"key":r['key'],"topics":t,"tags":g,"flags":[],"why":w} for r,(t,g,w) in zip(d,R)]
v=json.load(open('/Users/kml/shell/projects/yearbooks/japanyearbooks/stat-tables-site/build/tags/vocabulary.json'))
txt=json.dumps(v)
for o in out:
    for i in o['topics']+o['tags']: assert '"%s"'%i in txt,i
json.dump(out,open('results/b11.json','w'),ensure_ascii=False,indent=1)
print(len(out),sum(1 for o in out if o['tags']))
