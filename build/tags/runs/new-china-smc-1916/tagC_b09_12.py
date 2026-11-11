import json
F='finance'; PB='public-budgets'; PP='public-property'; PD='public-debt'; TX='taxation'
def s(t,g,w=''): return (t,g,w)
R={}
R['09']={0:s([F,'government'],[PB]),1:s([F],[PB]),2:s([F],[PB]),3:s([F,'welfare'],[PB,'charitable-institutions']),
4:s([F,'crime-and-justice'],[PB,'police']),5:s([F,'health'],[PB,'public-health']),6:s([F],[PB]),7:s([F,'education'],['education-finance',PB]),
8:s([F],[PD,PB]),9:s([F],[PD]),10:s([F],[PB,PD]),11:s([F],[PB]),12:s([F,'transportation'],[PB,'roads-and-bridges']),
13:s([F,'utilities'],[PB,'river-conservancy']),14:s([F,'utilities'],[PB,'water-and-sewerage']),15:s([F,'transportation'],[PB,'ports']),
16:s([F],[PB,PP]),17:s([F],[PB,PP]),18:s([F,'transportation'],[PB,'roads-and-bridges']),19:s([F],[PB]),20:s([F],[PD]),21:s([F],[PP]),22:s([F],[PB]),
23:s([F,'crime-and-justice'],['prison-labour','prisons']),24:s([F,'crime-and-justice'],['prison-labour','prisons']),
25:s([F,'manufacturing'],['cement-and-bricks']),26:s([F,'manufacturing'],['cement-and-bricks']),27:s([F,'mining'],[]),28:s([F,'mining'],[]),
29:s([F,'manufacturing'],[]),30:s([F,'manufacturing'],[]),31:s([F,'manufacturing'],[]),32:s([F,'crime-and-justice'],['police']),
33:s([F,'religion'],['religious-institutions']),34:s([F],[PP]),35:s([F],[PP]),36:s([F],[PP]),37:s([F],[PB]),
38:s([F,'trade'],[TX,'tariffs']),39:s([F],[TX])}
R['10']={0:s([F,'health'],[TX,'food-inspection']),1:s([F,'health'],[TX,'food-inspection']),2:s([F,'health'],[TX]),3:s([F,'health'],[TX]),
4:s([F,'trade'],[TX,'markets-and-exchanges']),5:s([F,'government'],[TX]),6:s([F],[TX,'land-tax']),7:s([F],[TX,PB]),8:s([F],[TX,PB]),
9:s([F],[TX,'advertising']),10:s([F],[TX,'customs-revenue']),11:s([F],[TX]),12:s([F,'trade'],[PP,'markets-and-exchanges']),
13:s([F],[PP,'firefighting']),14:s([F],[PP]),15:s([F,'utilities'],[PB,'securities-and-investment']),
16:s([F,'military'],[PB,'militias-and-volunteer-forces']),17:s([F,'military'],[PB,'militias-and-volunteer-forces']),18:s([F,'military'],[PB,'militias-and-volunteer-forces']),
19:s([F,'disasters'],[PB,'firefighting']),20:s([F,'disasters'],[PB,'firefighting'])}
for i in range(21,27): R['10'][i]=s([F,'crime-and-justice'],[PB,'police'])
R['10'].update({27:s([F,'health'],[PB,'public-health']),28:s([F,'health'],['epidemics','public-health']),29:s([F,'health'],['public-health']),30:s([F,'health'],[PB,'public-health'])})
for i in range(31,38): R['10'][i]=s([F,'health'],['medical-services',PB])
R['10'][38]=s([F,'health'],['medical-services','wages']); R['10'][39]=s([F,'health'],['medical-services'])
R['11']={0:s([F,'health'],[PB,'public-health']),1:s([F,'health'],[PB,'recreation-and-amusements']),2:s([F,'health'],['medical-services']),3:s([F,'health'],[PB,'medical-services']),
4:s([F],[PB]),5:s([F],[PB,PP]),6:s([F,'crime-and-justice'],[PB,'police']),7:s([F,'health'],[PB,'medical-services']),8:s([F],[PB,PP]),9:s([F,'education'],['education-finance',PB]),
10:s([F,'utilities'],[PB,'river-conservancy']),11:s([F,'utilities'],[PB,'water-and-sewerage']),12:s([F,'transportation'],[PB,'roads-and-bridges']),13:s([F,'transportation'],[PB,'roads-and-bridges']),14:s([F,'transportation'],[PB,'roads-and-bridges']),
15:s([F,'utilities'],['electricity','gas']),16:s([F,'culture'],[PB,'recreation-and-amusements']),17:s([F],[PB]),18:s([F,'culture'],[PB,'arts-and-music']),19:s([F,'education'],[PB,'libraries'])}
for i in range(20,36): R['11'][i]=s([F,'education'],['education-finance'] + (['teachers'] if i%2==0 and i<36 and i not in(21,23,25,27,29,31,33,35) else []))
R['11'][36]=s([F,'education'],['education-finance'])
for i in (37,38,39): R['11'][i]=s([F,'government'],[PB])
R['12']={0:s([F,'government'],[PB]),1:s([F,'government'],[PB]),2:s([F],[PB]),3:s([F],[PB]),4:s([F,'welfare'],[PB,'charitable-institutions']),5:s([F],[PP]),6:s([F],[PD]),7:s([F],[PD]),
8:s([F],[PB,PD]),9:s([F],[PB]),10:s([F,'transportation'],[PB,'roads-and-bridges']),11:s([F,'utilities'],[PB,'river-conservancy']),12:s([F,'utilities'],[PB,'water-and-sewerage']),13:s([F,'transportation'],[PB,'ports']),
14:s([F],[PP,'firefighting']),15:s([F,'health'],[PP,'public-health']),16:s([F],[PP]),17:s([F,'culture'],[PP,'recreation-and-amusements']),18:s([F,'education'],[PP,'education-finance']),19:s([F],[PP]),20:s([F],[PP]),
21:s([F],[PP,'firefighting']),22:s([F],[PP,'police']),23:s([F,'health'],[PP,'public-health']),24:s([F],[PP]),25:s([F,'education'],[PP,'education-finance']),26:s([F,'transportation'],[PB,'roads-and-bridges']),27:s([F],[PB])}
voc=json.load(open('../../vocabulary.json')); T={t['id'] for t in voc['topics']}; G={t['id'] for t in voc['tags']}
for b in R:
    d=json.load(open(f'batches/b{b}.json')); out=[]
    assert len(d)==len(R[b]),(b,len(d),len(R[b]))
    for i,r in enumerate(d):
        t,g,_=R[b][i]; assert set(t)<=T and set(g)<=G,(b,i,t,g)
        out.append({'key':r['key'],'topics':t,'tags':g[:3],'flags':[],'why':'municipal accounts: '+r['title'][-60:]})
    json.dump(out,open(f'results/b{b}.json','w'),ensure_ascii=False,indent=1)
    print(b,len(out),sum(1 for o in out if o['tags']))
