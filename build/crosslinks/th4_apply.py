import json
S='korea-tokanfu-1922-4/'
ORD={'1908':0,'1913':1,'1919':2,'1922':3,'1939':4}
def ed(m): return ORD[m.split('-')[2][:4]]
PLAN={
'korea-tokei--railways':{
 'Railway lines':['p0025_1'],'Train and vehicle operations':['p0026_2'],
 'State railway passenger and freight traffic':['p0027_1'],'State railway transport revenue':['p0027_2'],
 'Through traffic':['p0028_1'],'Principal freight by commodity':['p0029_1'],'Traffic by station':['p0030_1'],
 'Railway construction costs':['p0035_1'],'Railway repair costs':['p0037_1'],
 'Railway revenue and expenditure':['p0037_2'],'State railway investment':['p0037_3'],
 'Railway hotels':['p0038_1'],'Railway warehouses':['p0038_2'],'Railway casualties':['p0039_1'],
 'Railway law offences':['p0040_1'],
 'Private railways and tramways, capital':['p0040_3'],'Private railways and tramways, traffic':['p0041_1'],
 'Private railways, construction costs':['p0042_1'],'Private railways and tramways, revenue and expenditure':['p0044_1']},
'korea-tokei--communications':{
 'Post offices and communication facilities':['p0049_1'],'Ordinary mail':['p0050_1'],'Parcel post':['p0051_1'],
 'Postal money orders':['p0051_2','p0052_1'],'Postal savings accounts':['p0053_1'],
 'Postal savings deposits':['p0053_2'],'Securities through post offices':['p0053_3'],
 'Postal transfer savings':['p0054_1'],'Telegraph lines':['p0055_1'],'Telegrams':['p0055_2'],
 'Telephone lines':['p0057_1'],'Telephone calls':['p0057_2','p0058_1']},
'korea-tokei--public-works-and-shipping':{
 'Navigation marks':['p0046_1'],'Ships':['p0046_2'],'Government-ordered shipping routes':['p0047_1'],
 'Pusan-Shimonoseki ferry fleet':['p0047_2'],'Pusan-Shimonoseki ferry traffic':['p0047_3'],
 'Road construction, Government-General works':['p0061_2'],'Road construction, local-funds works':['p0062_1'],
 'Local civil engineering expenditure':['p0062_2'],'Waterworks':['p0063_1'],
 'Treasury subsidies for local civil engineering':['p0064_1'],'Harbour works':['p0064_2'],'Flood damage':['p0065_1']}}
for n,plan in PLAN.items():
    p=f'families/{n}.json'; d=json.load(open(p)); cnt=0
    ids={l.split('|')[1].strip() for l in open(f'listings/{n}.txt') if l.startswith('korea-tokanfu-1922-4')}
    byl={f['label']:f for f in d['families']}
    for lab,ts in plan.items():
        f=byl[lab]
        assert not any(m.startswith('korea-tokanfu-1922') for m in f['members']),lab
        for t in ts:
            assert t in ids,t
            m=S+t; i=len(f['members'])
            for j,x in enumerate(f['members']):
                if ed(x)>3: i=j;break
            f['members'].insert(i,m); cnt+=1
    json.dump(d,open(p,'w'),ensure_ascii=False,indent=1)
    json.load(open(p)); print(n,len(d['families']),cnt)
