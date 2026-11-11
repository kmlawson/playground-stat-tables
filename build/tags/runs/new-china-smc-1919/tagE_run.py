import json
PB='public-budgets'
def rule(k,t):
    n=k.split(':')[1]
    p,s=n[1:5],int(n.split('_')[1])
    P=int(p)
    if P==446: return ['finance'],[PB],'comparative expenditure statement'
    if P==447: 
        if s<=2: return ['finance','crime-and-justice'],['prison-labour'],'convict labour accounts'
        return ['finance','manufacturing'],[],'workshop accounts'
    if P==448: return ['finance','mining'],[],'quarry accounts'
    if P==449: return ['finance','manufacturing'],['cement-and-bricks'],'concreteware accounts'
    if P==450: return ['finance','manufacturing'],[],'industrial undertakings adjustment'
    if P in(451,453,455): return ['finance'],['public-property'],'municipal property account'
    if P==457: return ['finance'],[PB],'estimates 1920'
    if 459<=P<=462: return ['finance'],['taxation'],'rates, dues and fees schedule'
    if P==467:
        if s==1: return ['finance'],['land-tax',PB],'land tax income'
        if s in(2,3,4,5,6): return ['finance'],['taxation',PB],'rate income'
        return ['finance'],['taxation',PB],'dues/licence income'
    if P==468:
        if s<=2: return ['finance'],['public-property',PB],'rent of properties'
        return ['finance'],[PB],'undertakings revenue'
    if P==469: return ['finance','military'],['militias-and-volunteer-forces',PB],'volunteer corps budget'
    if P==470: return ['finance','disasters'],['firefighting',PB],'fire brigade budget'
    if 471<=P<=473:
        if P==473 and s==3: return ['finance','crime-and-justice'],['police','courts',PB],'police and mixed court total'
        return ['finance','crime-and-justice'],['police',PB],'police budget'
    if P==474:
        tg={2:'epidemics',3:'malaria'}.get(s,'public-health')
        return ['finance','health'],[tg,PB],'health office budget'
    if 475<=P<=477: return ['finance','health'],['medical-services',PB],'hospital budget'
    if P==478:
        if s==2: return ['finance','culture'],['recreation-and-amusements',PB],'swimming bath'
        return ['finance','health'],['public-health',PB],'health dept budget'
    if P==479: return ['finance','utilities'],[PB],'public works general'
    if P==480:
        tg={1:'construction',2:'river-conservancy',3:'water-and-sewerage'}[s]
        return ['finance','utilities'],[tg,PB],'public works budget'
    if P==481: return ['finance','utilities'],['roads-and-bridges',PB],'roads budget'
    if P==482: return ['finance','utilities'],['electricity',PB],'lighting budget'
    raise Exception(k)
v=json.load(open('../../vocabulary.json'));ids={x['id'] for x in v['tags']}|{x['id'] for x in v['topics']}
for b in('b12','b13'):
    d=json.load(open(f'batches/{b}.json'));o=[]
    for r in d:
        tp,tg,w=rule(r['key'],r['title'])
        assert set(tp+tg)<=ids,(tp,tg)
        o.append(dict(key=r['key'],topics=tp,tags=tg[:3],flags=[],why=w))
    json.dump(o,open(f'results/{b}.json','w'),ensure_ascii=False,indent=1)
    print(b,len(o),sum(1 for x in o if x['tags']))
