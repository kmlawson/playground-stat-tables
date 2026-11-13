import json
d=json.load(open('batches/b02.json'))
S={
'p0055_2':(["culture"],["museums-and-heritage","tourism"],[],"museum visitors by month"),
'p0064_1':(["history","culture"],["archaeology","museums-and-heritage"],[],"tomb finds"),
'p0069_1':(["history"],["archaeology"],[],"Silla royal tombs by surname"),
'p0090_1':(["welfare"],["housing"],[],"houses by roof and size"),
'p0092_1':(["culture"],[],[],"coloured clothing share"),
'p0092_2':(["culture"],[],[],"men's hair styles"),
'p0095_1':(["utilities"],["electricity"],[],"lighting households"),
'p0096_1':(["forestry"],["fuelwood-and-charcoal"],[],"fuel consumption"),
'p0096_2':(["forestry"],["fuelwood-and-charcoal"],[],"fuel production"),
'p0103_1':(["culture","welfare"],["marriage-and-divorce","household-budgets"],[],"wedding costs"),
'p0107_1':(["culture","welfare"],["household-budgets"],[],"funeral costs"),
'p0109_1':(["trade"],["domestic-trade","nationality-and-ethnicity"],[],"restaurants by Japanese/Korean operators"),
'p0110_1':(["labour","crime-and-justice"],["sex-work","nationality-and-ethnicity"],[],"geisha/barmaids by nationality"),
'p0110_2':(["labour","crime-and-justice"],["sex-work","nationality-and-ethnicity"],[],"geisha/barmaids by origin"),
'p0123_1':(["population"],["population-totals","administrative-divisions"],[],"villages with population growth"),
'p0123_2':(["population"],["population-totals","administrative-divisions"],[],"villages with population decline"),
}
out=[]
for r in d:
    k=r['key'].split(':')[1]
    if k in S: t,g,f,w=S[k]
    elif '地勢' in r['title'] or '山岳' in r['title']:
        t,g,f,w=["geography"],["physical-geography"],["text-tables"],"township topography gazetteer"
    else:
        t,g,f,w=["population"],["households","population-totals"],[],"households and population by village"
    out.append(dict(key=r['key'],topics=t,tags=g,flags=f,why=w))
json.dump(out,open('results/b02.json','w'),ensure_ascii=False,indent=1)
print(len(out),sum(1 for o in out if o['tags']))
