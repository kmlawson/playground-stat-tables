import json
V=json.load(open('../../vocabulary.json'))
T={t['id'] for t in V['topics']};G={t['id'] for t in V['tags']}
def cls(k,title):
    t=title; n=k.split(':')[1]
    tp=['finance'];tg=['public-budgets'];w='municipal financial statement'
    if 'Educational' in t and 'Rent' not in t and 'Buildings' not in t and 'Summary' not in t or ('Summary' in t and 'Educational' in t):
        tp=['education','finance'];tg=['education-finance','public-budgets'];w='school expenditure'
    if 'Grants in Aid' in t and 'Educational' in t: tg=['education-finance','public-budgets']
    if 'Health Department' in t and 'Summary' in t: tp=['finance','health'];tg=['public-budgets','medical-services']
    if 'Public Works' in t and 'Summary' in t: tp=['finance','utilities'];tg=['public-budgets']
    if 'Interest, Brokerage' in t or 'Redemption of Debentures' in t or 'Loans and Totals' in t or 'Liabilities — To' in t or 'Loans Outstanding' in t:
        tg=['public-debt','public-budgets'] if 'Interest' in t or 'Redemption' in t or 'Loans and' in t else ['public-debt']; w='loans and debt'
    if 'Extraordinary Income' in t: tg=['public-debt','public-budgets']
    if 'Bridges' in t or 'Landing' in t or 'Bundings' in t or 'Drainage' in t or 'Roads' in t and 'Extraordinary' in t:
        tp=['finance','utilities']; w='capital works'
        if 'Bridges' in t: tg=['public-budgets','roads-and-bridges']
        elif 'Landing' in t: tg=['public-budgets','ports']
        elif 'Bundings' in t: tg=['public-budgets','flood-control']
        elif 'Drainage' in t: tg=['public-budgets','water-and-sewerage']
        else: tg=['public-budgets','roads-and-bridges']
    if 'Sinking Fund' in t: tg=['public-debt','securities-and-investment']
    if 'Trust Funds' in t and 'Liabilities' in t: tg=['insurance-and-pensions','savings-and-loans']
    if 'Trust Funds Investments' in t or 'Sinking Funds Investments' in t: tg=['securities-and-investment']
    if 'Assets' in t or 'Balance Sheet' in t: 
        if tg==['public-budgets']: tg=['public-property']
    if 'Overdrafts' in t: tg=['banking']
    if 'Comparative Statements' in t: tg=['public-budgets']
    if t in('Land','Buildings','Stock and Stores'): tg=['public-property']
    if 'Working Account' in t or ('Balance Sheet' in t and 'Liabilities' not in t and 'December' not in t): 
        tp=['finance','manufacturing']; tg=['industrial-output'] if False else []
        if 'Convict' in t: tg=['prison-labour']; tp=['finance','crime-and-justice']
        if 'Quarry' in t: tg=['mineral-production']
        if 'Concrete' in t: tg=['cement-and-bricks']
    if 'Adjustment Account' in t and 'Industrial' in t: tp=['finance','manufacturing']; tg=[]
    if 'Budget of Municipal' in t: tg=['public-budgets','public-debt']
    if 'Wharfage' in t: tp=['finance','trade'];tg=['taxation','customs-revenue']
    elif 'Licence Fees' in t: tp=['finance','government'];tg=['taxation']
    elif 'Slaughter' in t or 'Special Permit' in t or 'Export Fees' in t: tp=['finance','agriculture'];tg=['taxation','livestock'] if 'Export' in t else ['taxation']
    elif 'Water Supply' in t: tp=['finance','utilities'];tg=['taxation','water-and-sewerage']
    elif 'Market Fees' in t: tp=['finance','trade'];tg=['taxation','markets-and-exchanges']
    elif 'Permit Fees' in t or 'Water Closet' in t: tp=['finance','utilities'];tg=['taxation','construction'] if 'Permit' in t else ['taxation','water-and-sewerage']
    elif 'Land Tax' in t: tp=['finance'];tg=['land-tax','taxation']
    return tp,tg
for b in ['b13','b14']:
    d=json.load(open(f'batches/{b}.json'));out=[]
    for r in d:
        tp,tg=cls(r['key'],r['title'])
        assert all(x in T for x in tp) and all(x in G for x in tg),(r['key'],tp,tg)
        out.append({'key':r['key'],'topics':tp[:2],'tags':tg[:3],'flags':[],'why':r['title'][-60:]})
    json.dump(out,open(f'results/{b}.json','w'),ensure_ascii=False,indent=1)
    print(b,len(out),sum(1 for o in out if o['tags']))
