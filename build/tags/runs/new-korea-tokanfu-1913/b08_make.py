import json
M={
'p0193_2':(['communications','finance'],['postal-services'],'treasury funds via post offices'),
'p0193_3':(['communications','finance'],['postal-services'],'communications revenue/expenditure'),
'p0194_1':(['geography','government'],['land-surveys'],'triangulation'),
'p0194_2':(['geography','government'],['land-surveys'],'preliminary land survey'),
'p0194_3':(['geography','government'],['land-surveys'],'control/detail survey'),
'p0195_1':(['geography','government'],['land-surveys','land-tax'],'land grade survey for tax'),
'p0195_2':(['geography','government'],['land-surveys','land-registration'],'map/register proofreading'),
'p0195_3':(['geography','government'],['land-surveys','land-area'],'area computation'),
'p0195_4':(['geography','government'],['land-surveys'],'cadastral map drawing'),
'p0196_1':(['government','geography'],['land-registration','land-surveys'],'land registers prepared'),
'p0196_2':(['crime-and-justice','government'],['land-registration','civil-litigation'],'land disputes'),
'p0196_3':(['geography','finance'],['land-surveys','public-property','land-area'],'state land by category'),
'p0196_4':(['geography','agriculture'],['land-surveys','land-tenure','land-area'],'private land by category'),
'p0197_1':(['geography','government'],['land-surveys'],'urban parcels surveyed'),
'p0198_1':(['transportation'],['roads-and-bridges'],'road improvement sections'),
'p0199_1':(['transportation'],['roads-and-bridges'],'road length and cost by province'),
'p0199_2':(['finance','utilities'],['public-budgets','roads-and-bridges'],'local civil engineering spending'),
'p0199_3':(['finance','utilities'],['public-budgets'],'treasury subsidies for local works'),
'p0200_1':(['transportation'],['ports'],'harbour works'),
'p0200_2':(['transportation','finance'],['ports','public-budgets'],'harbour works budget'),
'p0200_3':(['utilities'],['water-and-sewerage'],'waterworks'),
'p0201_1':(['disasters'],['floods','disaster-losses'],'flood damage'),
'p0202_1':(['crime-and-justice','government'],['police'],'police offices'),
'p0202_2':(['crime-and-justice','government'],['police'],'police personnel'),
'p0203_1':(['crime-and-justice','military'],['police'],'gendarmerie units and staff'),
'p0203_2':(['crime-and-justice'],['summary-justice','offences-and-convictions','nationality-and-ethnicity'],'summary judgments by nationality'),
'p0204_1':(['crime-and-justice'],['offences-and-convictions'],'theft/fraud victims'),
'p0206_1':(['crime-and-justice'],['offences-and-convictions','police'],'theft/fraud detection'),
'p0208_1':(['crime-and-justice','military'],['riots-and-civil-unrest'],'insurgent clashes'),
'p0209_1':(['crime-and-justice','military'],['riots-and-civil-unrest'],'insurgents four-year comparison'),
'p0210_1':(['disasters'],['fires'],'fires by cause'),
'p0211_1':(['disasters'],['fires'],'fires by month'),
'p0212_1':(['disasters','government'],['firefighting'],'fire brigades'),
'p0212_2':(['population','crime-and-justice'],['suicide'],'suicide/homicide deaths'),
'p0213_1':(['population','crime-and-justice'],['suicide'],'unnatural deaths, abandoned children'),
'p0217_1':(['crime-and-justice','welfare'],['police'],'police rescue work'),
'p0218_1':(['crime-and-justice','welfare'],['police'],'persons rescued by police'),
'p0219_1':(['crime-and-justice','government'],['police'],'police casualties'),
'p0220_1':(['crime-and-justice','government'],['police'],'police casualties by cause'),
'p0221_1':(['crime-and-justice','government'],['passports-and-travel-permits'],'residence bans'),
}
d=json.load(open('batches/b08.json'))
out=[]
for r in d:
    t,g,w=M[r['key'].split(':')[1]]
    out.append({'key':r['key'],'topics':t,'tags':g,'flags':[],'why':w})
v=json.load(open('../../vocabulary.json'))
T={x['id'] for x in v['topics']};G={x['id'] for x in v['tags']}
assert all(set(o['topics'])<=T and set(o['tags'])<=G for o in out)
assert len(out)==len(d)==40
json.dump(out,open('results/b08.json','w'),ensure_ascii=False,indent=1)
print(len(out),sum(1 for o in out if o['tags']))
