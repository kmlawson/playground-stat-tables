import json,re
V=json.load(open('../../vocabulary.json'))
TOP={t['id'] for t in V['topics']}
TAG={(t['id'] if isinstance(t,dict) else t) for t in V['tags']}
M={}
def S(b,idx,topics,tags,flags=(),why=''):
    for i in ([idx] if isinstance(idx,int) else idx): M[(b,i)]=(topics,tags,list(flags),why)
mil=['military'],['militias-and-volunteer-forces']
S('b01',[0,1,2],*mil,why='volunteer corps strength')
S('b01',3,*mil,flags=['text-tables'],why='officer roster')
S('b01',[4,5,6,7,8],['military'],['arms-and-arsenals','militias-and-volunteer-forces'],why='arms and ammunition stock')
S('b01',9,['finance'],['pawnshops'],why='pawn-shop licences')
S('b01',10,['finance'],['taxation','alcohol'],why='liquor licence fees')
S('b01',11,['crime-and-justice'],['police'],why='police strength')
S('b01',[12,16,17,18,21],['crime-and-justice'],['offences-and-convictions','police'],why='arrests by offence')
S('b01',13,['crime-and-justice'],['offences-and-convictions','literacy-and-adult-education'],why='prisoners by offence and literacy')
S('b01',14,['crime-and-justice'],['offences-and-convictions','corporal-punishment'],why='punishments')
S('b01',15,['crime-and-justice'],['prisons'],why='gaol population')
S('b01',19,['crime-and-justice'],['police','courts'],why='warrants and summonses')
S('b01',20,['crime-and-justice'],['police'],why='police length of service')
S('b01',22,['crime-and-justice','finance'],['police'],why='police rate collected')
S('b01',23,['health'],['public-health'],why='garbage collected')
S('b01',[24,25],['health'],['food-inspection','livestock'],why='animals slaughtered')
S('b01',26,['population','health'],['births-and-deaths','age-and-sex'],why='deaths by age')
S('b01',27,['population','health'],['births-and-deaths','nationality-and-ethnicity'],why='deaths by nationality')
S('b01',28,['population','health'],['births-and-deaths'],why='death rate')
S('b01',29,['health','population'],['epidemics','diseases'],why='cholera deaths')
S('b01',[30,31,33],['population','health'],['births-and-deaths','diseases'],why='deaths by cause')
S('b01',32,['population','health'],['infant-mortality','births-and-deaths'],why='infant deaths')
S('b01',[34,35],['finance'],['public-debt'],why='municipal loans')
S('b01',[36,38,39],['finance'],['public-budgets'],why='municipal accounts')
S('b01',37,['finance'],['public-budgets','taxation'],why='licence fees in excess')
S('b02',[0,1,2,3,4,5,6,7,8,9,10],['finance'],['taxation','real-estate'],why='rate assessments of houses')
S('b02',11,['finance'],['taxation','land-registration'],why='land lots assessed')
S('b02',[12,13],['communications'],['postal-services'],why='local post')
S('b02',[14,15,16,17,18,19,20],['transportation'],['roads-and-bridges'],why='road works')
S('b02',21,['population'],['births-and-deaths'],why='cemetery burials')
S('b02',[22,23,24],['utilities'],['water-and-sewerage'],why='drains/water')
S('b02',25,['finance','disasters'],['insurance-and-pensions','firefighting'],why='fire engine price')
S('b02',26,['education','finance'],['education-finance'],why='school accounts')
S('b02',27,['culture'],['recreation-and-amusements'],why='park admissions')
S('b02',28,['culture','finance'],['recreation-and-amusements','public-budgets'],why='recreation ground expenditure')
S('b02',[29,32,33],['finance','culture'],['public-budgets','arts-and-music'],why='band accounts')
S('b02',[30,31],['culture'],['arts-and-music'],why='band services/repertoire')
S('b02',[34,35,36],['government'],['government-offices','firefighting'],['text-tables'],'fire commission roster')
S('b02',37,['disasters'],['firefighting'],why='hose distribution')
S('b02',38,['disasters'],['fires','firefighting'],why='fires and houses burnt')
S('b02',39,['finance','disasters'],['public-budgets','firefighting'],why='fire brigade accounts')
S('b03',[0,1],['finance','disasters'],['public-budgets','firefighting'],why='fire dept accounts')
S('b03',2,['government'],['government-offices','firefighting'],['text-tables'],'fire commission members')
S('b03',3,['disasters'],['fires'],why='fire record summary')
RULES=[ # (regex on lower title, topics, extra tags)
 (r'land and house tax|land tax|general municipal rate',['finance'],['taxation']),
 (r'license|permit fees|dues',['finance'],['taxation']),
 (r'lock hospital|hospital|medical',['finance','health'],['medical-services']),
 (r'night-soil|nuisance|sanitary',['finance','health'],['public-health']),
 (r'relief of poor',['finance','welfare'],['poor-relief']),
 (r'police savings bank',['finance'],['savings-and-loans']),
 (r'police|carter road|bubbling well',['finance','crime-and-justice'],['police']),
 (r'water supply',['finance','utilities'],['water-and-sewerage']),
 (r'lighting',['finance','utilities'],['electricity','gas']),
 (r'telephone',['finance','communications'],['telephone']),
 (r'post office',['finance','communications'],['postal-services']),
 (r'bridges|roads|bund|widening',['finance','transportation'],['roads-and-bridges']),
 (r'drainage',['finance','utilities'],['water-and-sewerage']),
 (r'landing-stages',['finance','transportation'],['ports']),
 (r'fire-wells|fire department|fire',['finance','disasters'],['firefighting']),
 (r'volunteers',['finance','military'],['militias-and-volunteer-forces']),
 (r'band',['finance','culture'],['arts-and-music']),
 (r'museum',['finance','culture'],['museums-and-heritage']),
 (r'library',['finance','culture'],['libraries']),
 (r'education',['finance','education'],['education-finance']),
 (r'sinking fund|loan|interest',['finance'],['public-debt']),
 (r'buildings|bundings|land and buildings|latrines',['finance'],['construction']),
 (r'public garden|cemeter',['finance','culture'],['recreation-and-amusements']),
 (r'surveyor',['finance','government'],['government-offices']),
 (r'secretariat|general charges|stud',['finance','government'],['government-offices']),
]
def rule(r):
    t=r['title'].lower()
    # use the sub-head part after the section word
    for pat,tp,tg in RULES:
        if re.search(pat,t): 
            tags=['public-budgets']+tg
            if tg and tg[0] in('taxation',) : tags=['taxation','public-budgets']
            return tp,tags[:3],[], 'budget/statement section: '+pat.split('|')[0]
    return ['finance'],['public-budgets'],[],'municipal financial statement'
for b in ['b01','b02','b03','b04','b05','b06','b07']:
    recs=json.load(open(f'batches/{b}.json')); out=[]
    for i,r in enumerate(recs):
        if (b,i) in M: tp,tg,fl,w=M[(b,i)]
        else:
            tp,tg,fl,w=rule(r)
            t=r['title'].lower()
            if 'brought' in t or 'page totals' in t or 'carry' in t or 'subtotals' in t: tp,tg,w=['finance'],['public-budgets'],'running totals'
            if re.search(r'trust funds|bank|savings|contractor|fund|deposit',t) and b=='b05' and i>=17 and i<=35:
                tp,tg=['finance'],(['banking'] if 'bank' in t else ['public-budgets']); 
                if 'police savings' in t: tg=['savings-and-loans']
                w='trust fund account'
            if 'land, buildings and property' in t: tp,tg=['finance'],['public-property']
            if 'balance sheet' in t or 'general statement' in t or 'outstanding' in t or 'comparing' in t or 'comparative' in t or 'summary of' in t: tp,tg=['finance'],['public-budgets']
        assert all(x in TOP for x in tp),(b,i,tp); assert all(x in TAG for x in tg),(b,i,tg)
        out.append(dict(key=r['key'],topics=tp[:2],tags=tg[:3],flags=fl,why=w))
    json.dump(out,open(f'results/{b}.json','w'),ensure_ascii=False,indent=1)
    assert [o['key'] for o in out]==[r['key'] for r in recs]
    print(b,len(out),sum(1 for o in out if o['tags']))
