import json,re
def cls(i,r):
    t=r['title']; tl=t.lower(); k=r['key'].split(':')[1]
    F=['finance']; T=['public-budgets']; w=''
    def s(top=None,tags=None):
        nonlocal F,T
        if top is not None: F=top
        if tags is not None: T=tags
    if 'Rates, Taxes' in t:
        s(['finance'],['taxation'])
        if 'Wharfage' in t: s(['finance','trade'],['taxation','tariffs'])
        elif 'Slaughter' in t or 'Special Permit' in t or 'Export Fees' in t or 'Water Supply' in t: s(['finance','health'],['taxation'])
        elif 'Market Fees' in t: s(['finance','trade'],['taxation','markets-and-exchanges'])
        elif 'Permit Fees' in t: s(['finance','utilities'],['taxation','construction'])
        elif 'Cargo Boat' in t: s(['finance','transportation'],['taxation','shipping'])
        elif 'Livery' in t: s(['finance','transportation'],['taxation','road-transport'])
        elif 'Ammunition' in t: s(['finance','crime-and-justice'],['taxation'])
        elif 'Eating' in t: s(['finance','trade'],['taxation'])
        elif 'Licence' in t: s(['finance','trade'],['taxation'])
        w='fees and dues schedule'
    elif 'Convict Labour' in t:
        s(['finance','crime-and-justice'],['prison-labour','public-budgets'])
    elif 'Pingchiao Quarry' in t: s(['finance','mining'],['public-budgets'])
    elif 'Concreteware' in t: s(['finance','manufacturing'],['cement-and-bricks','public-budgets'])
    elif 'Tungchow Road Workshop' in t: s(['finance','manufacturing'],['public-budgets'])
    elif 'Industrial Undertakings' in t: s(['finance','manufacturing'],['public-budgets'])
    elif 'Police Recreation' in t: s(['finance','crime-and-justice'],['police'])
    elif t=='Balance Sheet — Liabilities': s(['finance'],['public-debt'])
    elif t=='Balance Sheet — Assets': s(['finance'],['public-property'])
    elif t in('Land','Buildings','Stock and Stores'): s(['finance'],['public-property'])
    elif 'Extraordinary Expenditure' in t or 'Extraordinary Income' in t:
        if 'Loan' in t and 'Income' in t: s(['finance'],['public-budgets','foreign-loans'][:1])
        if 'Bridges' in t: s(['finance','transportation'],['public-budgets','roads-and-bridges'])
        elif 'Drainage' in t: s(['finance','utilities'],['public-budgets','water-and-sewerage'])
        elif 'Landing Stages' in t: s(['finance','transportation'],['public-budgets','ports'])
        elif 'Roads' in t: s(['finance','transportation'],['public-budgets','roads-and-bridges'])
        elif 'Electricity' in t: s(['finance','utilities'],['public-budgets','electricity'])
        elif 'Buildings — Fire' in t: s(['finance','disasters'],['public-budgets','firefighting'])
        elif 'Buildings — Police' in t: s(['finance','crime-and-justice'],['public-budgets','police'])
        elif 'Buildings — Health' in t: s(['finance','health'],['public-budgets','medical-services'])
        elif 'Land' in t: s(['finance'],['public-budgets','public-property'])
        elif 'Buildings' in t: s(['finance'],['public-budgets','public-property'])
    elif 'Ordinary Income' in t:
        if 'Land Tax' in t: s(['finance'],['land-tax','taxation'])
        elif 'General Municipal Rate' in t: s(['finance'],['taxation','public-budgets'])
        elif 'Wharfage' in t: s(['finance','trade'],['customs-revenue','public-budgets'])
        elif 'Licence' in t: s(['finance'],['taxation','public-budgets'])
        elif 'Rent of Municipal' in t: s(['finance'],['public-property','public-budgets'])
        elif 'Public and Municipal Undertakings' in t: s(['finance','utilities'],['public-budgets','securities-and-investment'])
    elif 'Volunteer Corps' in t: s(['finance','military'],['public-budgets','militias-and-volunteer-forces'])
    elif 'Fire Brigade' in t: s(['finance','disasters'],['public-budgets','firefighting'])
    elif 'Police' in t:
        s(['finance','crime-and-justice'],['public-budgets','police'])
        if 'Prisoners' in t: s(None,['public-budgets','prisons'])
    elif 'Health' in t or 'Nursing Staff' in t:
        s(['finance','health'],['public-budgets','medical-services'])
        if 'Plague' in t: s(None,['public-budgets','epidemics'])
        elif 'Mosquito' in t: s(None,['public-budgets','malaria'])
        elif 'Cemeter' in t: s(None,['public-budgets','public-health'])
        elif 'Swimming' in t: s(None,['public-budgets','recreation-and-amusements'])
        elif 'Less, and Total' in t: s(None,['public-budgets'])
    elif 'Public Works' in t:
        s(['finance','utilities'],['public-budgets'])
        if 'Lighting' in t: s(['finance','utilities'],['public-budgets','electricity'])
        elif 'Roads' in t: s(['finance','transportation'],['public-budgets','roads-and-bridges'])
        elif 'Drainage' in t: s(None,['public-budgets','water-and-sewerage'])
        elif 'Creeks' in t: s(None,['public-budgets','river-conservancy'])
        elif 'Buildings' in t: s(None,['public-budgets','construction'])
        elif 'Parks' in t: s(['finance','culture'],['public-budgets','recreation-and-amusements'])
    elif 'Band' in t: s(['finance','culture'],['public-budgets','arts-and-music'])
    elif 'Library' in t: s(['finance','education'],['public-budgets','libraries'])
    elif 'Educational' in t:
        s(['education','finance'],['education-finance','schools-and-pupils'])
        if 'Grants' in t: s(None,['education-finance'])
    elif 'Interest' in t: s(['finance'],['public-debt','public-budgets'])
    elif 'Redemption' in t: s(['finance'],['public-debt'])
    elif 'Grants in Aid' in t: s(['finance','welfare'],['public-budgets','charitable-institutions'])
    elif 'Summary' in t or 'Comparative' in t or 'Deficit' in t or 'Financial Statement' in t: pass
    return F,T
for b in ['b11','b12','b13','b14']:
    d=json.load(open('batches/%s.json'%b)); out=[]
    for i,r in enumerate(d):
        F,T=cls(i,r)
        out.append({'key':r['key'],'topics':F[:2],'tags':T[:3],'flags':[],'why':'municipal accounts: '+r['title'][-60:]})
    json.dump(out,open('results/%s.json'%b,'w'),ensure_ascii=False,indent=1)
    assert [o['key'] for o in out]==[r['key'] for r in d]
    print(b,len(out),sum(1 for o in out if o['tags']))
