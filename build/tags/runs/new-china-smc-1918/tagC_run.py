import json,re
PB='public-budgets'
# (regex on lowercased title+chapter, topics, tags); first match wins
R=[
(r'^summary|— summary','finance',['finance'],[PB]),
(r'balance sheet — liabilities',None,['finance'],['public-debt',PB]),
(r'balance sheet — assets',None,['finance'],['public-property']),
(r'comparative statements',None,['finance'],[PB]),
(r'convict labour',None,['finance','crime-and-justice'],['prison-labour',PB]),
(r'quarry',None,['finance','mining'],[PB]),
(r'concreteware',None,['finance','manufacturing'],['cement-and-bricks',PB]),
(r'workshop',None,['finance','manufacturing'],[PB]),
(r'industrial undertakings',None,['finance'],[PB]),
(r'^(land|buildings|stock and stores)$',None,['finance'],['public-property']),
(r'wharfage dues',None,['finance','trade'],['taxation']),
(r'slaughterhouse|special permit|export fees|water supply|market fees',None,['finance','health'],['taxation']),
(r'rates, taxes, dues and fees — (rates|licence|permit)',None,['finance'],['taxation']),
(r'ordinary income — land tax',None,['finance'],['land-tax','taxation']),
(r'ordinary income — (general municipal|special advert|licence|wharfage)',None,['finance'],['taxation']),
(r'ordinary income — rent|ordinary income — revenue from public',None,['finance'],['public-property']),
(r'interest, brokerage',None,['finance'],['public-debt',PB]),
(r'redemption of debentures',None,['finance'],['public-debt',PB]),
(r'extraordinary income',None,['finance'],[PB,'public-debt']),
(r'extraordinary expenditure — (\[?deficit)',None,['finance'],[PB]),
(r'extraordinary expenditure — bridges|extraordinary expenditure — roads',None,['finance','transportation'],['roads-and-bridges',PB]),
(r'extraordinary expenditure — bundings',None,['finance','utilities'],['river-conservancy',PB]),
(r'extraordinary expenditure — drainage',None,['finance','utilities'],['water-and-sewerage',PB]),
(r'extraordinary expenditure — land',None,['finance'],['public-property',PB]),
(r'extraordinary expenditure — buildings',None,['finance','utilities'],['construction',PB]),
(r'loan to electricity',None,['finance','utilities'],['electricity',PB]),
(r'extraordinary expenditure',None,['finance'],[PB]),
(r'public band',None,['finance','culture'],['arts-and-music',PB]),
(r'public library',None,['finance','education'],['libraries',PB]),
(r'educational department.*(grants in aid)|grants in aid.*education',None,['finance','education'],['education-finance','schools-and-pupils']),
(r'educational department.*stock and stores',None,['finance','education'],['education-finance']),
(r'educational department|ellis kadoorie|public school|nieh chih|polytechnic',None,['finance','education'],['education-finance','schools-and-pupils']),
(r'health department — hospitals|ambulance|details of pay and sundry',None,['finance','health'],['medical-services',PB]),
(r'plague prevention',None,['finance','health'],['epidemics',PB]),
(r'mosquito',None,['finance','health'],['malaria','public-health']),
(r'cemeteries|swimming bath',None,['finance','health'],['public-health',PB]),
(r'health department',None,['finance','health'],['public-health',PB]),
(r'volunteer corps',None,['finance','military'],['militias-and-volunteer-forces',PB]),
(r'fire brigade',None,['finance','disasters'],['firefighting',PB]),
(r'police force',None,['finance','crime-and-justice'],['police',PB]),
(r'public works department — buildings — (police|health|educational|public)|public works department — buildings',None,['finance','utilities'],['construction',PB]),
(r'creeks and river',None,['finance','utilities'],['river-conservancy',PB]),
(r'public works department — drainage',None,['finance','utilities'],['water-and-sewerage',PB]),
(r'public works department — roads',None,['finance','transportation'],['roads-and-bridges',PB]),
(r'lighting',None,['finance','utilities'],['electricity','gas']),
(r'public works department',None,['finance','government'],[PB]),
(r'rent of municipal prop',None,['finance'],['public-property',PB]),
(r'treasurer|compradore|secretariat|secretary|finance department',None,['finance','government'],['government-offices',PB]),
(r'general charges',None,['finance'],[PB]),
(r'financial statement|municipal budget',None,['finance'],[PB]),
]
import sys
for b in sys.argv[1:]:
    d=json.load(open(f'batches/{b}.json')); out=[]
    for r in d:
        t=(r['title']+' — '+(r['chapter'] or '')).lower()
        t0=r['title'].lower()
        for pat,_,tp,tg in R:
            if re.search(pat,t0):
                break
        else: raise SystemExit('nomatch '+r['title'])
        tp=[x for x in tp]
        out.append({'key':r['key'],'topics':tp[:2],'tags':tg[:3],'flags':[],'why':'title/rows: '+r['title'][-60:]})
    assert [o['key'] for o in out]==[r['key'] for r in d]
    json.dump(out,open(f'results/{b}.json','w'),ensure_ascii=False,indent=1)
    print(b,len(out),sum(1 for o in out if o['tags']))
