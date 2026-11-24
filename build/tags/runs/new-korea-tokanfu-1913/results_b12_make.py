import json
b=json.load(open('batches/b12.json'))
S='schools-and-pupils'
m={
1:(['education'],[S,'secondary-education'],'middle schools'),
2:(['education'],['secondary-education','public-property'],'middle school assets'),
3:(['education'],['secondary-education',S],'girls higher schools'),
4:(['education'],['secondary-education','public-property'],'girls school assets'),
5:(['education'],['vocational-education',S],'vocational schools'),
6:(['education'],['vocational-education','public-property'],'vocational assets'),
7:(['education'],[S],'private misc schools'),
8:(['education'],['kindergartens'],'kindergartens'),
9:(['education'],[S,'primary-education'],'schools for Koreans by province'),
10:(['education'],['primary-education','teachers',S],'common school teachers pupils'),
11:(['education'],['primary-education',S],'entrants graduates'),
12:(['education'],['primary-education',S],'dropouts deaths'),
13:(['education'],['primary-education',S],'attendance'),
14:(['education'],['primary-education',S],'pupils by year'),
15:(['education'],['primary-education',S],'pupil age'),
16:(['education'],['primary-education','public-property'],'common school assets'),
17:(['education'],['primary-education','teachers'],'teacher qualification salary'),
18:(['education'],['secondary-education','teacher-training',S],'govt secondary schools'),
19:(['education'],['secondary-education','public-property'],'govt school assets'),
20:(['education'],['vocational-education',S],'vocational schools'),
21:(['education'],['vocational-education','public-property'],'vocational assets'),
22:(['education'],['vocational-education',S],'simple vocational'),
23:(['education'],['vocational-education',S],'agri-forestry school'),
24:(['education'],['vocational-education',S],'industrial institute'),
25:(['education','health'],['vocational-education',S],'medical training school'),
26:(['education'],[S],'private schools general/religious'),
27:(['education'],['traditional-schools'],'sodang'),
28:(['education'],['kindergartens'],'kindergartens'),
29:(['education'],['students-abroad'],'students in Japan'),
30:(['education'],['books'],'textbooks distributed'),
31:(['education'],['libraries'],'libraries'),
32:(['press'],['newspapers','periodicals'],'newspapers magazines'),
33:(['religion'],['missions','religious-institutions'],'Japanese missions'),
34:(['religion'],['buddhism','religious-institutions'],'temples monks'),
35:(['religion'],['christianity','missions'],'Christian missions'),
36:(['welfare','government'],['welfare-institutions'],'relief institute staff'),
37:(['welfare'],['child-welfare','charitable-institutions'],'orphanage'),
38:(['welfare','education'],['special-education','charitable-institutions'],'blind deaf dept'),
39:(['welfare','health'],['poor-relief'],'sick travellers relief'),
40:(['welfare','health'],['poor-relief','diseases'],'travellers by disease'),
}
out=[]
for i,r in enumerate(b,1):
    t,g,w=m[i]
    out.append(dict(key=r['key'],topics=t,tags=g,flags=['text-tables'] if i==32 and False else [],why=w))
json.dump(out,open('results/b12.json','w'),ensure_ascii=False,indent=1)
v=json.load(open('../../vocabulary.json'));T=v['tags'];ids={t['id'] for t in T} if isinstance(T,list) else set(T)
tp={t['id'] if isinstance(t,dict) else t for t in v['topics']}
for o in out:
    assert set(o['tags'])<=ids and set(o['topics'])<=tp,o
print(len(out))
