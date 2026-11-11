import json,re
def cls(key,t):
    T=t
    def has(*w): return any(x in T for x in w)
    if has('Police Force — Stock','Police Force — Pay','Police Force — Chinese','Police Force — [Other'):
        return ['crime-and-justice','finance'],['police','public-budgets'],'police pay/expenditure'
    if 'Police Force' in T and 'Buildings' not in T:
        return ['crime-and-justice','finance'],['police','public-budgets'],'police budget'
    if has('Hospital','Nursing','Ambulance','Plague','Mosquito','Health Office','Laboratory','Sanatorium'):
        if has('Hospital','Nursing','Ambulance','Sanatorium'): return ['health','finance'],['medical-services','public-budgets'],'hospital budget'
        return ['health','finance'],['public-health','public-budgets'],'public health budget'
    if has('Cemeter','Swimming'): return ['health','finance'],['public-budgets'],'health dept facilities'
    if 'Health Department' in T: return ['health','finance'],['public-health','public-budgets'],'health dept budget'
    if has('Educational Department','School'): 
        return ['education','finance'],['education-finance','schools-and-pupils'] if 'Stock' not in T else ['education-finance'] if 'Grants' not in T else ['education-finance'],'school budget'
    if has('Library'): return ['culture','finance'],['public-budgets'],'library budget'
    if has('Orchestra'): return ['culture','finance'],['arts-and-music','public-budgets'],'orchestra budget'
    if 'Drainage' in T or 'Sewer' in T: return ['utilities','finance'],['water-and-sewerage','public-budgets'],'drainage budget'
    if 'Refuse' in T: return ['utilities','finance'],['public-budgets'],'refuse disposal'
    if 'Lighting' in T: return ['utilities','finance'],['electricity','public-budgets'],'lighting'
    if has('Roads'): return ['utilities','finance'],['roads-and-bridges','public-budgets'],'roads'
    if has('Creeks','Bridges','Bundings','Landing'): return ['utilities','finance'],['river-conservancy','public-budgets'],'creeks/bridges works'
    if has('Parks'): return ['utilities','finance'],['public-budgets'],'parks'
    if 'Gaol' in T: return ['crime-and-justice','finance'],['prisons','public-budgets'],'gaol buildings'
    if has('Buildings'): return ['utilities','finance'],['construction','public-budgets'],'building works'
    if has('Interest','Debentures'): return ['finance'],['public-debt','public-budgets'],'debt service'
    if has('Income'): return ['finance'],['public-budgets'],'income'
    if has('Deficit'): return ['finance'],['public-budgets'],'deficit'
    if T=='Land': return ['finance'],['public-property','public-budgets'],'land purchase'
    if has('Summary'): return ['finance'],['public-budgets'],'budget summary'
    if has('Stock and Stores','Stores'): return ['finance'],['public-budgets'],'stores'
    if has('Finance Department','Secretariat','Commissioner General','General Charges','Compradore'): return ['government','finance'],['government-offices','public-budgets'],'admin budget'
    if has('Public Works'): return ['utilities','finance'],['public-budgets'],'PWD budget'
    return ['finance'],['public-budgets'],'budget'
for b in ['b15','b16','b17']:
    d=json.load(open(f'batches/{b}.json'));out=[]
    for r in d:
        t=r['title']+' '+(r['parts'][0].get('label') or '')
        tp,tg,w=cls(r['key'],r['title'])
        out.append(dict(key=r['key'],topics=tp,tags=tg,flags=[],why=w))
        print(b,r['title'][-60:],tp,tg)
    json.dump(out,open(f'results/{b}.json','w'),ensure_ascii=False,indent=1)
