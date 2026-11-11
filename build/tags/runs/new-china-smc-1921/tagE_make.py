import json,re
F=['finance']
def rule(k,t):
    n=k.split(':')[1]; T=t
    if 'Convict Labour' in T: return ['finance','crime-and-justice'],['prison-labour'],'convict labour accounts'
    if 'Concreteware' in T: return ['finance','manufacturing'],['cement-and-bricks'],'concreteware works account'
    if 'Pingchiao Quarry' in T: return ['finance','mining'],[],'quarry working account'
    if 'Tungchow Road Workshop' in T: return ['finance','manufacturing'],[],'workshop account'
    if 'Industrial Undertakings' in T: return ['finance','manufacturing'],[],'industrial adjustment account'
    if 'Rent of Municipal Properties' in T and 'Budget' in T: return ['finance'],['public-property'],'rent income'
    if T.startswith('Financial Statement 1921 — Ordinary Expenditure — General Charges — Rent'): return ['finance'],['public-budgets'],'rent expenditure by department'
    if 'Redemption of Debentures' in T or 'Interest, Brokerage' in T or 'Loans Outstanding' in T: return ['finance'],['public-debt'],'debt/interest'
    if 'Loan to Electricity' in T: return ['finance','utilities'],['electricity','public-budgets'],'loan to electricity dept'
    if 'Extraordinary Expenditure — Bridges' in T or 'Extraordinary Expenditure — Roads' in T: return ['finance','transportation'],['roads-and-bridges','public-budgets'],'capital works'
    if 'Bundings' in T: return ['finance','utilities'],['construction','public-budgets'],'bunding works'
    if 'Drainage' in T: return ['finance','utilities'],['water-and-sewerage','public-budgets'],'drainage works'
    if 'Landing Stages' in T: return ['finance','transportation'],['ports','public-budgets'],'landing stages'
    if 'Extraordinary Expenditure — Land' in T: return ['finance'],['public-property','public-budgets'],'land purchases'
    if 'Extraordinary Expenditure — Buildings' in T: return ['finance','utilities'],['construction','public-budgets'],'building works'
    if T.startswith('Land') or T in('Buildings','Stock and Stores'): return ['finance'],['public-property'],'municipal property values'
    if 'Wharfage Dues' in T and 'Rates, Taxes' in T: return ['finance','trade'],['taxation','ports'],'wharfage dues schedule'
    if 'Wharfage' in T: return ['finance'],['taxation','ports'],'wharfage income'
    if 'Water Supply' in T: return ['finance','utilities'],['water-and-sewerage','taxation'],'water fees'
    if 'Export Fees' in T: return ['finance','trade'],['taxation'],'export fees'
    if 'Rates, Taxes' in T: return ['finance'],['taxation'],'fees schedule'
    if 'Land Tax' in T: return ['finance'],['land-tax','taxation'],'land tax income'
    if 'Rate' in T and 'Income' in T: return ['finance'],['taxation'],'municipal rates income'
    if 'Licence Fees' in T: return ['finance'],['taxation'],'licence fees income'
    if 'Volunteer Corps' in T and 'Rent' not in T: return ['military','finance'],['militias-and-volunteer-forces'],'volunteer corps budget'
    if 'Volunteer Corps' in T: return ['finance'],['public-budgets'],'rent of volunteer premises'
    if 'Fire Brigade' in T: return ['finance','disasters'],['firefighting'],'fire brigade budget'
    if 'Expenses of Prisoners' in T: return ['crime-and-justice','finance'],['prisons'],'prisoner expenses'
    if 'Medical Aid' in T: return ['health','crime-and-justice'],['medical-services','police'],'police medical aid'
    if 'Police' in T and 'Rent' not in T: return ['crime-and-justice','finance'],['police'],'police budget'
    if 'Plague' in T: return ['health','finance'],['epidemics'],'plague prevention'
    if 'Mosquito' in T: return ['health','finance'],['malaria'],'mosquito reduction'
    if 'Cesspool' in T: return ['health','utilities'],['water-and-sewerage','public-health'],'cesspool disposal'
    if 'Hospitals' in T: return ['health','finance'],['medical-services'],'hospital budget'
    if 'Health Department' in T and 'Rent' not in T: return ['health','finance'],['public-health'],'health dept budget'
    if 'Stock and Stores' in T: return ['finance'],['public-budgets'],'stores budget'
    if 'Secretariat' in T or 'Revenue Office' in T: return ['finance','government'],['public-budgets'],'secretariat expenditure'
    if 'Comparative' in T or 'Summary' in T or 'Budget' in T or 'Balance Sheet' in T or 'Financial Statement' in T or 'Grants' in T: return ['finance'],['public-budgets'],'budget/statement'
    return ['finance'],[],'default'
for b in ('b13','b14'):
    d=json.load(open('batches/%s.json'%b)); out=[]
    for r in d:
        tp,tg,w=rule(r['key'],r['title'])
        if 'Licence Fees' in r['title'] and 'Rates, Taxes' in r['title']: tp,tg=['finance'],['taxation']
        if 'Slaughterhouse' in r['title'] or 'Market Fees' in r['title'] or 'Permit' in r['title']: tp,tg=['finance'],['taxation']
        out.append({'key':r['key'],'topics':tp,'tags':tg,'flags':[],'why':w})
    assert [o['key'] for o in out]==[r['key'] for r in d]
    json.dump(out,open('results/%s.json'%b,'w'),ensure_ascii=False,indent=1)
    print(b,len(out),sum(1 for o in out if o['tags']))
