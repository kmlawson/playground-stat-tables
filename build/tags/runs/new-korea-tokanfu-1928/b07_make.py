import json
d=json.load(open('batches/b07.json'))
M={
'p0183_1':(['crime-and-justice'],['police'],'police offices, staff'),
'p0183_2':(['crime-and-justice'],['offences-and-convictions'],'crimes detected, dispositions'),
'p0187_1':(['crime-and-justice'],['offences-and-convictions'],'crimes by offence'),
'p0189_1':(['crime-and-justice'],['offences-and-convictions'],'crimes by province'),
'p0189_2':(['crime-and-justice'],['summary-justice'],'summary judgment cases'),
'p0190_1':(['crime-and-justice'],['summary-justice'],'persons sentenced summarily'),
'p0192_1':(['crime-and-justice'],['offences-and-convictions'],'theft/fraud victims'),
'p0192_2':(['crime-and-justice'],['offences-and-convictions'],'theft/fraud detected'),
'p0192_3':(['transportation'],['shipping','transport-accidents'],'vessels in distress'),
'p0193_1':(['disasters'],['fires','disaster-losses'],'fires by province'),
'p0193_2':(['disasters'],['fires'],'fires by cause'),
'p0193_3':(['disasters'],['firefighting'],'fire brigades'),
'p0194_1':(['population','crime-and-justice'],['births-and-deaths'],'unnatural deaths'),
'p0194_2':(['population'],['suicide','age-and-sex'],'suicides by age, cause'),
'p0197_1':(['welfare'],['child-welfare'],'abandoned children'),
'p0197_2':(['welfare','crime-and-justice'],['police','poor-relief'],'police rescue work'),
'p0200_1':(['crime-and-justice'],['police'],'private firearms licensing'),
'p0201_1':(['crime-and-justice','government'],['police'],'police-regulated businesses'),
'p0201_2':(['crime-and-justice','government'],['police'],'business suspensions/revocations'),
'p0202_1':(['health'],['medical-services','public-health'],'health institutions'),
'p0203_1':(['health'],['epidemics','diseases'],'infectious disease'),
'p0208_1':(['health'],['epidemics','diseases'],'infectious disease fatality'),
'p0209_1':(['health'],['epidemics','occupations'],'disease by occupation'),
'p0210_1':(['health'],['epidemics','age-and-sex'],'disease by age'),
'p0212_1':(['health'],['epidemics','diseases'],'disease by month'),
'p0213_1':(['health','crime-and-justice'],['sex-work','public-health'],'medical exams of prostitutes'),
'p0215_1':(['health'],['vaccination'],'vaccinations'),
'p0217_1':(['health'],['medical-services'],'govt hospital staff, expenses'),
'p0217_2':(['health'],['medical-services'],'provincial hospitals'),
'p0219_1':(['health'],['medical-services','diseases'],'hospital patients by disease'),
'p0221_1':(['health'],['medical-services'],'itinerant treatment'),
'p0222_1':(['health'],['quarantine'],'vessel quarantine'),
'p0222_2':(['crime-and-justice'],['courts'],'judicial personnel'),
'p0223_1':(['crime-and-justice'],['civil-litigation','courts'],'first-instance civil'),
'p0226_1':(['crime-and-justice'],['civil-litigation','courts'],'second-instance civil'),
'p0227_1':(['crime-and-justice'],['civil-litigation','courts'],'third-instance civil'),
'p0227_2':(['crime-and-justice'],['civil-litigation'],'suit amounts'),
'p0230_1':(['crime-and-justice'],['civil-litigation'],'civil suits by parties'),
'p0231_1':(['crime-and-justice'],['civil-litigation','courts'],'civil appeals'),
'p0231_2':(['crime-and-justice'],['mediation-and-arbitration','civil-litigation'],'conciliation cases'),
}
out=[]
for r in d:
    t,g,w=M[r['key'].split(':')[1]]
    out.append(dict(key=r['key'],topics=t,tags=g,flags=[],why=w))
json.dump(out,open('results/b07.json','w'),ensure_ascii=False,indent=1)
v=json.load(open('../../vocabulary.json'))
T=set(v['topics']) if isinstance(v['topics'],dict) else {x['id'] for x in v['topics']}
G=set(v['tags']) if isinstance(v['tags'],dict) else {x['id'] for x in v['tags']}
print(len(out),[x for o in out for x in o['topics'] if x not in T],[x for o in out for x in o['tags'] if x not in G],sum(1 for o in out if o['tags']))
