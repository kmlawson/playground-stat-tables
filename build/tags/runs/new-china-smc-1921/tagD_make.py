import json
V=json.load(open('../../vocabulary.json'))
TOP={t['id'] for t in V['topics']}; TAG={t['id'] for t in V['tags']}
def R(t,g,w): return (t,g,w)
def classify(b,i,r):
    T=r['title']; k=r['key'].split(':')[1]
    if b=='b10':
        m={0:(['utilities','finance'],['electricity','public-budgets'],'electricity dept appropriation'),
        1:(['utilities','finance'],['electricity'],'electricity depreciation'),
        2:(['utilities','finance'],['electricity'],'electricity sinking fund'),
        3:(['utilities','finance'],['electricity'],'electricity reserve'),
        4:(['utilities','finance'],['electricity','public-debt'],'electricity balance sheet liabilities, loans'),
        5:(['finance'],['public-debt','interest-rates'],'loan principal and interest rates'),
        6:(['utilities','finance'],['electricity'],'electricity balance sheet assets'),
        7:(['utilities','finance'],['electricity'],'electricity capital outlay'),
        8:(['finance'],['public-budgets'],'ordinary/extraordinary budget'),
        9:(['finance'],['public-budgets'],'budget over/under spend by dept'),
        10:(['finance','crime-and-justice'],['police','wages'],'police pay by branch'),
        11:(['finance'],['public-budgets'],'general charges overspend'),
        12:(['finance'],['public-budgets'],'unspent extraordinary budget items'),
        13:(['finance'],['public-budgets'],'unbudgeted expenditure'),
        14:(['finance'],['public-budgets','prison-labour'],'industrial undertakings contributions'),
        15:(['finance'],['public-debt'],'loan statistics'),
        16:(['finance'],['public-debt','banking'],'debentures to bank depositors'),
        17:(['finance'],['public-budgets'],'ordinary income/expenditure compared'),
        18:(['finance'],['public-budgets','taxation'],'income vs estimates'),
        19:(['finance'],['taxation','land-tax'],'land tax by district'),
        20:(['finance'],['taxation','real-estate'],'municipal rate, houses/assessment'),
        21:(['finance'],['taxation','real-estate'],'special rate, houses/assessment'),
        22:(['finance','trade'],['taxation','ports'],'wharfage dues by quarter'),
        23:(['finance'],['taxation'],'licence fees excess/deficiency'),
        24:(['finance','transportation'],['road-transport','taxation'],'vehicle licences by year'),
        25:(['transportation'],['road-transport'],'motor vehicles register'),
        26:(['finance','trade'],['markets-and-exchanges'],'market fees'),
        27:(['finance'],[],'list of appended statements'),
        28:(['finance'],['public-budgets','taxation'],'ordinary revenue 1911-21'),
        29:(['finance'],['taxation','real-estate'],'Chinese rate summary'),
        30:(['finance'],['taxation','real-estate'],'Chinese houses and assessments'),
        31:(['finance'],['taxation'],'licence fees comparative'),
        32:(['finance'],['taxation'],'licence fee revenue ten years')}
        if i in m: return m[i]
        if i==33: return (['finance'],['land-tax','public-budgets'],'land tax est vs actual')
        if i in(34,35): return (['finance'],['taxation','public-budgets'],'rate income est vs actual')
        if i==36: return (['finance'],['taxation','advertising'],'advertisement rate')
        if i==37: return (['finance','trade'],['taxation','ports'],'wharfage dues')
        if i==38: return (['finance'],['taxation','public-budgets'],'licence fee income')
        return (['finance'],['public-property','public-budgets'],'market rents income')
    # statement tables
    base=['public-budgets']
    L=T.lower()
    def has(*a): return any(x.lower() in L for x in a)
    if k=='p0526_3': return (['finance'],['public-property','public-budgets'],'rent of municipal properties')
    if k=='p0526_4': return (['finance','utilities'],['public-budgets','electricity'],'revenue from public undertakings')
    if k=='p0526_5': return (['finance'],['public-budgets'],'miscellaneous income')
    if k=='p0526_6': return (['finance'],['public-budgets'],'ordinary income totals')
    if 'volunteer' in L: return (['finance','military'],['public-budgets','militias-and-volunteer-forces'],'volunteer corps expenditure')
    if 'fire brigade' in L: return (['finance'],['public-budgets','firefighting'],'fire brigade expenditure')
    if 'police hospital' in L or 'isolation' in L or 'sanatorium' in L or 'nursing' in L or 'ambulance' in L or 'victoria' in L:
        return (['finance','health'],['public-budgets','medical-services'],'hospital expenditure')
    if 'police' in L:
        t=['finance','crime-and-justice']
        if 'prisoners' in L: return (t,['public-budgets','police','prisons'],'police prisoner expenses')
        if 'mixed court' in L: return (t,['public-budgets','police','courts'],'police mixed court')
        return (t,['public-budgets','police'],'police expenditure')
    if 'health department' in L:
        tg=['public-budgets','public-health']
        if 'plague' in L or 'mosquito' in L or 'venereal' in L: tg=['public-budgets','epidemics']
        if 'cesspool' in L: tg=['public-budgets','water-and-sewerage']
        if 'cemeter' in L: tg=['public-budgets','public-health']
        if 'swimming' in L: tg=['public-budgets','recreation-and-amusements']
        return (['finance','health'],tg,'health dept expenditure')
    if 'educational' in L:
        if 'grants' in L: return (['finance','education'],['education-finance','schools-and-pupils'],'education grants in aid')
        return (['finance','education'],['education-finance','schools-and-pupils'],'school expenditure')
    if 'public works' in L:
        tg=['public-budgets']
        if 'creeks' in L: tg=['public-budgets','river-conservancy']
        elif 'drainage' in L: tg=['public-budgets','water-and-sewerage']
        elif 'roads' in L: tg=['public-budgets','roads-and-bridges']
        elif 'lighting' in L: tg=['public-budgets','electricity']
        elif 'parks' in L: tg=['public-budgets','recreation-and-amusements']
        elif 'buildings' in L: tg=['public-budgets','construction']
        return (['finance'],tg,'public works expenditure')
    if 'public band' in L: return (['finance','culture'],['public-budgets','arts-and-music'],'public band expenditure')
    if 'public library' in L: return (['finance','culture'],['public-budgets','libraries'],'library expenditure')
    return (['finance'],['public-budgets'],'finance department expenditure')
out={}
for b in('b10','b11','b12'):
    d=json.load(open(f'batches/{b}.json')); res=[]
    for i,r in enumerate(d):
        t,g,w=classify(b,i,r)
        assert all(x in TOP for x in t) and all(x in TAG for x in g),(b,i,t,g)
        res.append({'key':r['key'],'topics':t,'tags':g,'flags':[],'why':w})
    json.dump(res,open(f'results/{b}.json','w'),ensure_ascii=False,indent=1)
    assert [x['key'] for x in res]==[r['key'] for r in d]
    print(b,len(res),sum(1 for x in res if x['tags']))
