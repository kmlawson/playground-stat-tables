import json
B='/Users/kml/shell/projects/yearbooks/japanyearbooks/stat-tables-site/build/tags/'
inp=json.load(open(B+'runs/new-japan-keishicho-1938/batches/b05.json'))
S=['health'];V=['veterinary-health']
m={
93:(["health"],["veterinary-health","diseases"],"rabies cases humans/animals"),
}
L=[
(["health","agriculture"],["veterinary-health","diseases"],"rabies, humans and animals"),
(["health"],["veterinary-health","diseases"],"dogs, rabid dogs, bites"),
(["health"],["vaccination","veterinary-health"],"dog rabies vaccination"),
(["agriculture","health"],["livestock","veterinary-health"],"cattle TB inspection"),
(["agriculture","health"],["livestock","veterinary-health"],"cattle TB by ward"),
(["health","manufacturing"],["food-inspection"],"ice makers pass/fail"),
(["health","manufacturing"],["food-inspection"],"ice output and tests"),
(["health"],["pharmaceuticals"],"patent medicine inspection"),
(["health"],["pharmaceuticals"],"drug inspection tours"),
(["health"],["public-health","diseases"],"rat extermination, plague bacteria"),
(["health"],["epidemics"],"pathogen carriers by year"),
(["health"],["epidemics"],"pathogen carriers by station"),
(["health","population"],["births-and-deaths","diseases"],"deaths by cause by year"),
(["health","population"],["births-and-deaths","diseases","age-and-sex"],"deaths by cause and age"),
(["health","population"],["births-and-deaths","diseases"],"deaths by cause and month"),
(["health"],["diseases"],"bacteriological tests"),
(["health"],["suicide"],"suicide by method yearly"),
(["health"],["suicide"],"suicide by method"),
(["health","population"],["suicide","marriage-and-divorce"],"suicide residence, marital status"),
(["health"],["suicide"],"suicide by cause yearly"),
(["health"],["suicide"],"suicide by cause"),
(["health"],["suicide","age-and-sex"],"completed suicide cause by age"),
(["health"],["suicide","age-and-sex"],"attempted suicide cause by age"),
(["health"],["suicide"],"suicide by city/district"),
(["health"],["suicide"],"suicide by month"),
(["crime-and-justice"],["offences-and-convictions"],"killed/wounded by cause yearly"),
(["crime-and-justice"],["offences-and-convictions"],"killed/wounded by month"),
(["crime-and-justice"],["offences-and-convictions"],"killed/wounded by cause"),
(["crime-and-justice"],["offences-and-convictions"],"killed/wounded by city"),
(["disasters","health"],["disaster-losses","transport-accidents"],"accidental deaths by cause yearly"),
(["disasters","health"],["disaster-losses","transport-accidents"],"accidental deaths by cause"),
(["disasters","health"],["disaster-losses"],"accidental deaths by month"),
(["disasters","health"],["disaster-losses"],"accidental deaths by city"),
(["government","crime-and-justice"],["police"],"lost and found property yearly"),
(["government","crime-and-justice"],["police"],"lost and found by area"),
(["government","crime-and-justice"],["police"],"lost/found disposal"),
(["government"],["police"],"lost and found by month"),
(["government","welfare"],["police"],"personal consultations by station"),
(["government","welfare"],["police"],"personal consultations by month"),
(["crime-and-justice"],["police"],"surveillance of released/probation/juvenile offenders"),
]
assert len(L)==len(inp),(len(L),len(inp))
out=[{"key":r["key"],"topics":t,"tags":g,"flags":[],"why":w} for r,(t,g,w) in zip(inp,L)]
v=json.load(open(B+'vocabulary.json'))
json.dump(out,open(B+'runs/new-japan-keishicho-1938/results/b05.json','w'),ensure_ascii=False,indent=1)
txt=json.dumps(v,ensure_ascii=False)
bad=[i for o in out for i in o['topics']+o['tags'] if '"%s"'%i not in txt]
print(len(out),sum(1 for o in out if o['tags']),set(bad))
