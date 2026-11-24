import json
D='/Users/kml/shell/projects/yearbooks/japanyearbooks/stat-tables-site/build/tags/runs/new-korea-tokanfu-1913/'
inp=json.load(open(D+'batches/b09.json'))
H=(["health"],)
m={
'p0221_2':(["crime-and-justice"],["police"],"firearms owned, police chapter"),
'p0222_1':(["crime-and-justice","economy"],["police"],"police-supervised trades"),
'p0229_1':(["health"],["medical-services"],"institutions and practitioners"),
'p0236_5':(["health","crime-and-justice"],["sex-work","medical-services"],"health exams of prostitutes"),
'p0237_1':(["health"],["vaccination"],"vaccinations"),
'p0238_1':(["health"],["vaccination"],"vaccinations"),
'p0238_2':(["health"],["medical-services"],"hospital staff and expenses"),
'p0239_1':(["health"],["medical-services"],"hospital patients"),
'p0240_1':(["health"],["medical-services"],"charity hospital staff"),
'p0241_1':(["health"],["medical-services"],"charity hospital patients"),
'p0241_2':(["health"],["medical-services"],"itinerant clinics"),
'p0242_1':(["health","transportation"],["quarantine","ports"],"vessel quarantine by port"),
'p0243_1':(["crime-and-justice"],["courts","legal-profession"],"court staff and lawyers"),
'p0243_2':(["crime-and-justice"],["mediation-and-arbitration","civil-litigation"],"civil conciliation"),
'p0245_1':(["crime-and-justice"],["mediation-and-arbitration","civil-litigation"],"compromise cases"),
'p0245_2':(["crime-and-justice"],["mediation-and-arbitration","civil-litigation"],"compromise cases by type"),
'p0258_1':(["crime-and-justice"],["civil-litigation","nationality-and-ethnicity"],"suits by party nationality"),
'p0260_1':(["crime-and-justice"],["civil-litigation","nationality-and-ethnicity"],"foreign parties by nationality"),
'p0260_2':(["crime-and-justice"],["civil-litigation","courts"],"civil appeals"),
}
dis=['p0230_1','p0231_1','p0233_1','p0234_1','p0236_2','p0236_3']
dis_age=['p0232_1','p0232_2','p0235_1','p0236_1','p0236_4']
for k in dis: m[k]=(["health"],["diseases","epidemics"],"notifiable infectious diseases")
for k in dis_age: m[k]=(["health","population"],["diseases","epidemics"],"infectious disease deaths by age")
for k in ['p0247_1','p0250_1','p0251_1','p0252_1','p0253_1','p0254_1','p0254_2','p0254_3','p0254_4','p0255_1']:
    m[k]=(["crime-and-justice"],["civil-litigation","courts"],"civil suits")
out=[]
for r in inp:
    t,g,w=m[r['key'].split(':')[1]]
    out.append({"key":r['key'],"topics":t,"tags":g,"flags":[],"why":w})
json.dump(out,open(D+'results/b09.json','w'),ensure_ascii=False,indent=1)
print(len(inp),len(out),sum(1 for o in out if o['tags']))
