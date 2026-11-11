import json,re,glob
M='militias-and-volunteer-forces'
def A(t,g=(),f=(),w=''): return (list(t),list(g),list(f),w)
X={}
def s(ids,*a,**k):
    for i in ids.split(): X['p'+i]=A(*a,**k) if not k else A(*a,**k)
TT=['text-tables']
s('0011_1 0012_1 0013_1 0016_1 0023_1 0023_3 0032_2',['military'],[M],w='volunteer corps')
s('0012_2 0021_2 0022_1 0022_2 0022_3 0022_4 0023_2 0032_1',['military'],[M],TT,'volunteer corps roster/list')
s('0013_1',['military','finance'],[M],w='camp costs')
s('0017_1 0033_1',['military','sport'],[M,'sports-records'],TT,'shooting competitions')
s('0021_1',['military'],['arms-and-arsenals'],TT,'rifle classes')
s('0025_1 0060_2',['military'],['arms-and-arsenals'],w='arms and ammunition return')
X['p0060_2']=A(['crime-and-justice','military'],['police','arms-and-arsenals'],[],'police arms return')
s('0034_1 0034_2 0034_3 0034_4 0034_5 0034_6 0034_7',['disasters'],['firefighting'],TT,'fire brigade roster')
s('0035_1',['disasters'],['firefighting'],w='fire brigade equipment')
s('0036_1 0036_2 0036_3 0036_4 0054_1',['disasters'],['fires'],w='fire calls/returns')
s('0037_1 0040_1 0040_2 0041_1 0042_1 0042_2 0042_3 0042_5',['crime-and-justice'],['police'],w='police personnel')
s('0042_4',['crime-and-justice'],['police'],TT,'police ponies list')
s('0039_1 0039_3',['health','crime-and-justice'],['medical-services','police'],w='police sickness')
s('0039_2 0039_4 0039_5',['health','crime-and-justice'],['diseases','police'],w='police diseases')
s('0039_6',['crime-and-justice'],['police','offences-and-convictions'],w='police discipline offences')
s('0044_1 0044_2 0055_1',['crime-and-justice'],['police','offences-and-convictions'],w='police action returns')
s('0045_1 0060_1',['crime-and-justice'],['prisons'],w='prisoners')
s('0045_2',['crime-and-justice','population'],['prisons'],w='prisoners origin')
s('0049_1',['transportation','crime-and-justice'],['road-transport','police'],w='traffic men')
s('0050_1',['transportation'],['road-transport','trams'],w='vehicles')
s('0051_1',['transportation'],['transport-accidents','road-transport'],w='vehicle casualties')
s('0056_1 0057_1 0059_2',['crime-and-justice'],['offences-and-convictions','police'],w='arrests')
s('0058_1 0059_1',['crime-and-justice'],['courts','offences-and-convictions'],w='Mixed Court')
s('0116_1',['geography','population'],['land-area','population-totals'],w='statistical summary')
s('0117_1',['geography'],['weather'],w='meteorology')
s('0119_1 0119_2 0120_1',['health','population'],['births-and-deaths','diseases'],w='deaths by cause')
s('0120_2',['population','health'],['nationality-and-ethnicity','births-and-deaths'],w='deaths by nationality')
s('0120_3',['population','health'],['age-and-sex','births-and-deaths'],w='deaths by age')
s('0121_1',['population','health'],['births-and-deaths'],w='death-rate')
s('0121_2',['population','health'],['births-and-deaths','diseases'],w='Chinese deaths')
s('0122_1',['health'],['epidemics','diseases'],w='notified infectious')
s('0123_1',['health','population'],['diseases','births-and-deaths'],w='infectious deaths')
s('0124_1',['health'],['vaccination'],w='vaccination')
s('0130_1 0130_2',['health'],['epidemics','public-health'],w='plague rats')
s('0133_1',['health'],['diseases','medical-services'],w='lab diagnosis')
s('0133_2 0133_3',['health'],['food-inspection'],w='milk adulteration')
s('0134_1',['health','utilities'],['water-and-sewerage'],w='water analysis')
s('0134_2',['health','utilities'],['gas'],w='gas CO')
s('0136_1 0139_1',['health'],['medical-services','diseases'],w='hospital cases')
s('0137_1',['health'],['medical-services'],w='nursing home')
s('0140_1',['health','crime-and-justice'],['medical-services','prisons'],w='gaol hospital')
s('0143_1',['health','utilities'],['public-health','water-and-sewerage'],w='refuse disposal')
s('0145_1',['health'],['malaria','public-health'],w='mosquito work')
s('0146_1',['health'],['public-health'],TT,'licensed laundries list')
s('0148_1',['health'],['public-health'],w='sanitary work')
s('0149_1 0150_1 0150_2 0151_1 0151_2',['health'],['food-inspection'],TT,'licensed premises list')
s('0151_3 0152_1',['health'],['food-inspection','veterinary-health'],w='slaughter house')
s('0152_2',['economy','trade'],['prices','cost-of-living'],w='prices')
s('0152_3',['trade','finance'],['markets-and-exchanges'],w='market receipts')
s('0153_1',['health','crime-and-justice'],['public-health','offences-and-convictions'],TT,'prosecutions list')
s('0156_1 0156_2',['health','population'],['public-health','births-and-deaths'],w='burials')
s('0165_1',['transportation'],['roads-and-bridges'],w='bridges')
s('0168_1',['geography'],['land-surveys'],w='survey work')
s('0168_2 0168_4 0168_5',['geography'],['land-surveys'],w='survey')
s('0168_3',['finance','geography'],['taxation','land-surveys'],w='lots taxed')
s('0170_1 0170_2',['transportation'],['roads-and-bridges'],w='roads')
s('0170_3 0171_1',['utilities'],[],w='cleansing plant')
s('0171_2 0172_1',['utilities'],['water-and-sewerage'],w='water supply')
X['p0172_1']=A(['disasters','utilities'],['firefighting','water-and-sewerage'],[],'hydrants')
s('0172_2',['labour'],['employment-and-unemployment'],w='labour employed')
s('0172_3',['manufacturing'],['cement-and-bricks'],w='concreteware')
s('0172_4',['transportation'],['roads-and-bridges'],w='road works')
s('0173_1',['crime-and-justice','manufacturing'],['prison-labour'],w='convict labour')
s('0174_1',['utilities'],['electricity'],w='lamps')
s('0175_1',['utilities'],['gas'],w='gas lamps')
s('0175_2 0175_3 0177_1',['utilities'],['construction'],w='buildings')
s('0177_2',['utilities','government'],['construction'],w='permits')
s('0177_3',['utilities'],['water-and-sewerage'],w='drainage')
s('0179_1',['sport','culture'],['sports-participation','recreation-and-amusements'],w='recreation ground')
s('0180_1',['forestry'],[],w='planting')
RE=['economy','transportation']
s('0184_1 0186_1 0197_1 0198_1 0198_2 0201_1 0201_2 0201_3 0202_1 0203_1 0206_1 0206_2 0206_3 0206_4 0207_1 0207_2 0207_3 0207_4 0208_1 0211_1 0211_2 0213_1 0214_1 0214_2 0234_1 0235_1 0236_1 0236_2 0238_1 0238_2',RE,['real-estate','roads-and-bridges'],w='land compensation for road')
X['p0206_2']=A(RE,['real-estate'],TT,'items list'); X['p0206_4']=A(['economy'],[],TT,'list of enclosures')
s('0187_1 0187_3 0187_4 0188_1 0190_1 0190_2',['economy'],['real-estate'],w='nursery land purchase')
s('0187_2 0187_5',['economy'],['real-estate'],TT,'boundaries')
s('0190_3',['economy','finance'],['real-estate','public-property'],w='land sold')
s('0191_1',['finance','economy'],['public-property','real-estate'],w='properties schedule')
s('0194_1 0195_1',['finance','transportation'],['public-budgets','roads-and-bridges'],w='land/road cost')
s('0196_1 0196_2 0196_3',RE,['real-estate','roads-and-bridges'],w='Peking Road lots')
s('0213_2 0217_1 0225_1',RE,['real-estate','roads-and-bridges'],w='road improvement agreements')
s('0240_1 0241_1',['finance'],['public-property'],w='easements/leases')
s('0242_1',['economy'],['real-estate'],TT,'land commission cases')
s('0247_1 0248_1 0249_1 0253_1',['utilities'],['electricity','gas'],w='public lighting')
X['p0249_1']=A(['utilities'],['electricity','gas'],[],'lamps per town'); X['p0253_1']=A(['utilities'],['electricity'],[],'lamp tenders')
s('0254_1 0255_1 0256_1 0256_2 0257_1 0258_1 0258_2 0258_3 0268_1',['utilities'],['electricity'],w='electricity dept')
s('0259_1 0269_1 0269_2 0271_1 0273_1',['utilities','finance'],['electricity','public-budgets'],w='electricity accounts')
s('0260_1 0261_1',['utilities'],['electricity'],w='tenders')
s('0273_2',['utilities','labour'],['electricity','wages'],w='pay')
s('0301_1 0301_2 0302_1 0302_2',['education'],['schools-and-pupils'],w='school')
s('0307_1',['finance','science-and-technology'],['public-budgets'],w='observatory subscriptions')
s('0312_1',['government'],['government-offices'],TT,'staff roster')
s('0320_1',['finance'],['public-budgets','taxation'],w='revenue')
s('0320_2',['finance'],['land-tax','taxation'],w='land tax')
s('0321_1 0321_2',['welfare','finance'],['housing','taxation'],w='houses rated')
s('0321_3 0327_1 0328_1',['finance','welfare'],['taxation','housing'],w='municipal rate')
s('0321_4',['finance','transportation'],['ports'],w='wharfage')
s('0322_1',['finance'],['public-budgets'],w='budget variance')
s('0322_2 0323_2 0329_1',['finance'],['taxation'],w='licences')
s('0323_1',['finance','culture'],['taxation','theatre-and-cinema'],w='theatre licences')
s('0324_1',['finance','transportation'],['taxation','inland-navigation'],w='boat licences')
s('0324_2 0324_3 0324_4 0325_2',['finance','transportation'],['taxation','road-transport'],w='vehicle licences')
s('0325_1',['finance','trade'],['markets-and-exchanges'],w='market receipts')
s('0325_3',['finance'],[],TT,'list of statements')
s('0330_1',['finance'],['public-debt'],w='debentures')
s('0348_2 0369_1',['finance'],['public-debt'],w='debentures')
s('0351_1 0397_1',['finance'],['public-budgets'],w='budget summary')
s('0352_1 0352_2',['finance'],['public-budgets','public-debt'],w='sterling accounts')
s('0353_1 0354_1',['finance'],['public-debt','public-property'],w='balance sheet')
s('0355_1 0355_2 0364_1 0364_2',['finance'],['public-budgets'],w='budget comparison')
s('0356_1',['finance','crime-and-justice'],['public-budgets','police'],w='police fund')
s('0356_2',['finance','religion'],['public-budgets','religious-institutions'],w='gurdwara fund')
s('0357_1 0357_2',['finance','mining'],['public-budgets'],w='quarry accounts')
s('0358_1 0358_2',['finance','crime-and-justice'],['public-budgets','prison-labour'],w='convict labour accounts')
s('0358_3 0358_4',['finance','manufacturing'],['public-budgets','cement-and-bricks'],w='concreteware accounts')
s('0359_1 0361_1 0363_1',['finance'],['public-property'],w='property values')
X['p0359_1']=A(['finance'],['public-property','real-estate'],[],'land values')
s('0364_3',['finance'],['taxation'],TT,'tavern licence classes')
s('0365_1',['finance','trade'],['taxation','tariffs'],w='wharfage tariff')
s('0366_1',['finance'],['taxation'],w='licence fees')
s('0366_2 0367_1 0367_2',['finance','health'],['taxation','food-inspection'],w='slaughterhouse fees')
s('0367_3',['finance','utilities'],['taxation','water-and-sewerage'],w='water fees')
s('0367_4',['finance','trade'],['taxation','markets-and-exchanges'],w='market fees')
s('0367_5',['finance','utilities'],['taxation','construction'],w='permit fees')
s('0367_6',['finance'],['public-budgets'],w='dept comparison')
DEPT=[('Volunteer',['military'],[M]),('Fire Brigade',['disasters'],['firefighting']),('Police',['crime-and-justice'],['police']),
('Health',['health'],['public-health']),('Public Works',['utilities'],[]),('Public Band',['culture'],['arts-and-music']),
('Educational',['education'],['education-finance']),('Secretariat',['government'],[]),('Finance Department',['government'],[]),('General Charges',['government'],[])]
SUB=[('Roads',['transportation'],['roads-and-bridges']),('Bridges',['transportation'],['roads-and-bridges']),('Drainage',['utilities'],['water-and-sewerage']),
('Lighting',['utilities'],['electricity']),('Land Tax',['finance'],['land-tax']),('Licence',['finance'],['taxation']),('Wharfage',['finance'],['ports']),
('Interest',['finance'],['public-debt']),('Redemption',['finance'],['public-debt']),('Debenture',['finance'],['public-debt']),('Hospital',['health'],['medical-services']),
('Landing',['transportation'],['ports'])]
def rule(k,t):
    tt=t.split('—')[0:]; tl=' — '.join(tt)
    tops=['finance'];tags=['public-budgets']
    if re.search(r'Ordinary Receipts|Ordinary Income|Extraordinary (Receipts|Income)',tl):
        for n,a,b in SUB:
            if n in tl: tags=b+['public-budgets']; break
        if 'General Municipal Rate' in tl: tags=['taxation','housing','public-budgets']
        if 'Rent of' in tl: tags=['public-property','public-budgets']
        if 'Contributions' in tl: tags=['public-budgets','companies']
        return tops,tags[:3],'receipts'
    for n,a,b in DEPT:
        if n in tl: tops=['finance']+a; tags=b+['public-budgets']; break
    else:
        pass
    sub=tl.split('Ordinary Expenditure')[-1] if 'Ordinary Expenditure' in tl else tl.split('Payments')[-1]
    for n,a,b in SUB:
        if n in sub and n not in('Licence','Land Tax','Wharfage'):
            tags=(b+tags) ; 
            if a[0] not in tops and len(tops)<2: tops.append(a[0])
            break
    if 'Extraordinary' in tl and 'Land' in tl.split('Extraordinary')[-1][:20]: tags=['real-estate','public-budgets']
    if 'Buildings' in tl.split('Extraordinary')[-1][:20]: tags=['construction','public-budgets']
    if 'Parks' in tl and 'Extraordinary' in tl: tops=['finance','utilities']
    out=[]
    for x in tags:
        if x not in out: out.append(x)
    return tops[:2],out[:3],'dept expenditure'
res={}
for f in sorted(glob.glob('batches/b*.json')):
    d=json.load(open(f)); o=[]
    for r in d:
        k=r['key']; pid=k.split(':')[1]; t=r['title']
        if pid in X: tp,tg,fl,w=X[pid]
        elif re.match(r'(Financial Statement|Municipal Budget|\[Police Force)',t) or pid=='p0378_0':
            tp,tg,w=rule(pid,t); fl=[]
        else: tp,tg,fl,w=['finance'],[],[],'UNMAPPED'; print('UNMAPPED',pid,t)
        o.append({'key':k,'topics':tp,'tags':tg,'flags':fl,'why':w})
    json.dump(o,open('results/'+f.split('/')[-1],'w'),ensure_ascii=False,indent=1)
    res[f]=o
