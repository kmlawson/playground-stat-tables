import json,re
V=json.load(open('../../vocabulary.json'))
TOP={t['id'] for t in V['topics']};TAG={t['id'] for t in V['tags']}
# (regex on key-title-chapter lower, topics, tags, flags) first match wins
R=[
(r'officers of the corps|changes among the officers|list of winners|^staff \(end|members of fire commission|^the board|^officers$|officers for 1887', ['military'],['militias-and-volunteer-forces'],['text-tables']),
(r'force present|strength of (and )?the corps|comparative strength|full strength', ['military'],['militias-and-volunteer-forces'],[]),
(r'arms|accoutrements|ammunition', ['military'],['arms-and-arsenals','militias-and-volunteer-forces'],[]),
(r'pawn', ['finance'],['pawnshops'],[]),
(r'police force.*strength|present strength', ['crime-and-justice'],['police'],[]),
(r'confined in municipal gaols', ['crime-and-justice'],['prisons'],[]),
(r'punishments inflicted', ['crime-and-justice'],['corporal-punishment','offences-and-convictions'],[]),
(r'prisoners|arrests|arrested', ['crime-and-justice'],['offences-and-convictions','police'],[]),
(r'warrants executed', ['crime-and-justice'],['police'],[]),
(r'bubbling well road, ?$|monthly subscriptions for policing', ['crime-and-justice','finance'],['police'],[]),
(r'garbage', ['health'],['public-health'],[]),
(r'animals slaughtered|grease-shops', ['trade'],['markets-and-exchanges'],[]),
(r'age-group|death-rates', ['population','health'],['births-and-deaths'],[]),
(r'cholera', ['health'],['epidemics','diseases'],[]),
(r'death', ['health','population'],['births-and-deaths','diseases'],[]),
(r'deferred pay|pension fund|sinking fund', ['finance'],['public-debt'] ,[]),
(r'burials', ['population'],['births-and-deaths'],[]),
(r'eurasian school', ['education'],['education-finance'],[]),
(r'brass band|orchestra|town band', ['culture'],['arts-and-music'],[]),
(r'hose', ['disasters'],['firefighting'],[]),
(r'fire', ['disasters'],['firefighting'],[]),
(r'post office|postal', ['communications'],['postal-services'],[]),
(r'general municipal rate|assessment|lots of land|houses upon which', ['finance'],['taxation'],[]),
(r'brick drains|pipe drains|drainage', ['utilities'],['water-and-sewerage'],[]),
(r'canal|dredging|creeks', ['utilities'],['river-conservancy'],[]),
(r'water', ['utilities'],['water-and-sewerage'],[]),
(r'roads|road extensions|new roads', ['transportation'],['roads-and-bridges'],[]),
]
FIN=[
(r'museum', ['finance','culture'],['museums-and-heritage','public-budgets']),
(r'library', ['finance','culture'],['libraries','public-budgets']),
(r'education', ['finance','education'],['education-finance','public-budgets']),
(r'town band', ['finance','culture'],['arts-and-music','public-budgets']),
(r'police savings bank', ['finance'],['savings-and-loans','public-budgets']),
(r'deferred pay|pension fund', ['finance','crime-and-justice'],['insurance-and-pensions','police','public-budgets']),
(r'police', ['finance','crime-and-justice'],['police','public-budgets']),
(r'liquor|livery|billiard|saloon', ['finance'],['taxation','public-budgets']),
(r'post office', ['finance','communications'],['postal-services','public-budgets']),
(r'volunteer', ['finance','military'],['militias-and-volunteer-forces','public-budgets']),
(r'fire dep', ['finance','disasters'],['firefighting','public-budgets']),
(r'water supply', ['finance','utilities'],['water-and-sewerage','public-budgets']),
(r'lighting', ['finance','utilities'],['gas','public-budgets']),
(r'telegraph', ['finance','communications'],['telegraph','public-budgets']),
(r'stud', ['finance','agriculture'],['livestock','public-budgets']),
(r'roads|bridges|landing|bundings', ['finance','transportation'],['roads-and-bridges','public-budgets']),
(r'drainage|latrine', ['finance','utilities'],['water-and-sewerage','public-budgets']),
(r'creeks', ['finance','utilities'],['river-conservancy','public-budgets']),
(r'relief of poor', ['finance','welfare'],['poor-relief','public-budgets']),
(r'sanitary|hospital|medical|nuisance', ['finance','health'],['public-health','public-budgets']),
(r'sinking fund|loan|debenture|interest', ['finance'],['public-debt','public-budgets']),
(r'land and buildings|property', ['finance'],['public-property','public-budgets']),
(r'land tax|rate|dues|licen[cs]e|permit|revenue — land and house', ['finance'],['taxation','public-budgets']),
(r'secretariat', ['finance','government'],['government-offices','public-budgets']),
(r'cemeter', ['finance'],['public-budgets']),
]
out={}
for b in range(1,8):
    d=json.load(open(f'batches/b{b:02d}.json')); res=[]
    for r in d:
        t=(r['title'] or '').lower(); ch=(r['chapter'] or '').lower(); key=r['key']
        txt=t+' '+ch
        fin = 'financ' in ch or 'budget' in ch or 'finance' in ch
        top=tags=None;fl=[]
        if fin and not re.search(r'brass band|eurasian|post office—report|^accounts|general balance|^general statement|summary of|comparing|comparative|closing|brought|running|no sub-head|carried',t) or (fin and re.search(r'(financial statement|municipal budget).*(—)',t)):
            for pat,tp,tg in FIN:
                if re.search(pat,t): top,tags=tp,tg;break
            if top is None: top,tags=['finance'],['public-budgets']
            why='municipal accounts line: '+t[:50]
        elif fin:
            top,tags=['finance'],['public-budgets']
            if re.search(r'balance sheet|property',t): tags=['public-budgets','public-property']
            if 'outstanding' in t: tags=['public-budgets']
            why='municipal accounts/summary'
        else:
            for pat,tp,tg,f in R:
                if re.search(pat,t): top,tags,fl=tp,tg,f;break
            why='by title/rows: '+t[:50]
        if top is None:
            top,tags=['government'],[]; why='unclassified; default'
        if 'sinking fund' in t and not fin: pass
        assert all(x in TOP for x in top) and all(x in TAG for x in tags),(key,top,tags)
        if re.search(r'\bfire',t) and fin and 'fire dep' not in t: pass
        res.append({'key':key,'topics':top[:2],'tags':tags[:3],'flags':fl,'why':why})
    json.dump(res,open(f'results/b{b:02d}.json','w'),ensure_ascii=False,indent=1)
    assert [x['key'] for x in res]==[x['key'] for x in d]
    out[b]=(len(res),sum(1 for x in res if x['tags']))
print(out)
