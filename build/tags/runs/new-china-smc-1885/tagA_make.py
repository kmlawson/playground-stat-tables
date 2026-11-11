import json,re
B='batches/'
def A(t,g=(),f=(),w=''): return dict(topics=list(t),tags=list(g),flags=list(f),why=w)
M=['militias-and-volunteer-forces']
O={
'p0008_1':A(['military'],M,w='volunteer corps strength'),'p0008_2':A(['military'],M,w='staff and band'),
'p0008_3':A(['military'],M,w='inspection strength'),
'p0008_4':A(['military'],M,['text-tables'],'commissions roster'),'p0008_5':A(['military'],M,['text-tables'],'resignations list'),
'p0008_6':A(['military'],M,['text-tables'],'death list'),'p0009_1':A(['military'],M,w='corps strength'),
'p0021_1':A(['population'],['population-totals','age-and-sex'],w='foreign pop by class'),
'p0021_2':A(['population'],['population-totals','age-and-sex'],w='native pop'),
'p0022_1':A(['population'],['nationality-and-ethnicity','overseas-communities'],w='foreign census by nationality'),
'p0023_1':A(['population'],['occupations','overseas-communities'],w='foreign occupations'),
'p0025_1':A(['population'],['population-totals'],w='native census'),
'p0026_1':A(['population'],['migration','population-totals'],w='native pop by native province'),
'p0027_1':A(['population'],['households'],w='native houses and occupants'),
'p0027_2':A(['population'],['households'],w='houses by year'),
'p0038_1':A(['utilities','finance'],['electricity'],w='electric plant estimate'),
'p0040_1':A(['utilities'],['electricity'],w='lamps out'),
'p0042_1':A(['finance','government'],['pawnshops'],w='pawn-shop licences'),
'p0047_1':A(['finance','trade'],['taxation'],w='liquor licence fees'),
'p0052_1':A(['crime-and-justice'],['police'],w='police strength'),
'p0053_1':A(['crime-and-justice'],['offences-and-convictions','police'],w='arrests foreigners'),
'p0054_1':A(['crime-and-justice'],['prisons'],w='gaol prisoners'),
'p0055_1':A(['crime-and-justice'],['offences-and-convictions','police'],w='apprehended by offence'),
'p0057_1':A(['crime-and-justice'],['offences-and-convictions','literacy-and-adult-education'],w='offences and literacy'),
'p0059_1':A(['crime-and-justice'],['corporal-punishment','offences-and-convictions'],w='punishments'),
'p0061_1':A(['crime-and-justice'],['offences-and-convictions'],w='arrests comparison'),
'p0062_1':A(['crime-and-justice'],['police'],w='arrested not charged'),
'p0063_1':A(['crime-and-justice'],['police','courts'],w='warrants summonses'),
'p0066_1':A(['health'],['public-health'],w='garbage'),
'p0079_1':A(['health','agriculture'],['food-inspection','livestock'],w='animals slaughtered'),
'p0079_2':A(['health','agriculture'],['food-inspection','livestock'],w='animals grease-shops'),
'p0080_1':A(['health','population'],['births-and-deaths','age-and-sex'],w='deaths by age'),
'p0081_1':A(['health','population'],['births-and-deaths'],w='death rate series'),
'p0082_1':A(['health'],['epidemics','diseases'],w='cholera cases'),
'p0083_1':A(['health'],['epidemics','diseases'],w='cholera by month'),
'p0085_1':A(['health'],['public-health'],w='disinfection recipes'),
'p0086_1':A(['health'],['epidemics','diseases'],w='cholera deaths by year'),
'p0090_1':A(['health','population'],['diseases','births-and-deaths'],w='deaths by cause'),
'p0091_1':A(['health','population'],['diseases','births-and-deaths'],w='deaths by cause'),
'p0091_2':A(['health','population'],['births-and-deaths','diseases'],w='deaths by age cause'),
'p0093_1':A(['finance'],['public-debt'],w='loan tenders'),
'p0098_2':A(['finance'],['public-budgets','taxation'],w='licence fees excess'),
'p0100_1':A(['finance'],['taxation','real-estate'],w='municipal rate'),
'p0104_1':A(['finance'],['taxation','real-estate'],w='assessments reduced'),
'p0105_1':A(['finance'],['taxation','real-estate'],w='assessments increased'),
'p0106_1':A(['finance'],['taxation','real-estate'],w='lots assessed'),
'p0110_1':A(['communications','government'],['postal-services'],w='correspondence'),
'p0119_1':A(['finance','culture'],['recreation-and-amusements'],w='recreation ground expenditure'),
'p0125_1':A(['population'],['births-and-deaths'],w='burials'),
'p0129_1':A(['utilities'],['water-and-sewerage'],w='pipe drains'),
'p0133_2':A(['transportation'],['roads-and-bridges'],w='road extensions progress'),
'p0171_1':A(['utilities','finance'],['electricity'],w='electric plant cost'),
'p0184_1':A(['education','finance'],['education-finance'],w='school account'),
'p0187_1':A(['finance'],[],w='memo account'),
'p0197_1':A(['culture','finance'],['arts-and-music'],w='band expenditure'),
'p0198_1':A(['culture','finance'],['arts-and-music'],w='band estimate'),
'p0201_1':A(['disasters'],['firefighting'],w='hose distribution'),
'p0203_1':A(['finance','disasters'],['firefighting'],w='fire brigade accounts'),
'p0205_1':A(['finance','disasters'],['firefighting'],w='fire brigade estimate'),
'p0205_2':A(['government','disasters'],['firefighting'],['text-tables'],'fire commission roster'),
'p0210_1':A(['disasters'],['fires','firefighting'],w='fire record'),
'p0243_1':A(['finance'],['savings-and-loans'],w='police savings bank'),
'p0243_2':A(['finance','crime-and-justice'],['police'],w='police fund'),
'p0244_1':A(['finance','crime-and-justice'],['police'],w='secret service fund'),
'p0246_3':A(['finance','crime-and-justice'],['insurance-and-pensions','police'],w='police pension'),
'p0247_1':A(['finance'],['public-debt'],w='sinking fund'),
'p0248_2':A(['finance','military'],M,w='volunteer prize fund'),
'p0249_1':A(['finance'],['public-property'],w='property valuation'),
'p0255_1':A(['finance'],['public-budgets'],w='balance sheet'),
'p0261_1':A(['finance'],['public-budgets'],w='actual vs estimate'),
'p0291_1':A(['finance'],['public-budgets'],w='comparative statement'),
}
# keyword rules for finance statement/budget tables (first match wins)
R=[('police pension',['finance','crime-and-justice'],['insurance-and-pensions','police']),
('police',['finance','crime-and-justice'],['police','public-budgets']),
('bubbling well road station',['finance','crime-and-justice'],['police','public-budgets']),
('land tax',['finance'],['land-tax','taxation']),
('general municipal rate',['finance'],['taxation','public-budgets']),
('dues on merchandise',['finance'],['customs-revenue','public-budgets']),
('license fees',['finance'],['taxation','public-budgets']),
('licence',['finance'],['taxation','public-budgets']),
('poundage',['finance'],['public-budgets']),
('lock hospital',['finance','health'],['medical-services','public-budgets']),
('night-soil',['finance','health'],['public-health','public-budgets']),
('relief of poor',['finance','welfare'],['poor-relief','public-budgets']),
('hospital',['finance','health'],['medical-services','public-budgets']),
('medical',['finance','health'],['medical-services','public-budgets']),
('nuisance',['finance','health'],['public-health','public-budgets']),
('sanitary',['finance','health'],['public-health','public-budgets']),
('lighting',['finance','utilities'],['electricity','public-budgets']),
('telegraph',['finance','communications'],['telegraph','public-budgets']),
('telephone',['finance','communications'],['telephone','public-budgets']),
('cemeter',['finance'],['public-budgets']),
('outside roads',['finance','transportation'],['roads-and-bridges','public-budgets']),
('widening',['finance','transportation'],['roads-and-bridges','public-budgets']),
('public garden',['finance','culture'],['recreation-and-amusements','public-budgets']),
('public works',['finance','utilities'],['construction','public-budgets']),
('museum',['finance','culture'],['museums-and-heritage','public-budgets']),
('library',['finance','culture'],['libraries','public-budgets']),
('education',['finance','education'],['education-finance','public-budgets']),
('stud',['finance','agriculture'],['livestock','public-budgets']),
('water supply',['finance','utilities'],['water-and-sewerage','public-budgets']),
('interest',['finance'],['public-debt','public-budgets']),
('sinking fund',['finance'],['public-debt','public-budgets']),
('loan',['finance'],['public-debt','public-budgets']),
('fire department',['finance','disasters'],['firefighting','public-budgets']),
('volunteers',['finance','military'],M+['public-budgets']),
('town band',['finance','culture'],['arts-and-music','public-budgets']),
('post office',['finance','communications'],['postal-services','public-budgets']),
('secretariat',['finance','government'],['government-offices','public-budgets']),
('surveyor',['finance','government'],['government-offices','public-budgets']),
('land and buildings',['finance'],['public-property','public-budgets']),
('stock and stores',['finance'],['public-budgets']),
]
S={'p0096','p0097','p0098'}
out_all=0
for i in range(1,8):
    b='b%02d'%i
    recs=json.load(open(B+b+'.json'));res=[]
    for r in recs:
        k=r['key'];loc=k.split(':')[1]
        if loc in O: a=O[loc]
        else:
            t=(r['title']+' '+(r.get('chapter') or '')).lower()
            a=None
            if r['chapter'] and r['chapter'].startswith(('Finance','Budget')) or 'budget' in t:
                tl=r['title'].lower()
                if 'brought' in tl or 'carry' in tl or 'closing' in tl or 'no sub-head' in tl or 'depreciation' in tl or 'deficit' in tl or 'outstanding' in tl:
                    a=A(['finance'],['public-budgets'],w='carry/closing lines of municipal accounts')
                else:
                    for kw,tp,tg in R:
                        if kw in tl: a=A(tp,tg,w='municipal accounts: '+kw);break
                    if not a: a=A(['finance'],['public-budgets'],w='municipal accounts')
            if not a:
                m=re.match(r'p00(8|9|1)',loc)
                if r['title'].startswith('S.V.C.'): a=A(['military'],['arms-and-arsenals']+M,w='volunteer arms stock')
                elif loc in('p0131_1','p0132_1','p0132_2','p0132_3','p0133_1'): a=A(['transportation'],['roads-and-bridges'],w='road works')
                elif loc.startswith('p009') or loc.startswith('p0096'): a=A(['finance'],['public-budgets'],w='council finances')
                elif loc.startswith('p0101') or loc.startswith('p0102') or loc.startswith('p0103'): a=A(['finance'],['taxation','real-estate'],w='municipal rate quarter')
                else: print('UNMAPPED',loc,r['title'])
        res.append(dict(key=k,**a))
    json.dump(res,open('results/%s.json'%b,'w'),ensure_ascii=False,indent=1)
    assert [x['key'] for x in res]==[r['key'] for r in recs]
    print(b,len(res),sum(1 for x in res if x['tags']))
