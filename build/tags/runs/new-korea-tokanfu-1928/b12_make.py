import json
d=json.load(open('batches/b12.json'))
G='government';F='finance'
m={
'p0367_3':([G],['local-government','government-offices'],'township heads and staff'),
'p0368_1':([G],['local-government','government-offices'],'township clerks posted'),
'p0368_2':([G],['local-government'],'ward heads'),
'p0369_1':([G],['imperial-household','government-offices','wages'],'Yi household office staff salaries'),
'p0369_2':([F,G],['insurance-and-pensions'],'pensions and annuities'),
'p0370_1':([F],['public-budgets'],'special account revenue/expenditure'),
'p0370_2':([F],['public-budgets'],'special account comparison'),
'p0371_1':([F],['public-budgets'],'revenue budget'),
'p0371_2':([F],['public-budgets'],'expenditure budget'),
'p0372_1':([F],['public-budgets','railways'],'railway stores fund account'),
'p0372_2':([F],['public-budgets'],'continuing expenditures'),
'p0373_1':([F],['land-tax','taxation'],'land tax'),
'p0373_2':([F],['land-tax','taxation'],'urban land tax'),
'p0374_1':([F],['land-tax'],'wasteland, land tax'),
'p0374_2':([F],['land-tax'],'wasteland, urban land tax'),
'p0375_1':([F],['land-tax'],'tax-exempt land'),
'p0375_2':([F],['land-tax'],'tax-exempt urban land'),
'p0376_1':([F],['land-tax','taxation'],'taxpayers by amount, land'),
'p0376_2':([F],['land-tax','taxation'],'taxpayers by amount, urban land'),
'p0377_1':([F],['taxation'],'income tax'),
'p0378_1':([F],['taxation'],'income taxpayers by amount'),
'p0379_1':([F,'manufacturing'],['alcohol','taxation'],'liquor tax brewed'),
'p0379_2':([F,'manufacturing'],['alcohol','taxation'],'liquor tax distilled'),
'p0380_1':([F,'manufacturing'],['alcohol','taxation'],'liquor tax reprocessed'),
'p0380_2':([F,'manufacturing'],['alcohol','taxation'],'Korean liquor tax'),
'p0380_3':([F,'manufacturing'],['alcohol','taxation'],'home-use liquor tax'),
'p0380_4':([F,'trade'],['alcohol','taxation'],'imported liquor tax'),
'p0380_5':([F,'trade'],['alcohol','taxation'],'imported distilled liquor tax'),
'p0381_1':([F,'trade'],['alcohol','taxation'],'imported reprocessed liquor tax'),
'p0381_2':([F,'agriculture'],['tobacco','taxation'],'home-grown tobacco tax'),
'p0382_1':([F,'manufacturing'],['sugar','taxation'],'sugar consumption tax'),
'p0384_1':([F,'mining'],['taxation','mining-rights-and-concessions'],'mining area tax'),
'p0384_2':([F,'mining'],['taxation','mineral-production'],'mineral output tax'),
'p0384_3':([F,'mining'],['taxation','mining-rights-and-concessions'],'special mining right tax'),
'p0385_1':([F,'agriculture'],['land-tenure'],'post-station land leases'),
'p0387_1':([F],['taxation','public-budgets'],'tax receipts by tax'),
'p0388_1':([F],['taxation','customs-revenue'],'tax receipts by province/customs'),
'p0388_2':([F],['public-budgets'],'post-station land revenue'),
'p0388_3':([F],['taxation'],'revenue stamp receipts'),
'p0389_1':([F],['public-budgets'],'non-tax receipts'),
}
out=[]
for r in d:
    t,g,w=m[r['key'].split(':')[1]]
    out.append(dict(key=r['key'],topics=t,tags=g,flags=[],why=w))
json.dump(out,open('results/b12.json','w'),ensure_ascii=False,indent=1)
v=json.load(open('../../vocabulary.json'));ids={x['id'] for x in v['tags']}|{x['id'] for x in v['topics']}
print(len(out),sum(1 for o in out if o['tags']),[i for o in out for i in o['topics']+o['tags'] if i not in ids])
