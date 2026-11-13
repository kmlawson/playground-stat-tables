import json
b=json.load(open('runs/new-korea-keishu-1934/batches/b03.json'))
T="text-tables"
m={
"p0139_1":(["history"],["historical-chronologies"],[T],"Silla kings and clans"),
"p0141_1":(["history"],[],[T],"notable persons list"),
"p0141_2":(["population"],["nationality-and-ethnicity"],[T],"clans list, Kyongju seat"),
"p0142_1":(["history"],[],[T],"clans, founders, notable people"),
"p0143_1":(["population"],["nationality-and-ethnicity","households"],[],"household heads by surname"),
"p0147_1":(["population"],["nationality-and-ethnicity"],[T],"single-clan village list"),
"p0147_2":(["population","agriculture"],["households","land-tenure"],[],"clan villages households and tenure"),
"p0156_1":(["population"],["households"],[],"large households 1930"),
"p0157_1":(["population"],["nationality-and-ethnicity","households"],[],"single-clan villages households/pop"),
"p0173_1":(["agriculture","welfare"],["rural-development","land-tenure"],[],"model villages"),
"p0175_1":(["agriculture","finance"],["rural-development","cooperatives"],[],"association assets"),
"p0175_2":(["agriculture","finance"],["cooperatives","mutual-credit"],[T],"mutual aid association outline"),
"p0180_1":(["education"],["schools-and-pupils"],[],"schools classes teachers pupils"),
"p0181_1":(["education"],["primary-education","schools-and-pupils"],[],"Japanese elementary schools"),
"p0181_2":(["education"],["primary-education","schools-and-pupils"],[],"common schools"),
"p0183_1":(["education"],["education-finance"],[],"tuition arrears"),
"p0184_1":(["education"],["schools-and-pupils"],[],"monthly dropouts"),
"p0184_2":(["education"],["education-finance"],[],"tuition burden arrears"),
"p0185_1":(["education","labour"],["schools-and-pupils","occupations"],[],"graduate destinations"),
"p0187_1":(["education","religion"],["confucianism","traditional-schools"],[],"academy holdings"),
"p0187_2":(["culture","religion"],["confucianism","books"],[T],"academy book list"),
"p0188_1":(["culture","religion"],["confucianism","books"],[T],"family document list"),
"p0188_2":(["culture","religion"],["confucianism","books"],[T],"family book list"),
"p0191_1":(["religion","education"],["confucianism","traditional-schools"],[],"Confucian scholars by address"),
"p0192_1":(["religion","education"],["confucianism","traditional-schools"],[],"Confucian scholars by province"),
"p0193_1":(["education"],["language-education","literacy-and-adult-education"],[],"Japanese-language ability"),
"p0193_2":(["education"],["literacy-and-adult-education","literacy-and-adult-education"][:1],[],"literacy by township"),
"p0194_1":(["press"],["newspapers","periodicals"],[],"subscribers"),
"p0197_1":(["religion"],["religious-institutions","shinto","buddhism"],[],"religion institutions clergy believers"),
"p0217_1":(["crime-and-justice"],["offences-and-convictions","police"],[],"crimes occurred cleared"),
"p0220_1":(["disasters"],["fires"],[],"fires by cause"),
"p0220_2":(["crime-and-justice","population"],["police","births-and-deaths"],[],"unnatural deaths"),
"p0221_1":(["health"],["epidemics","diseases"],[],"infectious disease"),
"p0221_2":(["health","welfare"],["public-health","poor-relief"],[],"sick/dead travellers"),
"p0224_1":(["agriculture"],["households","occupations","nationality-and-ethnicity"],[],"farm households by nationality"),
"p0225_1":(["agriculture"],["land-tenure"],[],"households by tenure"),
"p0225_2":(["agriculture"],["arable-land"],[],"cultivated area"),
"p0226_1":(["agriculture"],["land-tenure","arable-land"],[],"owner/tenant area"),
"p0227_1":(["agriculture"],["rice","crop-production"],[],"rice area harvest"),
"p0227_2":(["agriculture"],["barley","cereals"],[],"barley area harvest"),
}
out=[]
for r in b:
    k=r['key'].split(':')[1]; t,g,f,w=m[k]
    g=list(dict.fromkeys(g))
    out.append(dict(key=r['key'],topics=t,tags=g,flags=f,why=w))
v=json.load(open('vocabulary.json'));ids={x['id'] for x in v['tags']}
for o in out: assert all(x in ids for x in o['tags']),o
assert len(out)==len(b)
json.dump(out,open('runs/new-korea-keishu-1934/results/b03.json','w'),ensure_ascii=False,indent=1)
print(len(out),sum(1 for o in out if o['tags']))
