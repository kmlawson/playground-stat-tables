import json,re
B='batches/'
E={}  # suffix -> (topics,tags,flags,why)
def e(keys,t,g,w,f=()):
    for k in keys.split(): E[k]=(t,g,list(f),w)
M=['military'];
e('p0014_1 p0014_2',M,['militias-and-volunteer-forces'],'volunteer corps strength')
e('p0015_1 p0016_1',M,['militias-and-volunteer-forces'],'volunteer corps roster',['text-tables'])
e('p0018_1 p0019_1 p0019_2 p0020_1 p0021_1',M,['arms-and-arsenals'],'volunteer arms and ammunition stock')
e('p0023_1',['population'],['population-totals','nationality-and-ethnicity'],'foreign census')
e('p0023_2 p0024_1 p0028_1 p0028_2',['population'],['population-totals'],'native census')
e('p0024_2',['population','finance'],['housing','taxation'],'houses assessed, occupancy')
e('p0025_1',['population'],['nationality-and-ethnicity','overseas-communities'],'foreign residents by nationality')
e('p0025_2',['population'],['population-totals'],'shipping and naval census')
e('p0026_1',['population'],['occupations'],'foreign residents by profession')
e('p0029_1',['population'],['migration'],'natives by province of origin')
e('p0030_1',['population'],['population-totals','housing'],'native houses and occupants by road')
e('p0038_1',['finance','government'],['pawnshops'],'pawn-shop licences')
e('p0039_1',['government','transportation'],['inland-navigation'],'boat and sampan licences')
e('p0040_1',['government','finance'],[],'liquor licence fees')
e('p0044_1',['crime-and-justice'],['prisons'],'prisoners confined')
e('p0046_1',['government','crime-and-justice'],['police'],'police strength')
e('p0048_1 p0055_1 p0056_1 p0057_1 p0059_1',['crime-and-justice'],['offences-and-convictions'],'arrests and offences')
e('p0050_1',['crime-and-justice'],['offences-and-convictions','literacy-and-adult-education'],'prisoners by offence and literacy')
e('p0052_1',['crime-and-justice'],['corporal-punishment','offences-and-convictions'],'punishments')
e('p0054_1',['crime-and-justice'],['prisons'],'weekly gaol returns')
e('p0058_1',['crime-and-justice'],['police','courts'],'warrants and summonses')
e('p0060_1 p0061_1',['government','crime-and-justice'],['police'],'police force variations')
e('p0062_1',['finance','crime-and-justice'],[],'monthly subscriptions, Bubbling Well policing')
e('p0067_1',['health','utilities'],['public-health'],'garbage collection')
e('p0077_1',['health','agriculture'],['food-inspection','livestock'],'animals slaughtered')
e('p0079_1',['population','health'],['births-and-deaths','age-and-sex'],'deaths by age')
e('p0080_1',['population','health'],['births-and-deaths'],'death rates')
e('p0082_1',['health'],['epidemics','diseases'],'cholera cases')
e('p0083_1',['health'],['epidemics','births-and-deaths'],'cholera deaths by month')
e('p0088_1 p0089_1 p0091_1',['health','population'],['births-and-deaths','diseases'],'deaths by cause')
e('p0090_1',['population','health'],['infant-mortality','births-and-deaths'],'infant deaths',['text-tables'] if False else [])
e('p0098_1',['finance'],['public-debt'],'debenture allotments')
e('p0099_1 p0102_1 p0102_2',['finance'],['public-budgets'],'municipal accounts')
e('p0101_1',['finance'],['public-budgets'],'licence fee excess/deficiency')
e('p0104_1',['finance'],['taxation','real-estate'],'assessments')
e('p0110_1 p0111_1 p0113_1',['finance'],['taxation','real-estate'],'house assessments')
e('p0115_1',['communications'],['postal-services'],'local post office correspondence')
e('p0147_1',['government','crime-and-justice'],['police'],'police station accommodation')
e('p0148_1',['government','crime-and-justice'],['police'],'outhouse contents list',['text-tables'])
e('p0150_1 p0150_2 p0172_1 p0172_2',['utilities'],['water-and-sewerage'],'drains laid')
e('p0151_1 p0214_1 p0214_2',['utilities'],['water-and-sewerage'],'water used')
e('p0152_1',['transportation'],['ports'],'jetty traffic')
e('p0156_1',['transportation'],['roads-and-bridges'],'pavement temperatures')
e('p0164_1',['transportation'],['roads-and-bridges'],'proposed roads list',['text-tables'])
e('p0165_1 p0166_2',['transportation'],['roads-and-bridges'],'roads made/metalled',['text-tables'] if False else [])
e('p0165_2 p0166_1',['labour'],['employment-and-unemployment'],'coolies and artisans employed')
e('p0168_1 p0168_2',['utilities'],['construction','housing'],'houses built')
e('p0170_1',['population'],['births-and-deaths'],'burials')
e('p0178_1 p0180_1',['finance','culture'],['recreation-and-amusements','public-budgets'],'park expenditure')
e('p0187_1',['government','crime-and-justice'],['police'],'police station accommodation')
e('p0225_1',['culture'],['arts-and-music'],'band repertoire')
e('p0225_2 p0230_1 p0231_1',['culture','finance'],['arts-and-music'],'band accounts')
e('p0226_1',['culture'],['arts-and-music'],'band services')
e('p0232_1 p0232_2',['disasters','government'],['firefighting'],'fire brigade office-holders',['text-tables'])
e('p0233_1',['disasters'],['firefighting'],'hose distribution')
e('p0233_2 p0233_3 p0247_1',['disasters'],['fires'],'fire records')
e('p0234_1 p0236_1 p0238_1',['disasters','finance'],['firefighting'],'fire department accounts')
PD=['finance'];PB='public-budgets'
POL=set('p0249_1 p0249_2 p0249_3 p0249_4 p0249_5 p0249_6 p0249_7 p0251_1 p0253_1 p0316_1 p0318_1 p0318_2 p0318_3 p0318_4 p0318_5 p0318_6 p0318_7 p0330_2'.split())
def fin(k,title):
    t=title.lower()
    if 'police deferred' in t: return ['finance'],['insurance-and-pensions',PB],'police deferred pay fund'
    if k in POL: return ['finance','crime-and-justice'],[PB,'police'],'police charges'
    if 'police savings bank' in t: return ['finance'],['savings-and-loans'],'police savings bank'
    if k.startswith(('p029')) and 'bank' in t: return ['finance'],['banking'],'bank trust account'
    if 'foochow road hospital' in t or 'medical' in t: return ['finance','health'],[PB,'medical-services'],'medical'
    if k=='p0253_5' or 'sanitary' in t and 'hospital' in t: return ['finance','health'],[PB,'medical-services'],'hospitals'
    if 'night-soil' in t or 'nuisance' in t and 'stock' not in t and 'contractor' not in t: return ['finance','health'],[PB,'public-health'],'sanitary'
    if 'relief of poor' in t: return ['finance','welfare'],[PB,'poor-relief'],'poor relief'
    if t.endswith('land tax'): return PD,['land-tax','taxation'],'land tax'
    if 'general municipal rate' in t: return PD,['taxation','real-estate'],'municipal rate'
    if 'dues on merchandise' in t or 'dues on merchandize' in t: return PD,['taxation'],'dues'
    if 'water supply' in t: return ['finance','utilities'],[PB,'water-and-sewerage'],'water'
    if 'lighting' in t: return ['finance','utilities'],[PB,'electricity'],'lighting'
    if 'telephone' in t: return ['finance','communications'],[PB,'telephone'],'telephone'
    if 'local post office' in t and 'coolies' not in t and 'non-sub' not in t: return ['finance','communications'],[PB,'postal-services'],'post office'
    if 'drain' in t: return ['finance','utilities'],[PB,'water-and-sewerage'],'drainage'
    if 'landing' in t: return ['finance','transportation'],[PB,'ports'],'landing-stages'
    if 'bridges' in t or 'roads' in t or 'widening' in t: return ['finance','transportation'],[PB,'roads-and-bridges'],'roads/bridges'
    if 'fire department' in t: return ['finance','disasters'],[PB,'firefighting'],'fire dept'
    if 'volunteers' in t and 'prize' not in t: return ['finance','military'],[PB,'militias-and-volunteer-forces'],'volunteers'
    if 'band' in t: return ['finance','culture'],[PB,'arts-and-music'],'band'
    if 'museum' in t: return ['finance','culture'],[PB,'museums-and-heritage'],'museum'
    if 'library' in t: return ['finance','culture'],[PB,'libraries'],'library'
    if 'education grants' in t: return ['finance','education'],['education-finance',PB],'education grants'
    if 'sinking fund' in t or 'municipal loan' in t or 'interest' in t: return PD,['public-debt',PB],'debt/interest'
    if 'secretariat' in t or 'surveyor' in t or 'general charges' in t or 'stud' in t.split()[-1:]: return ['finance','government'],[PB],'administration'
    if 'land, buildings and property' in t: return PD,['public-property'],'property'
    if 'buildings' in t: return PD,['public-property',PB],'buildings'
    if 'working accounts' or True:
        pass
    return PD,[PB],'budget/statement line'
for b in range(1,8):
    d=json.load(open(B+'b%02d.json'%b));out=[]
    for r in d:
        k=r['key'].split(':')[1]; pr=r.get('prior')
        if k in E: t,g,f,w=E[k]
        elif r['chapter'].startswith('Finance — Working') and k not in ('p0292_1','p0292_2','p0293_1','p0294_1','p0288_1'):
            t,g,f,w=['finance'],[],[],'trust-fund deposit account'
            if k=='p0294_1': g=['public-debt']
        elif pr and k in ('p0106_1','p0106_2','p0107_1','p0107_2','p0108_1','p0108_2','p0109_1','p0109_2','p0220_1','p0238_2'):
            t,g,f,w=pr['topics'],pr['tags'],pr['flags'],'prior kept'
            if k=='p0238_2': f=['text-tables']
        else: t,g,w=fin(k,r['title']);f=[]
        if k=='p0294_1': g=['public-debt',PB]; w='sinking fund deposit account'
        out.append(dict(key=r['key'],topics=t,tags=g,flags=f,why=w))
    json.dump(out,open('results/b%02d.json'%b,'w'),ensure_ascii=False,indent=1)
    print(b,len(d),len(out),sum(1 for o in out if o['tags']))
