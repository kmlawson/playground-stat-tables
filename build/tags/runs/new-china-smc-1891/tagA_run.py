import json,re,sys
V=json.load(open('../../vocabulary.json'))
TOP={t['id'] for t in V['topics']}
TAG={l.split('|')[1].strip().strip('`').rstrip('*').strip('` ') for l in open('../../VOCABULARY.md') if l.startswith('| `')}-TOP
def fin(t,c):
    s=t.lower()
    R=[('deferred pay',['crime-and-justice'],['insurance-and-pensions']),
     ('police',['crime-and-justice'],['police']),('poor',['welfare'],['poor-relief']),
     ('hospital|medical',['health'],['medical-services']),('nuisance|market',['health'],[]),
     ('water supply',['utilities'],['water-and-sewerage']),('lighting',['utilities'],[]),
     ('telephone',['communications'],['telephone']),('post office',['communications'],['postal-services']),
     ('bridges|roads|engineer',['transportation'],['roads-and-bridges']),
     ('drainage|creeks|latrine',['utilities'],['water-and-sewerage']),
     ('buildings|landing|fire-wells|bundings',['utilities'],[]),
     ('garden|stud',['culture'],['recreation-and-amusements']),
     ('fire department',['disasters'],['firefighting']),('volunteers',['military'],['militias-and-volunteer-forces']),
     ('band',['culture'],['arts-and-music']),('library',['culture'],['libraries']),('museum',['culture'],['museums-and-heritage']),
     ('education',['education'],['education-finance']),('interest|sinking|loan',['finance'],['public-debt']),
     ('land and buildings',['finance'],['public-property']),('secretariat|general charges',['government'],[]),
     ('land tax|license|permit|rate|dues',['finance'],['taxation'])]
    for p,tp,tg in R:
        if re.search(p,s):
            top=['finance']+[x for x in tp if x!='finance']
            tags=(['public-budgets']+tg) if 'taxation' not in tg and 'public-debt' not in tg else tg+['public-budgets']
            if 'taxation' in tg: tags=['public-budgets','taxation']
            return top,tags[:3]
    return ['finance'],['public-budgets']
def rule(t,c):
    s=(t+' '+c).lower()
    if re.search('financial statement|municipal budget|budget 1892|comparative statement|summary of expenditure|general statement of receipts',s) and 'overseer' not in c.lower():
        a,b=fin(t,c)
        return a,b,[]
    if 'working accounts' in c.lower():
        if 'savings bank' in s: return ['finance'],['savings-and-loans'],[]
        if 'bank' in s: return ['finance'],['banking'],[]
        if 'liquor' in s: return ['finance'],['alcohol'],[]
        return ['finance'],[],[]
    if 'balance sheet' in c.lower(): return ['finance'],['public-budgets'],[]
    if 'land, buildings' in c.lower(): return ['finance'],['public-property'],[]
    R=[
    ('equipment|ammunition',['military'],['arms-and-arsenals']),
    ('officers of the corps',['military'],['militias-and-volunteer-forces'],['text-tables']),
    ('watch — volunteer',['military'],['militias-and-volunteer-forces']),
    ('opium-shops',['narcotics'],['opium-licensing']),
    ('boats licensed',['finance','transportation'],['taxation']),
    ('liquor-sellers',['finance'],['taxation','alcohol']),
    ('present strength',['crime-and-justice'],['police']),
    ('weekly return of prisoners',['crime-and-justice'],['prisons']),
    ('prisoners|arrests|arrested|apprehended|warrants|larceny',['crime-and-justice'],['offences-and-convictions']),
    ('bubbling well',['crime-and-justice','finance'],['police']),
    ('persons visiting',['utilities','health'],[]),
    ('market|hawkers',['trade','finance'],['markets-and-exchanges']),
    ('sewer|drain|water|ventilating',['utilities'],['water-and-sewerage']),
    ('yu hang|road|pavement|metalled|curbed|chip-paved|hanbury',['transportation'],['roads-and-bridges']),
    ('garbage',['utilities','health'],[]),
    ('latrine',['utilities','finance'],[]),
    ('slaughtered',['health','agriculture'],['livestock']),
    ('slaughter-house',['utilities','finance'],[]),
    ('age distribution',['population','health'],['births-and-deaths','age-and-sex']),
    ('death-rate',['population','health'],['births-and-deaths']),
    ('cholera cases',['health'],['epidemics','diseases']),
    ('cholera',['health'],['epidemics','diseases']),
    ('small-pox',['health'],['diseases','epidemics']),
    ('infants and children',['population','health'],['infant-mortality','births-and-deaths']),
    ('death returns|deaths registered',['population','health'],['births-and-deaths','diseases']),
    ('debentures',['finance'],['public-debt']),
    ('correspondence|covers',['communications'],['postal-services']),
    ('general municipal rate',['finance'],['taxation','real-estate']),
    ('foreign houses',['finance'],['taxation','real-estate']),
    ('overseer',['finance'],['public-budgets']),
    ('labour',['labour'],['employment-and-unemployment']),
    ('name-plates',['utilities'],[]),
    ('building operations',['utilities'],['construction','housing']),
    ('burials',['population','health'],['births-and-deaths']),
    ('parks and open',['finance','culture'],['recreation-and-amusements']),
    ('eurasian',['education','finance'],['education-finance']),
    ('receipts and expenditure of the band|band — receipts|band — estimate',['culture','finance'],['arts-and-music','public-budgets']),
    ('band|music|repertoire',['culture'],['arts-and-music']),
    ('board of the fire|officers of the fire|members of the fire',['government','disasters'],['firefighting','government-offices'],['text-tables']),
    ('fires',['disasters'],['fires','firefighting']),
    ('fire',['disasters','finance'],['firefighting','public-budgets']),
    ]
    for x in R:
        if re.search(x[0],s): return x[1],x[2],(x[3] if len(x)>3 else [])
    return None
for b in range(1,9):
    d=json.load(open(f'batches/b0{b}.json')); out=[]
    for r in d:
        t,c=r['title'] or '',r['chapter'] or ''
        pr=r.get('prior')
        if pr and set(pr['topics'])<=TOP and set(pr['tags'])<=TAG:
            out.append(dict(key=r['key'],topics=pr['topics'][:2],tags=pr['tags'][:3],flags=pr.get('flags',[]),why='prior checked against title/columns'));continue
        x=rule(t,c)
        if not x: print('UNMATCHED',r['key'],t);x=([],[],[])
        assert set(x[0])<=TOP and set(x[1])<=TAG,(r['key'],x)
        out.append(dict(key=r['key'],topics=x[0],tags=x[1],flags=x[2] if len(x)>2 else [],why=(t[:60])))
    json.dump(out,open(f'results/b0{b}.json','w'),ensure_ascii=False,indent=1)
    print(b,len(d),len(out),sum(1 for o in out if o['tags']))
