import json,re,os
D=os.path.dirname(os.path.abspath(__file__))
V=json.load(open(os.path.join(D,'../../vocabulary.json')))
TAGS={t['id'] for t in V['tags']}; TOP={t['id'] if isinstance(t,dict) else t for t in V['topics']} if isinstance(V['topics'],list) else set(V['topics'])
T='text-tables'
# (regex on lowercased title, topics, tags, flags, why)
R=[
 (r'attendance at the inspection|efficient list|full strength of the corps',['military'],['militias-and-volunteer-forces'],[],'volunteer corps strength'),
 (r'resignations|promotions|new commissions|officers of the corps',['military'],['militias-and-volunteer-forces'],[T],'volunteer officer roll'),
 (r'equipment|ammunition',['military'],['arms-and-arsenals','militias-and-volunteer-forces'],[],'volunteer stores'),
 (r'pawn-shops',['finance','government'],['pawnshops'],[],'pawnshop licences'),
 (r'liquor-sellers$',['finance','government'],['public-budgets'],[],'liquor licence'),
 (r'present strength of and variations',['crime-and-justice','government'],['police'],[],'police force strength'),
 (r'prisoners confined|condition of chinese prisoners',['crime-and-justice'],['prisons','offences-and-convictions'],[],'prisoners'),
 (r'prisoners apprehended|comparative table of arrests|foreigners arrested|arrested and not charged',['crime-and-justice'],['offences-and-convictions','police'],[],'arrests by offence'),
 (r'punishments inflicted',['crime-and-justice'],['corporal-punishment','offences-and-convictions'],[],'punishments'),
 (r'warrants executed',['crime-and-justice'],['police','civil-litigation'],[],'warrants and summonses'),
 (r'bubbling well road',['finance','government'],['local-government'],[],'road subscriptions'),
 (r'garbage',['health','government'],['public-health'],[],'garbage collected'),
 (r'slaughtered',['health','agriculture'],['food-inspection','livestock'],[],'animals slaughtered'),
 (r'deaths of foreigners by age',['population','health'],['births-and-deaths','age-and-sex'],[],'deaths by age'),
 (r'death-rates',['population','health'],['births-and-deaths'],[],'death rates'),
 (r'cholera cases',['health','population'],['epidemics','diseases'],[],'cholera cases'),
 (r'cholera',['health','population'],['epidemics','births-and-deaths'],[],'cholera deaths'),
 (r'infants and children',['population','health'],['infant-mortality','births-and-deaths'],[],'infant deaths'),
 (r'death returns|deaths registered',['population','health'],['births-and-deaths','diseases'],[],'deaths by cause'),
 (r'debentures',['finance'],['public-debt'],[],'municipal loan debentures'),
 (r'municipal rate',['finance'],['taxation','real-estate'],[],'rate assessment'),
 (r'houses upon which|new houses assessed|lots of land assessed',['finance'],['taxation','real-estate'],[T],'assessment list'),
 (r'value of stamps',['communications','finance'],['postal-services'],[],'stamps sold'),
 (r'post office — report',['communications'],['postal-services'],[],'post office report'),
 (r'paving contract|cost of extending|roads to be made|chip-paved|curbed|metalled|road extensions',['transportation','utilities'],['roads-and-bridges'],[],'roads'),
 (r'progress of road',['transportation'],['roads-and-bridges'],[],'roads'),
 (r'cemeteries — burials',['population','health'],['births-and-deaths'],[],'burials'),
 (r'drain',['utilities'],['water-and-sewerage'],[],'drains'),
 (r'recreation ground',['sport','finance'],['sports-organisations-and-facilities'],[],'recreation ground accounts'),
 (r'police station',['government','crime-and-justice'],['police'],[],'station accommodation'),
 (r'quantity of water',['utilities'],['water-and-sewerage'],[],'water used'),
 (r'eurasian school',['education','finance'],['education-finance','schools-and-pupils'],[],'school accounts'),
 (r'town band — services',['culture'],['arts-and-music'],[],'band services'),
 (r'town band|orchestra|receipts and expenditure for 1888|estimate for 1889',['culture','finance'],['arts-and-music','public-budgets'],[],'band accounts'),
 (r'fires, general alarms|fire record',['disasters'],['fires','firefighting'],[],'fires'),
 (r'fire department|fire brigade|receipts for the year|expenditure for the year',['disasters','finance'],['firefighting','public-budgets'],[],'fire dept accounts'),
 (r'members of the fire commission',['disasters','government'],['firefighting'],[T],'commission roll'),
 (r'police savings bank',['finance'],['savings-and-loans'],[],'savings bank'),
 (r'hongkong & shanghai bank',['finance'],['banking'],[],'bank account'),
 (r'sinking fund$',['finance'],['public-debt'],[],'sinking fund'),
 (r'land, buildings and property',['finance'],['public-property','real-estate'],[],'municipal property'),
 (r'outstanding contracts|outstanding dues',['finance'],['public-budgets'],[],'outstanding items'),
 (r'balance sheet|general statement of receipts',['finance'],['public-budgets'],[],'municipal accounts'),
]
# department rules for finance statements/budget (title lowercased)
DEP=[
 (r'police deferred|police charges|police force|carter road|police',['finance','crime-and-justice'],['public-budgets','police'],'police finance'),
 (r'volunteers',['finance','military'],['public-budgets','militias-and-volunteer-forces'],'volunteers finance'),
 (r'fire-well|fire department',['finance','disasters'],['public-budgets','firefighting'],'fire finance'),
 (r'relief of poor',['finance','welfare'],['public-budgets','poor-relief'],'poor relief finance'),
 (r'lock hospital|medical',['finance','health'],['public-budgets','medical-services'],'medical finance'),
 (r'sanitary|latrines|nuisance|market',['finance','health'],['public-budgets','public-health'],'sanitary finance'),
 (r'water supply|drainage',['finance','utilities'],['public-budgets','water-and-sewerage'],'water finance'),
 (r'lighting',['finance','utilities'],['public-budgets','electricity','gas'],'lighting finance'),
 (r'telephone',['finance','communications'],['public-budgets','telephone'],'telephone finance'),
 (r'post office',['finance','communications'],['public-budgets','postal-services'],'post office finance'),
 (r'bridges|roads|widening|landing|bundings',['finance','transportation'],['public-budgets','roads-and-bridges'],'public works finance'),
 (r'town band',['finance','culture'],['public-budgets','arts-and-music'],'band finance'),
 (r'museum',['finance','culture'],['public-budgets','museums-and-heritage'],'museum finance'),
 (r'library',['finance','culture'],['public-budgets','libraries'],'library finance'),
 (r'education',['finance','education'],['public-budgets','education-finance'],'education finance'),
 (r'interest|sinking fund|loan',['finance'],['public-budgets','public-debt'],'debt finance'),
 (r'land tax',['finance'],['public-budgets','land-tax'],'land tax income'),
 (r'municipal rate|dues on merchandize|license fees|permit fees',['finance'],['public-budgets','taxation'],'tax income'),
 (r'land and buildings|buildings|stock',['finance'],['public-budgets','public-property'],'property finance'),
 (r'secretariat|surveyor|general charges|stud|contingency',['finance','government'],['public-budgets','government-offices'],'administration finance'),
 (r'cemeteries',['finance','government'],['public-budgets'],'cemetery finance'),
]
def rec(r):
    t=r['title'].lower(); ch=(r['chapter'] or '').lower()
    for pat,tp,tg,fl,w in R:
        if re.search(pat,t): return tp,tg,fl,w
    if re.match(r'(financial statement|statement, 31|municipal budget|summary of|comparative statement|summary of expenditure|police|foreign|native|local post|hongkong)',t) or 'finance' in ch or 'budget' in ch:
        for pat,tp,tg,w in DEP:
            if re.search(pat,t): return tp,tg,[],w
        return ['finance'],['public-budgets'],[],'municipal accounts'
    raise Exception(r['title'])
for i in range(1,8):
    b=json.load(open(os.path.join(D,f'batches/b0{i}.json'))); out=[]
    for r in b:
        tp,tg,fl,w=rec(r)
        assert set(tp)<=TOP and set(tg)<=TAGS,(tp,tg)
        out.append({'key':r['key'],'topics':tp,'tags':tg,'flags':fl,'why':w})
    os.makedirs(os.path.join(D,'results'),exist_ok=True)
    json.dump(out,open(os.path.join(D,f'results/b0{i}.json'),'w'),ensure_ascii=False,indent=1)
    print(i,len(out),sum(1 for o in out if o['tags']))
