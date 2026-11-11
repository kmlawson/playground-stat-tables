import json,sys
v=json.load(open('../../vocabulary.json'))
T={t['id'] if isinstance(t,dict) else t for t in v['topics']}
G={t['id'] if isinstance(t,dict) else t for t in v['tags']}
FIN=['finance']
def cls(k,t):
    tl=t.lower(); n=k.split(':')[1]
    def R(tp,tg,why): return tp,tg,why
    if n.startswith('p0498'): return R(['finance','disasters'],['firefighting','public-budgets'],'fire brigade budget lines')
    if n.startswith('p0497'): return R(['finance','military'],['militias-and-volunteer-forces','public-budgets'],'volunteer corps budget')
    if n.startswith('p0499') or n.startswith('p050'+'0') or n.startswith('p0501'):
        if 'p0502' not in n: return R(['finance','crime-and-justice'],['police','public-budgets'] if 'mixed court' not in tl else ['courts','public-budgets'],'police budget lines')
    if 'wharfage dues tariff' in tl: return R(['trade','finance'],['tariffs'],'dues tariff by goods')
    if 'summary of estimates' in tl: return R(['finance'],['public-budgets'],'estimates summary')
    if 'licence fees' in tl or 'rates, taxes' in tl and 'fees' in tl:
        tg=[]
        if any(x in tl for x in ['motor','vehicle','livery','garage','public motor']): tg=['road-transport']
        elif any(x in tl for x in ['cargo boat','ferries']): tg=['shipping']
        elif 'ammunition' in tl: tg=['arms-and-arsenals']
        elif 'market fees' in tl: return R(['finance','trade'],['markets-and-exchanges'],'market fees')
        elif 'slaughter' in tl or 'export fees' in tl or 'special permit' in tl or 'water supply' in tl: tg=['food-inspection'] if 'slaughter' in tl else []
        elif 'permit fees' in tl: tg=['construction']
        elif 'theatres' in tl: tg=['theatre-and-cinema']
        elif 'eating house' in tl or 'general licences' in tl: tg=[]
        return R(['finance','government'],tg,'licence fee schedule')
    if 'land tax' in tl: return R(['finance'],['land-tax','taxation'],'land tax')
    if 'municipal rate' in tl or 'special rate' in tl: return R(['finance'],['taxation'],'rates income')
    if 'advertisement rate' in tl: return R(['finance'],['taxation','advertising'],'advert rate')
    if 'ordinary income — wharfage' in tl: return R(['finance','trade'],['taxation'],'wharfage dues income')
    if 'ordinary income — licence' in tl: return R(['finance'],['public-budgets'],'licence income')
    if 'rent of municipal properties' in tl and 'ordinary income' in tl: return R(['finance'],['public-property'],'rent income')
    if 'revenue from public' in tl: return R(['finance'],['securities-and-investment'],'dividends from undertakings')
    if 'rent of municipal properties' in tl: return R(['finance'],['public-property','public-budgets'],'rents paid')
    if 'redemption' in tl or 'interest, brokerage' in tl: return R(['finance'],['public-debt'],'loan interest/redemption')
    if 'extraordinary income' in tl: return R(['finance'],['public-debt','public-budgets'],'loans and surplus')
    if 'deficit' in tl: return R(['finance'],['public-budgets'],'deficit')
    if 'bridges' in tl: return R(['finance','transportation'],['roads-and-bridges'],'bridge works')
    if 'drainage' in tl and 'public works' not in tl: return R(['finance','utilities'],['water-and-sewerage'],'drainage works')
    if 'landing stages' in tl: return R(['finance','transportation'],['ports'],'landing stages')
    if 'waterworks company' in tl: return R(['finance','utilities'],['water-and-sewerage','securities-and-investment'],'waterworks')
    if 'loan to electricity' in tl: return R(['finance','utilities'],['electricity','public-debt'],'electricity loan')
    if 'extraordinary expenditure — roads' in tl: return R(['finance','transportation'],['roads-and-bridges'],'road works')
    if 'extraordinary expenditure — land' in tl: return R(['finance'],['public-property'],'land purchase')
    if 'extraordinary expenditure' in tl: return R(['finance'],['construction','public-budgets'] if 'buildings' in tl else ['public-budgets'],'extraordinary works')
    if 'balance sheet 1920 — liabilities' in tl: return R(['finance'],['public-debt'],'liabilities')
    if 'balance sheet 1920 — assets' in tl: return R(['finance'],['public-property'],'assets')
    if 'comparative' in tl or 'summary' in tl: return R(['finance'],['public-budgets'],'budget summary')
    if 'convict labour' in tl: return R(['finance','crime-and-justice'],['prison-labour'],'convict labour accounts')
    if 'quarry' in tl: return R(['finance','mining'],[],'quarry accounts')
    if 'concreteware' in tl: return R(['finance','manufacturing'],['cement-and-bricks'],'concreteware accounts')
    if 'workshop' in tl: return R(['finance','manufacturing'],[],'workshop accounts')
    if 'adjustment account' in tl: return R(['finance'],[],'industrial adjustment account')
    if tl in ('land','buildings','stock and stores'): return R(['finance','government'],['public-property'],'municipal property inventory')
    if 'public library' in tl: return R(['finance','culture'],['libraries','public-budgets'],'library budget')
    if 'educational department' in tl:
        return R(['finance','education'],['education-finance','public-budgets'] if 'grants' in tl else ['education-finance','schools-and-pupils'],'school budget')
    if 'health department' in tl or 'financial statement 1920 — ordinary expenditure — health' in tl:
        tg=['public-budgets']
        for kw,tag in [('plague','epidemics'),('mosquito','malaria'),('venereal','diseases'),('cesspool','water-and-sewerage'),('hospital','medical-services'),('nursing','medical-services'),('ambulance','medical-services'),('cemeter','public-health'),('swimming','recreation-and-amusements'),('sanatorium','medical-services')]:
            if kw in tl: tg=[tag,'public-budgets']; break
        return R(['finance','health'],tg,'health dept budget')
    if 'public works' in tl:
        tg=['public-budgets']
        for kw,tag in [('buildings','construction'),('creeks','river-conservancy'),('drainage','water-and-sewerage'),('roads','roads-and-bridges'),('lighting','electricity'),('parks','recreation-and-amusements')]:
            if kw in tl: tg=[tag,'public-budgets']; break
        return R(['finance','government'],tg,'public works budget')
    if 'public band' in tl: return R(['finance','culture'],['arts-and-music','public-budgets'],'band budget')
    if 'finance department' in tl or 'secretariat' in tl: return R(['finance','government'],['public-budgets'],'admin dept budget')
    if 'grants in aid' in tl: return R(['finance','welfare'],['charitable-institutions','public-budgets'],'grants in aid')
    if 'general charges' in tl: return R(['finance','government'],['public-budgets'],'general charges')
    return R(['finance'],['public-budgets'],'budget')
for b in sys.argv[1:]:
    d=json.load(open('batches/%s.json'%b)); out=[]
    for r in d:
        tp,tg,why=cls(r['key'],r['title'])
        assert set(tp)<=T and set(tg)<=G,(r['key'],tp,tg)
        out.append({'key':r['key'],'topics':tp[:2],'tags':tg[:3],'flags':[],'why':why})
    assert [o['key'] for o in out]==[r['key'] for r in d]
    json.dump(out,open('results/%s.json'%b,'w'),ensure_ascii=False,indent=1)
    print(b,len(out),sum(1 for o in out if o['tags']))
