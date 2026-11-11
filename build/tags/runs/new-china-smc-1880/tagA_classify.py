import json,re,os
R='/Users/kml/shell/projects/yearbooks/japanyearbooks/stat-tables-site/build/tags'
V=json.load(open(R+'/vocabulary.json'))
TOP={t['id'] for t in V['topics']}; TAG={t['id'] for t in V['tags']}
def cls(r):
    k=r['key'].split(':')[1]; t=r['title']; tl=t.lower(); ch=r['chapter']
    # (topics,tags,flags,why)
    if 'Volunteer' in ch:
        return ['military'],['militias-and-volunteer-forces','arms-and-arsenals'],[],'volunteer corps arms/ammunition inventory'
    if 'Ammunition' in t: pass
    if k=='p0027_1': return ['finance','government'],['public-budgets'],[],'unbudgeted appropriations'
    if k in('p0028_1','p0029_1'): return ['finance'],['taxation','real-estate'],[],'house assessments by road'
    if k=='p0029_2': return ['finance'],['taxation','land-tax'],[],'land assessments by settlement'
    if 'municipal rate' in tl and 'Overseer' in ch: return ['finance'],['taxation'],[],'general municipal rate houses/rental'
    if k=='p0034_1': return ['communications'],['postal-services'],[],'local post office mails'
    if k=='p0038_1': return ['finance'],['public-budgets'],[],'surplus vs budget'
    if ch=='Census':
        return ['population'],(['nationality-and-ethnicity','population-totals'] if 'Foreign' in t and k!='p0039_2' else ['population-totals']),[],'census by sex/nationality'
    if k in('p0046_1','p0047_1'): return ['crime-and-justice'],['police','offences-and-convictions'],[],'arrests by offence/month'
    if k=='p0048_1': return ['crime-and-justice'],['offences-and-convictions','literacy-and-adult-education'],[],'prisoners by offence and literacy'
    if k=='p0049_1': return ['crime-and-justice'],['corporal-punishment','offences-and-convictions'],[],'punishments inflicted'
    if k=='p0051_1': return ['health','utilities'],['public-health','water-and-sewerage'],[],'nuisance cart-loads'
    if k=='p0063_1': return ['health','agriculture'],['food-inspection','livestock'],[],'animals slaughtered'
    if k=='p0066_1': return ['population','health'],['births-and-deaths','age-and-sex'],[],'deaths by age'
    if k=='p0066_2': return ['population','health'],['births-and-deaths'],[],'deaths and death rate'
    if k in('p0069_1','p0070_1','p0070_2'): return ['health','population'],['diseases','births-and-deaths'],[],'deaths by cause'
    if k=='p0092_1': return ['finance','culture'],['public-budgets','recreation-and-amusements'],[],'public garden expenditure'
    if k=='p0095_1': return ['population','religion'],['births-and-deaths'],[],'burials by cemetery'
    if k.startswith('p0098'): return ['utilities'],['water-and-sewerage','roads-and-bridges'],[],'drains laid by road'
    if k.startswith('p0100') or k.startswith('p0101'): return ['transportation'],['roads-and-bridges','urban-planning'],[],'road works lists'
    if k.startswith('p0105'): return ['government'],['elections-and-parties','local-government'],[],'voter qualifications'
    if k=='p0126_1': return ['finance','government'],['firefighting','public-budgets'],[],'fire department account'
    if k=='p0128_1': return ['finance','government'],['firefighting','public-budgets'],[],'fire dept estimate'
    if k=='p0128_2': return ['government'],['firefighting'],['text-tables'],'fire commission roster'
    # financial statement / budget items
    ex='expenditure' in tl; inc='revenue' in tl or 'income' in tl
    base=(['finance','government'],['public-budgets'],[],'municipal accounts')
    rules=[('land tax','taxation','land-tax'),('municipal rate','taxation'),('dues on merchandize','customs-revenue'),('license','taxation'),
     ('police','police'),('relief of poor','poor-relief'),('telegraph','telegraph'),('hospital','medical-services'),('medical','medical-services'),
     ('night-soil','public-health'),('nuisance','public-health'),('sanitary','public-health'),('lighting','gas'),('post office','postal-services'),
     ('roads','roads-and-bridges'),('bridges','roads-and-bridges'),('drainage','water-and-sewerage'),('fire','firefighting'),('museum','museums-and-heritage'),
     ('public garden','recreation-and-amusements'),('cemeter','public-property'),('volunteers','militias-and-volunteer-forces'),('interest','interest-rates'),
     ('sinking fund','public-debt'),('loan','public-debt'),('land and buildings','public-property'),('stock','public-property'),('buildings','public-property'),('permit','taxation'),('poundage','taxation'),('surveyor','government-offices'),('secretariat','government-offices')]
    if ch.startswith('Finance — Working') :
        tg=['public-budgets']
        if 'Police' in t or 'Liquor' in t: tg=['police','public-budgets'] if 'Police' in t else ['taxation','public-budgets']
        if 'Sinking' in t: tg=['public-debt','public-budgets']
        if 'Savings' in t: tg=['savings-and-loans','police']
        if 'Post' in t: tg=['postal-services','public-budgets']
        return ['finance'],tg[:3],[],'working account fund'
    if k=='p0158_1': return ['finance'],['public-property','real-estate'],[],'land/buildings account'
    if k in('p0160_1','p0162_1','p0164_1','p0185_1','p0187_1','p0170_1'): return ['finance'],['public-budgets'],[],'receipts/expenditure statement'
    tags=[]
    for kw,*tg in rules:
        if kw in tl:
            for x in tg:
                if x not in tags: tags.append(x)
            if len(tags)>=2: break
    if 'income' in tl and 'land tax' in tl: pass
    tags=['public-budgets']+[x for x in tags if x!='public-budgets']
    tags=tags[:3]
    topics=['finance','government']
    if 'police' in tl or 'fire dep' in tl: topics=['finance','government']
    return topics,tags,[],('budget' if 'Budget' in ch else 'financial statement')+' line item'
out={}
for i in range(1,7):
    b=json.load(open(f'{R}/runs/new-china-smc-1880/batches/b0{i}.json'))
    res=[]
    for r in b:
        to,tg,fl,w=cls(r)
        assert set(to)<=TOP and set(tg)<=TAG,(r['key'],to,tg)
        res.append(dict(key=r['key'],topics=to[:2],tags=tg[:3],flags=fl,why=w))
    json.dump(res,open(f'{R}/runs/new-china-smc-1880/results/b0{i}.json','w'),ensure_ascii=False,indent=1)
    print(i,len(res),sum(1 for x in res if x['tags']))
