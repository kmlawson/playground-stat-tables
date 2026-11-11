import json
D='/Users/kml/shell/projects/yearbooks/japanyearbooks/stat-tables-site/build/tags/'
v=json.load(open(D+'vocabulary.json'))
T={x['id'] for x in v['topics']}; G={x['id'] for x in v['tags']}
def r(k,t,g,w,f=()): return (k,t,g,list(f),w)
R=[
r('p0091_1',['crime-and-justice'],['police','offences-and-convictions'],'police action returns'),
r('p0092_1',['crime-and-justice'],['offences-and-convictions','police','nationality-and-ethnicity'],'offences by foreigners/Chinese'),
r('p0094_1',['crime-and-justice'],['offences-and-convictions','police'],'apprehended not charged'),
r('p0096_1',['crime-and-justice'],['offences-and-convictions','courts','nationality-and-ethnicity'],'sentences of foreigners'),
r('p0109_1',['health','crime-and-justice'],['diseases','prisons'],'TB deaths in gaol'),
r('p0110_1',['health','crime-and-justice'],['nutrition','prisons'],'gaol dietary'),
r('p0110_2',['health','crime-and-justice'],['nutrition','prisons'],'diet constituents'),
r('p0110_3',['health'],['nutrition'],'standard dietary comparison'),
r('p0110_4',['health','crime-and-justice'],['nutrition','prisons'],'new gaol dietary'),
r('p0110_5',['health'],['nutrition'],'new diet constituents'),
r('p0111_1',['health','crime-and-justice'],['nutrition','prisons','diseases'],'TB dietary'),
r('p0111_2',['health'],['nutrition'],'meals TB diet'),
r('p0111_3',['health'],['nutrition'],'TB diet constituents'),
r('p0116_1',['geography','population'],['land-area','population-totals','weather'],'statistical summary'),
r('p0117_1',['geography'],['weather'],'meteorology'),
r('p0118_1',['population'],['population-totals','nationality-and-ethnicity'],'foreign population by district'),
r('p0121_1',['health','population'],['diseases','births-and-deaths'],'foreign deaths by cause'),
r('p0121_2',['health','population'],['births-and-deaths','infant-mortality','diseases'],'child deaths by cause'),
r('p0122_1',['health','population'],['diseases','births-and-deaths'],'total foreign deaths'),
r('p0122_2',['population'],['births-and-deaths','nationality-and-ethnicity'],'deaths by nationality'),
r('p0122_3',['population'],['births-and-deaths','age-and-sex'],'age at death'),
r('p0123_1',['population','health'],['births-and-deaths'],'death-rate series'),
r('p0124_1',['health','population'],['diseases','births-and-deaths'],'Chinese deaths by disease'),
r('p0125_1',['health','population'],['diseases','births-and-deaths','epidemics'],'infectious deaths series'),
r('p0126_1',['health'],['diseases','public-health'],'notifiable disease list',['text-tables']),
r('p0126_2',['health'],['diseases','epidemics'],'notified diseases monthly'),
r('p0128_1',['health'],['vaccination','public-health'],'vaccinations by station'),
r('p0129_1',['health'],['epidemics','diseases'],'plague incidence'),
r('p0129_2',['health'],['epidemics','diseases','public-health'],'plague prevention work'),
r('p0130_1',['health','population'],['diseases','births-and-deaths'],'deaths reported by year'),
r('p0131_1',['health'],['diseases','public-health'],'laboratory diagnosis'),
r('p0132_1',['health'],['diseases','epidemics'],'typhoid monthly'),
r('p0132_2',['health'],['diseases','nationality-and-ethnicity'],'typhoid by race'),
r('p0134_1',['health'],['veterinary-health','diseases'],'rabies animals classes'),
r('p0135_1',['health'],['veterinary-health','diseases'],'kennels rabies'),
r('p0136_1',['health'],['food-inspection'],'adulteration extent'),
r('p0136_2',['health'],['food-inspection'],'milk samples adulterated'),
r('p0136_3',['health'],['food-inspection'],'adulteration by year'),
r('p0137_1',['health','utilities'],['water-and-sewerage','public-health'],'water analysis'),
r('p0139_1',['health'],['medical-services'],'hospital beds'),
]
R2=[
r('p0139_2',['health'],['diseases','medical-services'],'isolation hospital admissions'),
r('p0140_1',['health'],['medical-services'],'nursing home cases'),
r('p0141_1',['health'],['medical-services'],'nursing home fees'),
r('p0141_2',['health'],['medical-services'],'private nurses'),
r('p0142_1',['health'],['medical-services'],'Indian police admissions by station'),
r('p0142_2',['health'],['diseases','pharmaceuticals'],'syphilis treatment course'),
r('p0143_1',['health'],['medical-services'],'Chinese police admissions'),
r('p0144_1',['health'],['diseases','nutrition'],'beri-beri outbreak'),
r('p0144_2',['health'],['nutrition'],'recruits diet'),
r('p0147_1',['health','crime-and-justice'],['diseases','prisons'],'gaol chest classes TB'),
r('p0147_2',['health','crime-and-justice'],['diseases','prisons'],'mortality chest classes'),
r('p0147_3',['health','crime-and-justice'],['diseases','prisons'],'gaol TB deaths'),
r('p0148_1',['health','crime-and-justice'],['nutrition','prisons'],'gaol dietary'),
r('p0148_2',['health','crime-and-justice'],['nutrition','prisons'],'diet constituents'),
r('p0148_3',['health'],['nutrition'],'comparison dietary'),
r('p0148_4',['health','crime-and-justice'],['nutrition','prisons'],'new dietary'),
r('p0148_5',['health'],['nutrition'],'new diet constituents'),
r('p0149_1',['health','crime-and-justice'],['nutrition','prisons','diseases'],'TB dietary'),
r('p0149_2',['health'],['nutrition'],'meal distribution'),
r('p0149_3',['health'],['nutrition'],'TB diet constituents'),
r('p0149_4',['health'],['nutrition'],'meal composition'),
r('p0150_1',['health'],['nutrition'],'fuel values'),
r('p0151_1',['health'],['nutrition'],'calorie factors'),
r('p0152_1',['health'],['diseases','medical-services'],'police gaol hospitals'),
r('p0152_2',['health'],['medical-services'],'police hospital outpatients'),
r('p0153_1',['health'],['medical-services'],'sanatorium visitors'),
r('p0153_2',['health'],['medical-services'],'sanatorium by department'),
r('p0154_1',['health','government'],['public-health'],'branch health offices list',['text-tables']),
r('p0156_1',['health','utilities'],['public-health','water-and-sewerage'],'house refuse disposal'),
r('p0156_2',['health','utilities'],['public-health'],'refuse disposal series'),
r('p0157_1',['health'],['malaria','public-health'],'mosquito larvae'),
r('p0157_2',['health'],['malaria','public-health'],'anopheles survey'),
r('p0159_1',['health'],['public-health','vaccination'],'sanitary work'),
r('p0159_2',['health','crime-and-justice'],['offences-and-convictions','public-health'],'sanitary prosecutions'),
r('p0160_1',['health','agriculture'],['food-inspection','livestock'],'dairies census'),
r('p0160_2',['health'],['food-inspection','livestock'],'slaughter house animals'),
r('p0161_1',['health'],['food-inspection','veterinary-health'],'rejections'),
r('p0161_2',['health'],['food-inspection','veterinary-health'],'slaughter returns'),
r('p0162_1',['trade'],['markets-and-exchanges'],'municipal markets'),
r('p0162_2',['trade','economy'],['prices','cost-of-living'],'price variation'),
]
for b,R_ in (('b03',R),('b04',R2)):
    inp=json.load(open(D+f'runs/new-china-smc-1922/batches/{b}.json'))
    assert len(inp)==len(R_),(b,len(inp),len(R_))
    out=[]
    for i,x in zip(inp,R_):
        assert i['key']=='china-smc-1922:'+x[0],(i['key'],x[0])
        assert all(t in T for t in x[1]),x
        g=[t for t in x[2] if t in G]
        if len(g)!=len(x[2]): print('drop',x[0],set(x[2])-set(g))
        out.append({'key':i['key'],'topics':x[1],'tags':g,'flags':x[3],'why':x[4]})
    import os; os.makedirs(D+'runs/new-china-smc-1922/results',exist_ok=True)
    json.dump(out,open(D+f'runs/new-china-smc-1922/results/{b}.json','w'),ensure_ascii=False,indent=1)
    print(b,len(out),sum(1 for o in out if o['tags']))
