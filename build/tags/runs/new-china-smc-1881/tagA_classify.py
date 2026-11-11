import json,re
V=json.load(open('../../vocabulary.json'))
TOP={t['id'] for t in V['topics']}; TAG={t['id'] for t in V['tags']}
M={ # manual by key suffix
'p0018_1':(['military'],['arms-and-arsenals','militias-and-volunteer-forces'],'volunteer arms'),
'p0020_1':(['military'],['arms-and-arsenals','militias-and-volunteer-forces'],'volunteer ammunition'),
'p0022_1':(['finance'],['public-budgets'],'deficit'),
'p0022_2':(['finance'],['public-budgets','taxation'],'budget revenue'),
'p0022_3':(['finance'],['public-budgets'],'expenditure'),
'p0023_1':(['finance'],['public-budgets'],'unbudgeted appropriations'),
'p0030_1':(['finance'],['taxation','real-estate'],'house assessments'),
'p0031_1':(['finance'],['taxation','real-estate'],'assessment reductions'),
'p0032_1':(['finance'],['land-tax','land-registration'],'land lots assessed'),
'p0036_1':(['communications'],['postal-services'],'local post'),
'p0038_1':(['utilities'],[],'public lamps'),
'p0041_1':(['crime-and-justice'],['police','offences-and-convictions'],'arrests foreigners'),
'p0042_1':(['crime-and-justice'],['police','offences-and-convictions'],'arrests by month'),
'p0043_1':(['crime-and-justice','education'],['offences-and-convictions','literacy-and-adult-education'],'prisoners literacy'),
'p0044_1':(['crime-and-justice'],['corporal-punishment','offences-and-convictions'],'punishments'),
'p0048_1':(['health'],['public-health'],'garbage'),
'p0060_1':(['health'],['food-inspection','livestock'],'slaughter'),
'p0060_2':(['health'],['food-inspection','livestock'],'slaughter'),
'p0062_1':(['population','health'],['age-and-sex','births-and-deaths'],'age at death'),
'p0063_1':(['population','health'],['births-and-deaths'],'death rate'),
'p0065_1':(['health','population'],['epidemics','births-and-deaths'],'cholera deaths'),
'p0068_1':(['health','population'],['epidemics','births-and-deaths'],'cholera deaths'),
'p0074_1':(['health','population'],['diseases','births-and-deaths'],'phthisis deaths'),
'p0077_1':(['health','agriculture'],['veterinary-health','livestock'],'cattle plague'),
'p0078_1':(['health','population'],['diseases','births-and-deaths'],'deaths by cause'),
'p0079_1':(['health','population'],['diseases','births-and-deaths'],'deaths by cause'),
'p0079_2':(['health','population'],['infant-mortality','diseases'],'child deaths'),
'p0083_1':(['finance'],['real-estate'],'land purchase memo'),
'p0099_1':(['finance','culture'],['recreation-and-amusements','public-budgets'],'public garden'),
'p0106_1':(['population'],['births-and-deaths'],'burials'),
'p0108_1':(['utilities'],['water-and-sewerage'],'drains'),
'p0108_2':(['utilities'],['water-and-sewerage'],'drains'),
'p0112_1':(['utilities'],[],'lamps by road'),
'p0113_1':(['transportation'],['roads-and-bridges'],'road surfacing'),
'p0113_2':(['transportation'],['roads-and-bridges'],'road surfacing'),
'p0113_3':(['transportation'],['roads-and-bridges'],'road surfacing'),
'p0114_1':(['transportation'],['roads-and-bridges'],'road surfacing'),
'p0114_2':(['transportation'],['roads-and-bridges'],'road widening'),
'p0115_1':(['transportation'],['roads-and-bridges'],'road improvements'),
'p0137_1':(['finance','culture'],['public-budgets','arts-and-music'],'band expenditure'),
'p0137_2':(['finance','culture'],['public-budgets','arts-and-music'],'band appropriations'),
'p0138_1':(['finance','culture'],['public-budgets','arts-and-music'],'band estimate'),
'p0141_1':(['government'],['government-offices'],'gratuities to staff'),
'p0146_1':(['finance','government'],['firefighting','public-budgets'],'fire dept account'),
'p0148_1':(['finance','government'],['firefighting','public-budgets'],'fire estimate'),
'p0148_2':(['government'],['firefighting'],'fire commission members'),
'p0198_1':(['finance'],['public-budgets'],'budget summary'),
'p0198_2':(['finance'],['taxation'],'rates recommended'),
'p0190_1':(['finance'],['public-budgets'],'general receipts expenditure'),
'p0192_1':(['finance'],['public-budgets'],'balance sheet'),
'p0194_1':(['finance'],['public-budgets'],'actual vs estimate'),
'p0188_1':(['finance'],['public-property'],'land and buildings account'),
'p0212_1':(['finance'],['public-budgets'],'expenditure summary'),
'p0213_1':(['finance'],['public-budgets'],'comparative statement'),
}
# keyword rules (first match) on lower title, for financial statements/budgets
R=[('rate',['finance'],['taxation'],'municipal rate'),] 
K=[
('police gratuity',['finance','crime-and-justice'],['police','insurance-and-pensions'],'police fund'),
('police savings',['finance','crime-and-justice'],['savings-and-loans','police'],'police savings'),
('police force',['finance','crime-and-justice'],['police','public-budgets'],'police finance'),
('land tax',['finance'],['land-tax','taxation'],'land tax'),
('general municipal rate',['finance'],['taxation','public-budgets'],'municipal rate'),
('license',['finance'],['taxation','public-budgets'],'licence fees'),
('liquor',['finance'],['public-budgets'],'liquor deposits'),
('livery',['finance'],['public-budgets'],'livery deposits'),
('telegraph',['finance','communications'],['telegraph','public-budgets'],'telegraph finance'),
('post office',['finance','communications'],['postal-services','public-budgets'],'post finance'),
('lock hospital',['finance','health'],['medical-services','public-budgets'],'lock hospital'),
('night-soil',['finance','health'],['public-health','public-budgets'],'night-soil'),
('sanitary',['finance','health'],['public-health','public-budgets'],'sanitary'),
('relief of poor',['finance','welfare'],['poor-relief','public-budgets'],'poor relief'),
('orphanage',['finance','welfare'],['child-welfare','public-budgets'],'orphanage grant'),
('cemeter',['finance'],['public-budgets'],'cemeteries'),
('bridges',['finance','transportation'],['roads-and-bridges','public-budgets'],'bridges'),
('landing stage',['finance','transportation'],['ports','public-budgets'],'landing stages'),
('drain',['finance','utilities'],['water-and-sewerage','public-budgets'],'drainage'),
('old race course',['finance'],['real-estate','public-property'],'land sale'),
('public works',['finance','transportation'],['roads-and-bridges','public-budgets'],'public works'),
('road',['finance','transportation'],['roads-and-bridges','public-budgets'],'roads'),
('buil',['finance'],['public-property','public-budgets'],'buildings'),
('garden',['finance','culture'],['recreation-and-amusements','public-budgets'],'garden'),
('museum',['finance','culture'],['museums-and-heritage','public-budgets'],'museum'),
('library',['finance','culture'],['libraries','public-budgets'],'library'),
('loan',['finance'],['public-debt'],'loan'),
('sinking fund',['finance'],['public-debt'],'sinking fund'),
('interest',['finance'],['public-debt','public-budgets'],'interest'),
('fire',['finance','government'],['firefighting','public-budgets'],'fire dept'),
('volunteer',['finance','military'],['militias-and-volunteer-forces','public-budgets'],'volunteers'),
('band',['finance','culture'],['arts-and-music','public-budgets'],'band'),
('lighting',['finance','utilities'],['public-budgets'],'lighting'),
('stock',['finance'],['public-property','public-budgets'],'stock and stores'),
('stud',['finance'],['public-budgets'],'stud'),
('secretariat',['finance','government'],['government-offices','public-budgets'],'secretariat'),
('surveyor',['finance','government'],['government-offices','public-budgets'],'surveyor office'),
('tax office',['finance','government'],['taxation','government-offices'],'tax office'),
('contribution',['finance'],['public-budgets'],'contribution'),
('poundage',['finance'],['public-budgets'],'poundage'),
]
def cls(r):
    k=r['key'].split(':')[1]
    if k in M:
        t,g,w=M[k]
    else:
        s=r['title'].lower()
        for kw,t,g,w in K:
            if kw in s: break
        else: t,g,w=['finance'],['public-budgets'],'municipal finance'
    fl=['text-tables'] if k=='p0148_2' else []
    return dict(key=r['key'],topics=t,tags=g,flags=fl,why=w)
for i in range(1,6):
    d=json.load(open('batches/b0%d.json'%i)); out=[cls(r) for r in d]
    for o in out:
        assert all(x in TOP for x in o['topics']) and all(x in TAG for x in o['tags']) and len(o['topics'])<=2 and len(o['tags'])<=3
    json.dump(out,open('results/b0%d.json'%i,'w'),ensure_ascii=False,indent=1)
    print(i,len(out),sum(1 for o in out if o['tags']))
