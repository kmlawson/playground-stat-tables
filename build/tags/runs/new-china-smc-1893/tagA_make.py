import json,re
B='batches/'
M=['militias-and-volunteer-forces']
# explicit: (topics,tags,flags,why) per batch index
X={}
def S(b,i,t,g,f=False,w=''):
    X[(b,i)]=(t,g,['text-tables'] if f else [],w)
mil=lambda i,g=M,f=False,w='volunteer corps':S('b01',i,['military'],g,f,w)
mil(0,M+['arms-and-arsenals']);mil(1);mil(2);mil(3);mil(4,[],True);mil(5);mil(6,M,True);mil(7,M,True);mil(8,M);mil(9,M+['arms-and-arsenals'])
S('b01',10,['utilities'],['gas'],0,'gas lamps');S('b01',11,['utilities'],['gas'],0,'lamps lighted')
S('b01',12,['utilities'],['electricity'],0,'electric lamps')
S('b01',13,['finance','government'],['pawnshops'],0,'pawn-shop licences')
S('b01',14,['transportation','government'],['road-transport','taxation'],0,'carriage licence fees')
S('b01',15,['transportation','government'],['inland-navigation','taxation'],0,'boat licence fees')
S('b01',16,['finance','government'],['taxation','alcohol'],0,'liquor licence fees')
S('b01',17,['crime-and-justice'],['prisons'],0,'prisoners confined')
for i in (18,21,22,23,25):S('b01',i,['crime-and-justice'],['offences-and-convictions'],0,'arrests by offence')
S('b01',19,['crime-and-justice'],['offences-and-convictions','literacy-and-adult-education'],0,'prisoners by offence and literacy')
S('b01',20,['crime-and-justice'],['corporal-punishment','offences-and-convictions'],0,'punishments')
S('b01',24,['crime-and-justice'],['police'],0,'warrants and summonses')
S('b01',26,['crime-and-justice'],['police'],0,'police strength')
S('b01',27,['finance','crime-and-justice'],['police'],0,'policing fund subscriptions')
S('b01',28,['health'],['public-health'],0,'garbage removal')
S('b01',29,['health','agriculture'],['food-inspection','livestock'],0,'animals slaughtered')
S('b01',30,['population','health'],['births-and-deaths','age-and-sex'],0,'deaths by age')
S('b01',31,['population','health'],['births-and-deaths'],0,'death rates')
S('b01',32,['health'],['diseases','epidemics'],0,'smallpox deaths')
S('b01',33,['health'],['epidemics','diseases'],0,'cholera deaths')
S('b01',34,['health'],['diseases'],0,'disease deaths')
S('b01',35,['health'],['public-health'],1,'sanitary board matters')
for i in (36,37,39):S('b01',i,['population','health'],['births-and-deaths','diseases'],0,'deaths by cause')
S('b01',38,['population','health'],['infant-mortality','births-and-deaths'],0,'child deaths')
S('b02',0,['health'],['vaccination'],0,'vaccine station salaries');S('b02',1,['health'],['vaccination'],0,'vaccine station expenses')
S('b02',2,['finance','utilities'],['public-debt','electricity'],0,'debentures for electricity')
S('b02',3,['finance','trade'],['taxation'],0,'dues on merchandise')
S('b02',4,['finance'],['public-budgets'],0,'receipts and surplus')
S('b02',5,['finance'],['taxation','public-budgets'],0,'licence fees vs estimate')
S('b02',6,['finance'],['public-budgets'],0,'budget excess');S('b02',7,['finance'],['public-budgets'],0,'unexpended')
S('b02',8,['finance','utilities'],['electricity','savings-and-loans'],0,'electric deposit')
S('b02',9,['communications'],['postal-services'],0,'mail volume');S('b02',10,['communications'],['postal-services'],0,'postal rates');S('b02',11,['communications'],['postal-services'],0,'postal rates')
S('b02',12,['government'],['government-offices'],1,'committee members')
S('b02',13,['communications'],['postal-services'],0,'stamps issued')
for i in range(14,24):S('b02',i,['finance'],['taxation','real-estate'],0,'municipal rate and houses')
S('b02',25,['transportation'],['roads-and-bridges'],0,'road mileage')
for i in (26,27,28,29,30,35):S('b02',i,['transportation'],['roads-and-bridges'],1,'road lists')
S('b02',31,['transportation'],['roads-and-bridges'],0,'footways area')
S('b02',32,['utilities'],['construction'],0,'concrete ware')
S('b02',33,['transportation'],['roads-and-bridges','land-tenure'],0,'road land transactions');S('b02',34,['transportation'],['roads-and-bridges','land-tenure'],0,'road land strips')
S('b02',36,['labour'],['employment-and-unemployment'],0,'workmen');S('b02',37,['labour'],['employment-and-unemployment'],0,'workmen')
S('b02',38,['transportation'],['roads-and-bridges'],0,'outside roads')
S('b02',39,['utilities'],['construction'],0,'building operations')
S('b03',0,['population'],['births-and-deaths'],0,'burials')
S('b03',1,['utilities'],['water-and-sewerage'],0,'sewers');S('b03',2,['utilities'],['water-and-sewerage'],0,'pipes and drains')
S('b03',3,['utilities'],['electricity'],1,'private lighting consumers')
S('b03',4,['utilities','finance'],['electricity'],0,'electricity account');S('b03',5,['finance','utilities'],['electricity'],0,'balance sheet');S('b03',6,['finance','utilities'],['electricity'],0,'estimate');S('b03',7,['utilities','finance'],['electricity'],0,'new station cost')
S('b03',8,['finance','culture'],['recreation-and-amusements','public-budgets'],0,'recreation ground expenditure');S('b03',9,['finance','culture'],['recreation-and-amusements','public-budgets'],0,'garden expenditure')
for i in range(10,16):S('b03',i,['utilities'],['water-and-sewerage'],0,'water use')
S('b03',16,['education'],['schools-and-pupils'],0,'attendance')
S('b03',17,['education','finance'],['education-finance'],0,'school accounts');S('b03',18,['education','finance'],['education-finance'],0,'school estimate')
S('b03',19,['education'],['schools-and-pupils','school-curricula'],0,'forms');S('b03',20,['education'],['schools-and-pupils','school-curricula'],0,'forms')
S('b03',21,['education'],['kindergartens','school-curricula'],0,'kindergarten');S('b03',22,['education'],['schools-and-pupils','school-curricula'],0,'Chinese dept')
for i in (23,25,26):S('b03',i,['culture'],['arts-and-music'],0,'band music')
for i in (24,27,28):S('b03',i,['culture','finance'],['arts-and-music','public-budgets'],0,'band accounts')
for i in (29,30,31,36):S('b03',i,['government','disasters'],['firefighting','government-offices'],1,'fire commission names')
S('b03',32,['disasters'],['fires'],0,'fires compared');S('b03',37,['disasters'],['fires'],0,'fires summary')
for i in (33,34,35):S('b03',i,['disasters','finance'],['firefighting','public-budgets'],0,'fire dept accounts')
S('b03',38,['finance'],['public-budgets','land-tax'],0,'land tax revenue');S('b03',39,['finance'],['taxation','public-budgets'],0,'licence fee revenue')

RULES=[
 (r'Police Deferred|Deferred Pay',['finance'],['insurance-and-pensions','public-budgets']),
 (r'Police Savings|Tax Collectors Savings',['finance'],['savings-and-loans']),
 (r'Hongkong & Shanghai Bank|Chartered Bank',['finance'],['banking']),
 (r'Working Accounts|Liquor-Sellers|Coolies|Deposit|Fund$|Contractor|Billiard|Widow|Prize Fund|Recreation Fund|Secret Service',['finance'],['savings-and-loans']),
 (r'Land, Buildings and Property',['finance'],['public-property']),
 (r'Balance Sheet',['finance'],['public-property','public-debt']),
 (r'Outstanding',['finance'],['public-budgets']),
 (r'Land Tax',['finance'],['taxation','land-tax']),
 (r'General Municipal Rate',['finance'],['taxation','real-estate']),
 (r'Dues on Merchandise',['finance','trade'],['taxation']),
 (r'License Fees|Permit Fees',['finance'],['taxation','public-budgets']),
 (r'Police|Carter Road',['finance','crime-and-justice'],['public-budgets','police']),
 (r'Slaughter',['finance','health'],['public-budgets','food-inspection']),
 (r'Hospital|Medical',['finance','health'],['public-budgets','medical-services']),
 (r'Night-soil|Nuisance|Latrine|Sanitary|Markets',['finance','health'],['public-budgets','public-health']),
 (r'Relief of Poor',['finance','welfare'],['public-budgets','poor-relief']),
 (r'Water Supply',['finance','utilities'],['public-budgets','water-and-sewerage']),
 (r'Telephone',['finance','communications'],['public-budgets','telephone']),
 (r'Lighting|Electrical',['finance','utilities'],['public-budgets','electricity']),
 (r'Local Post Office|Post Office',['finance','communications'],['public-budgets','postal-services']),
 (r'Cemeter',['finance'],['public-budgets']),
 (r'Public Gardens|Gardens',['finance','culture'],['public-budgets','recreation-and-amusements']),
 (r'Drainage|Landing|Bridges|Roads|Widening|Public Works|Engineer',['finance','transportation'],['public-budgets','roads-and-bridges']),
 (r'Education|Shanghai Public|School',['finance','education'],['education-finance','public-budgets']),
 (r'Library|Museum',['finance','culture'],['public-budgets','museums-and-heritage']),
 (r'Volunteers',['finance','military'],['public-budgets','militias-and-volunteer-forces']),
 (r'Fire Department|Fire Insurance',['finance','disasters'],['public-budgets','firefighting']),
 (r'Band',['finance','culture'],['public-budgets','arts-and-music']),
 (r'Sinking Fund|Loan|Interest|Debenture',['finance'],['public-debt','public-budgets']),
 (r'Jubilee',['finance'],['public-budgets']),
]
def rule(r):
    t=r['title']
    for pat,tp,tg in RULES:
        if re.search(pat,t): return tp,tg
    return ['finance'],['public-budgets']
out_n=0
for n in range(1,9):
    b='b%02d'%n
    d=json.load(open(B+b+'.json'));res=[]
    for i,r in enumerate(d):
        if (b,i) in X: tp,tg,fl,w=X[(b,i)]
        else:
            tp,tg=rule(r);fl=[];w='municipal accounts/budget: '+r['title'][-40:]
        res.append({'key':r['key'],'topics':tp,'tags':tg,'flags':fl,'why':w})
    assert len(res)==len(d)
    json.dump(res,open('results/%s.json'%b,'w'),ensure_ascii=False,indent=1)
