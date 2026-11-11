import json
V=json.load(open('../../vocabulary.json'))
T={t['id'] for t in V['topics']};G={t['id'] for t in V['tags']}
def L(b): return json.load(open(f'batches/b0{b}.json'))
U=['utilities'];E=['electricity']
out={}
# b05
b=[None]*40
def s(i,t,g,w,f=False): b[i]=(t,g,w,f)
s(0,['labour','utilities'],['employment-and-unemployment'],'men employed on public works')
s(1,['welfare','population'],['work-relief','nationality-and-ethnicity'],'shelter inmates by nationality')
s(2,['welfare'],['work-relief'],'shelter admissions, wood chopped')
s(3,U,['river-conservancy'],'mud removed from creeks')
s(4,U,['gas'],'street gas lamps');s(5,U,E,'street electric lamps')
s(6,U,E+['gas'],'fines unlit lamps')
for i in (7,8,9,10): s(i,U,['construction'],'building permits/work')
s(11,['mining','utilities'],['mineral-production'],'quarry materials');s(12,['mining','utilities'],['mineral-production'],'quarry dispatch')
s(13,['manufacturing'],['cement-and-bricks'],'concreteware')
s(14,['government'],['public-property','real-estate'],'municipal property schedule')
s(15,['transportation','finance'],['roads-and-bridges','real-estate'],'road widening costs')
for i in (16,18,19,20,21,23): s(i,['finance','transportation'],['real-estate','roads-and-bridges'],'land compensation calc')
s(17,['government'],[],'petition signatories',True)
for i in (22,24,25): s(i,['transportation','finance'],['roads-and-bridges','real-estate'],'road improvements compensation')
s(26,['government','crime-and-justice'],['real-estate'],'Land Commission cases list',True)
s(27,U+['agriculture'],['horticulture'],'plants bedded out');s(28,U,[],'paths surfaced')
s(29,U+['agriculture'],['horticulture'],'trees transplanted');s(30,U+['agriculture'],['horticulture'],'turf')
s(31,U+['agriculture'],['horticulture'],'roadside trees');s(32,U,[],'park seats')
s(33,U+['agriculture'],['horticulture'],'nurseries');s(34,U+['agriculture'],['horticulture'],'trees planted')
s(35,['sport','culture'],['sports-participation'],'players by sport')
s(36,['government'],[],'commission members',True)
s(37,U,['construction'],'plans approved')
s(38,U,E,'plant comparison');s(39,U,E,'plant comparison')
out[5]=b
b=[None]*40
FU=['utilities','finance']
for i in range(40): s(i,U,E,'electricity department')
s(0,FU,E,'works costs')
for i in (17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39): s(i,['finance','utilities'],E,'electricity accounts')
s(18,FU,E+['wages'],'pay electricity staff')
out[6]=b
# b07
b=[None]*40
PB=['public-budgets']
s(0,FU,E,'electricity balance sheet');s(1,FU,E+['public-debt'],'loan interest')
for i in (2,3,4,6,7,8,9,10): s(i,['finance','government'],PB,'municipal budget/statement')
s(5,['finance'],PB+['police'],'police pay')
s(11,['finance'],['taxation']+PB,'revenue by head');s(12,['finance'],['land-tax'],'land tax by district')
s(13,['finance'],['taxation','real-estate'],'rates inside limits');s(14,['finance'],['taxation','real-estate'],'rates outside limits')
s(15,['finance'],['taxation','ports'],'wharfage dues');s(16,['finance'],['taxation'],'licence fees')
s(17,['finance','narcotics'],['opium-licensing','taxation'],'opium licence revenue')
s(18,['transportation','finance'],['road-transport','taxation'],'vehicle licences');s(19,['transportation'],['road-transport'],'motor vehicles')
s(20,['finance'],['markets-and-exchanges','taxation'],'market fees');s(21,['finance'],['taxation'],'fruit shop licences')
s(22,['finance'],['taxation','real-estate'],'Chinese rate summary');s(23,['finance'],['taxation','real-estate'],'Chinese houses assessments')
s(24,['finance'],['taxation'],'licence comparison');s(25,['finance'],['taxation'],'licence revenue ten years')
s(26,['finance'],['land-tax']+PB,'land tax estimate/actual');s(27,['finance'],['taxation']+PB,'municipal rate estimate/actual')
s(28,['finance'],PB+['ports'],'wharfage est/actual');s(29,['finance'],['taxation']+PB,'licence est/actual')
s(30,['finance'],['public-property']+PB,'rents est/actual');s(31,['finance'],PB,'undertakings revenue')
for i,t,g in ((32,'military',['militias-and-volunteer-forces']),(33,'military',['militias-and-volunteer-forces']),(34,'disasters',['firefighting']),(35,'disasters',['firefighting']),(36,'crime-and-justice',['police']),(37,'crime-and-justice',['police']),(38,'health',['public-health']),(39,'health',['public-health'])):
    s(i,['finance',t],PB+g,'dept expenditure')
out[7]=b
b=[None]*40
def D(i,t,g): s(i,['finance',t],PB+g,'dept expenditure')
D(0,'health',['public-health']);D(1,'health',['public-health'])
for i in range(2,8): D(i,'health',['medical-services'])
D(8,'health',['public-health']);D(9,'health',[]);D(10,'health',['medical-services']);D(11,'health',[])
s(12,['finance','utilities'],PB,'PWD general')
for i in range(13,18): s(i,['finance','utilities'],PB+['construction'],'PWD buildings')
s(18,['finance','utilities'],PB+['river-conservancy'],'creeks');s(19,['finance','utilities'],PB+['water-and-sewerage'],'drainage')
s(20,['finance','transportation'],PB+['roads-and-bridges'],'roads');s(21,['finance','transportation'],PB+['roads-and-bridges'],'road cleansing')
s(22,['finance','utilities'],PB+E+['gas'],'lighting');s(23,['finance','utilities'],PB+['horticulture'],'parks')
s(24,['finance','utilities'],PB,'PWD stores');s(25,['finance','utilities'],PB,'PWD credit')
s(26,['finance','culture'],PB+['arts-and-music'],'public band');s(27,['finance','education'],PB+['libraries'],'library')
for i in range(28,35): s(i,['education','finance'],['education-finance','schools-and-pupils'],'school expenditure')
s(35,['education','finance'],['education-finance'],'grants in aid')
for i in (36,37,38,39): s(i,['finance','government'],PB,'finance/secretariat expenditure')
out[8]=b
for n,b in out.items():
    ins=L(n);assert len(ins)==len(b)==40
    res=[]
    for r,(t,g,w,f) in zip(ins,b):
        assert set(t)<=T and set(g)<=G and len(t)<=2 and len(g)<=3,(n,r['key'],t,g)
        res.append({'key':r['key'],'topics':t,'tags':g,'flags':['text-tables'] if f else [],'why':w})
    json.dump(res,open(f'results/b0{n}.json','w'),ensure_ascii=False,indent=1)
    print(n,len(res),sum(1 for x in res if x['tags']))
