import json,re
def cls(r):
    t=r['title']; k=r['key'].split(':')[1]; ch=r['chapter'] or ''; tl=t.lower(); fl=[]
    T=['finance'];G=[];w=''
    def has(*a): return any(x in tl for x in a)
    if k in('p0008_1','p0008_2','p0008_3'):
        return ['military','government'],['militias-and-volunteer-forces'],['text-tables'],'volunteer corps roster'
    if ch.startswith('Watch — Volunteer'):
        return ['military'],['militias-and-volunteer-forces','arms-and-arsenals'] if k!='p0010_1' or 1 else [],[],'volunteer arms/ammunition inventory'
    if k=='p0013_1': return ['finance'],['public-debt'],[],'debenture allotments'
    if k=='p0014_1': return ['finance'],['public-budgets'],[],'receipts and expenditure statement'
    if k=='p0015_1': return ['finance'],['public-budgets'],[],'overspending vs budget'
    if k.startswith(('p0016','p0017','p0018','p0019')): return ['finance','government'],['taxation','local-government'],[],'municipal rate by quarter'
    if k=='p0020_1': return ['finance'],['taxation','real-estate'],[],'land assessment comparison'
    if k in('p0021_1','p0022_1','p0023_1'): return ['finance'],['taxation','real-estate'],[],'house assessments'
    if k=='p0025_1': return ['finance'],['land-registration','taxation'],[],'lots of land assessed'
    if k=='p0029_1': return ['communications'],['postal-services'],[],'local post office report'
    if k in('p0040_1','p0041_1'): return ['crime-and-justice'],['police','offences-and-convictions'],[],'arrests by month'
    if k=='p0042_1': return ['crime-and-justice'],['offences-and-convictions','police'],[],'prisoners by offence'
    if k=='p0043_1': return ['crime-and-justice'],['corporal-punishment','offences-and-convictions'],[],'punishments inflicted'
    if k=='p0047_1': return ['health'],['public-health'],[],'night-soil cart-loads'
    if k.startswith('p0053'): return ['health','agriculture'],['food-inspection','livestock'],[],'animals slaughtered'
    if k=='p0054_1': return ['population','health'],['births-and-deaths','age-and-sex'],[],'age at death'
    if k=='p0055_1': return ['population','health'],['births-and-deaths'],[],'deaths and death rate'
    if k.startswith('p0056'): return ['health','population'],['epidemics','diseases'],[],'cholera'
    if k=='p0062_1': return ['health','population'],['diseases','births-and-deaths'],[],'phthisis deaths'
    if k.startswith(('p0064','p0065')): return ['health','population'],['births-and-deaths','diseases'],[],'deaths by cause'
    if k=='p0077_1': return ['finance','sport'],['recreation-and-amusements'],[],'recreation ground expenditure'
    if k=='p0079_1': return ['population','health'],['births-and-deaths'],[],'burials in cemeteries'
    if k.startswith('p0082'): return ['utilities'],['water-and-sewerage'],[],'drains'
    if k in('p0088_1','p0089_1'): return ['utilities'],['gas'],[],'public lamps'
    if k.startswith(('p0090','p0091')): return ['transportation'],['roads-and-bridges'],[],'road works'
    if k=='p0092_1': return ['transportation','government'],['roads-and-bridges','urban-planning'],['text-tables'],'road extension schemes'
    if k=='p0107_1': return ['culture'],['arts-and-music'],[],'band instruments'
    if k.startswith('p0108'): return ['culture','finance'],['arts-and-music','public-budgets'],[],'band expenditure/estimate'
    if k=='p0112_1': return ['health','finance'],['food-inspection'],[],'slaughter charges'
    if k=='p0140_1': return ['finance','disasters'],['firefighting','public-budgets'],[],'fire dept accounts'
    if k=='p0142_1': return ['finance','disasters'],['firefighting','public-budgets'],[],'fire dept estimate'
    if k=='p0142_2': return ['disasters','government'],['firefighting'],['text-tables'],'fire commission members'
    # finance statements
    topics=['finance','government'] 
    tags=['public-budgets']; w='municipal accounts'
    rules=[('police','police'),('lock hospital','medical-services'),('hospital','medical-services'),('medical','medical-services'),('night-soil','public-health'),('nuisance','public-health'),('sanitary','public-health'),
      ('poor','poor-relief'),('lighting','gas'),('telegraph','telegraph'),('cemeter','public-health'),('drain','water-and-sewerage'),('road','roads-and-bridges'),('bridge','roads-and-bridges'),('landing','ports'),
      ('garden','recreation-and-amusements'),('museum','museums-and-heritage'),('library','libraries'),('orphanage','charitable-institutions'),('education','schools-and-pupils'),('post office','postal-services'),
      ('band','arts-and-music'),('fire','firefighting'),('volunteer','militias-and-volunteer-forces'),('license','taxation'),('rate','taxation'),('land tax','land-tax'),('debenture','public-debt'),('loan','public-debt'),
      ('sinking','public-debt'),('interest','public-debt'),('permit','taxation'),('stud','road-transport'),('market','markets-and-exchanges')]
    for a,b in rules:
        if a in tl and b not in tags and len(tags)<3: tags.append(b)
    if ch.startswith('Finance — Working') or 'fund' in tl or 'liquor' in tl or 'deposit' in tl or 'security' in tl or 'saloons' in tl or 'stable keepers' in tl:
        tags=['public-budgets']
        if 'savings' in tl: tags.append('savings-and-loans')
        if 'liquor' in tl or 'saloons' in tl or 'livery' in tl: tags.append('taxation')
        if 'sinking' in tl: tags=['public-debt','public-budgets']
        if 'post office' in tl: tags.append('postal-services')
    if k=='p0178_1': tags=['public-budgets','real-estate']
    if k in('p0180_1','p0182_1','p0184_1','p0188_1','p0209_1','p0211_1') or 'closing' in tl or 'brought' in tl or 'carried' in tl:
        tags=['public-budgets']
    if k=='p0188_2': return ['finance'],['taxation','road-transport'],[],'licence fees for vehicles'
    if k.startswith('p0165_5') or k=='p0206_7': tags=['public-debt','public-budgets']
    if 'police' in tl and 'pay' in tl: pass
    if len(tags)>3: tags=tags[:3]
    if 'revenue' in tl or 'income' in tl:
        w='municipal revenue'
    # drop public-budgets first when specific tags present? keep up to 3
    return topics,tags,[],w
out={}
for i in range(1,7):
    d=json.load(open('batches/b%02d.json'%i)); res=[]
    for r in d:
        tp,tg,fl,w=cls(r)
        res.append(dict(key=r['key'],topics=tp[:2],tags=tg[:3],flags=fl,why=w))
    assert [x['key'] for x in res]==[r['key'] for r in d]
    json.dump(res,open('results/b%02d.json'%i,'w'),ensure_ascii=False,indent=1)
    print(i,len(res),sum(1 for x in res if x['tags']))
