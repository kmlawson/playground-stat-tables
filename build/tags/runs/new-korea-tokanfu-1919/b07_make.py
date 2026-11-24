import json
d=json.load(open('batches/b07.json'))
CJ,CS,CC,H,CJ_='crime-and-justice','courts','civil-litigation','health',None
m={
'p0195_2':(['disasters'],['fires']),
'p0195_3':(['disasters','government'],['firefighting']),
'p0196_1':(['crime-and-justice','population'],[]),
'p0196_2':(['population','crime-and-justice'],['suicide']),
'p0197_1':(['welfare','crime-and-justice'],['child-welfare']),
'p0198_1':(['crime-and-justice','welfare'],['police']),
'p0199_1':(['crime-and-justice'],['police']),
'p0200_1':(['crime-and-justice'],['police']),
'p0201_1':(['health'],['medical-services']),
'p0202_1':(['health'],['diseases','epidemics']),
'p0204_1':(['health'],['diseases']),
'p0205_1':(['health'],['diseases']),
'p0207_1':(['health'],['diseases']),
'p0208_1':(['health'],['public-health']),
'p0209_2':(['health'],['vaccination']),
'p0211_1':(['health'],['vaccination']),
'p0211_2':(['health','government'],['medical-services']),
'p0212_1':(['health'],['medical-services','diseases']),
'p0215_1':(['health'],['medical-services']),
'p0215_2':(['health'],['medical-services']),
'p0216_1':(['health','transportation'],['quarantine','shipping']),
}
for k in ['p0216_2','p0217_1','p0217_2','p0217_3','p0218_1','p0218_2','p0219_1','p0219_2','p0219_3','p0219_4','p0220_1','p0220_2','p0220_3','p0220_4']:
    m[k]=(['crime-and-justice'],['civil-litigation','courts'])
m['p0217_3']=(['crime-and-justice'],['civil-litigation'])
m['p0220_1']=(['crime-and-justice','economy'],['civil-litigation'])
m['p0221_1']=(['crime-and-justice'],['courts'])
m['p0222_1']=(['crime-and-justice'],['courts'])
m['p0222_2']=(['crime-and-justice'],['courts'])
m['p0222_3']=(['crime-and-justice'],['land-registration'])
m['p0223_1']=(['crime-and-justice'],['courts'])
out=[]
for r in d:
    t,g=m[r['key'].split(':')[1]]
    out.append({'key':r['key'],'topics':t,'tags':g,'flags':[],'why':r['en']['t'][:60]})
json.dump(out,open('results/b07.json','w'),ensure_ascii=False,indent=1)
print(len(out),sum(1 for o in out if o['tags']))
