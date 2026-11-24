import json
d='/Users/kml/shell/projects/yearbooks/japanyearbooks/stat-tables-site/build/tags/runs/new-korea-tokanfu-1913/'
b=json.load(open(d+'batches/b14.json'))
F=['finance']; FG=['finance','government']
m={
'p0406_1':(['finance','agriculture'],['public-property'],'post-station land leases'),
'p0406_2':(F,['public-property'],'post-station land fees'),
'p0406_3':(F,['taxation'],'national tax receipts'),
'p0407_1':(F,['taxation'],'domestic taxes by province'),
'p0407_2':(F,['land-tax','taxation'],'land tax receipts'),
'p0408_1':(F,['taxation'],'household tax receipts'),
'p0408_2':(F,['taxation'],'house tax receipts'),
'p0409_1':(F,['taxation'],'liquor tax receipts'),
'p0410_1':(F,['taxation'],'tobacco tax receipts'),
'p0410_2':(F,['taxation'],'mining tax receipts'),
'p0411_1':(F,['taxation'],'misc tax receipts'),
'p0412_1':(F,['public-property'],'post-station land income'),
'p0412_2':(F,['taxation'],'revenue stamps and registration taxes'),
'p0413_1':(F,['public-budgets'],'non-tax revenue'),
'p0414_1':(F,['taxation'],'tax distraint'),
'p0415_1':(['crime-and-justice','finance'],['offences-and-convictions','taxation'],'tax offenders'),
'p0415_2':(FG,['taxation'],'tax collection expenses'),
'p0416_1':(F,['banking'],'treasury-handling offices and banks'),
'p0416_2':(F,['taxation'],'direct tax burden'),
'p0417_1':(FG,['public-budgets','local-government'],'local fund revenue/expenditure'),
'p0417_2':(FG,['public-budgets','local-government'],'local fund revenue'),
'p0418_1':(FG,['public-budgets','local-government'],'local fund expenditure'),
'p0418_2':(FG,['taxation','local-government'],'local levies'),
'p0418_3':(FG,['taxation','local-government'],'local levy collection'),
'p0419_1':(FG,['taxation','local-government'],'local levy collection by province'),
'p0419_2':(FG,['taxation','local-government'],'local levy distraint'),
'p0420_1':(['finance','welfare'],['public-budgets'],'imperial bounty distribution'),
'p0420_2':(['finance','welfare'],['public-budgets'],'bounty fund revenue'),
'p0420_3':(['finance','welfare'],['public-budgets'],'bounty fund expenditure'),
'p0420_4':(FG,['public-budgets','local-government'],'township revenue budget'),
'p0421_1':(FG,['public-budgets','local-government'],'township expenditure budget'),
'p0421_2':(FG,['taxation','local-government'],'township levy rates'),
'p0421_3':(FG,['taxation','local-government'],'township levy per household'),
'p0421_4':(['government','finance'],['local-government','wages'],'township staff pay'),
'p0422_1':(FG,['public-budgets','local-government'],'urban municipality budgets'),
'p0422_2':(FG,['public-budgets','local-government'],'municipal revenue by item'),
'p0423_1':(FG,['public-budgets','local-government'],'municipal expenditure by item'),
'p0425_1':(FG,['public-budgets','overseas-communities'],'settlers associations accounts'),
'p0425_2':(['finance','education'],['public-budgets','education-finance'],'school association budgets'),
'p0425_3':(['finance','agriculture'],['public-budgets','irrigation'],'water association budgets'),
}
out=[]
for r in b:
    k=r['key'].split(':')[1]
    t,g,w=m[k]
    out.append({'key':r['key'],'topics':t,'tags':g,'flags':[],'why':w})
assert len(out)==len(b)
json.dump(out,open(d+'results/b14.json','w'),ensure_ascii=False,indent=1)
print(len(out),sum(1 for o in out if o['tags']))
