import json,sys
base='/Users/kml/shell/projects/yearbooks/japanyearbooks/stat-tables-site/build/tags/'
T='text-tables'
E=lambda t,g,f=None,w='':(t,g,[T] if f else [],w)
A={
'b07':{
'p0233_2':E(['education'],['schools-and-pupils'],0,'attendance by month'),
'p0233_3':E(['education'],['schools-and-pupils'],0,'pupil ages'),
'p0234_1':E(['education'],['teachers'],1,'staff allocation'),
'p0234_2':E(['education'],['teachers'],1,'subject teachers'),
'p0235_1':E(['education'],[],1,'exam results names'),
'p0235_2':E(['education'],[],1,'exam results names'),
'p0236_1':E(['education'],[],1,'student association officers'),
'p0237_1':E(['education'],['schools-and-pupils'],0,'roll by term'),
'p0237_2':E(['education'],['schools-and-pupils'],0,'attendance'),
'p0237_3':E(['education'],['schools-and-pupils'],0,'pupil ages'),
'p0278_1':E(['communications','finance'],['telephone'],0,'telephone rates effect on accounts'),
'p0284_1':E(['transportation'],['roads-and-bridges'],1,'road reconstruction order'),
'p0290_1':E(['transportation'],['roads-and-bridges'],1,'road renewals list'),
'p0306_1':E(['transportation'],['road-transport'],0,'omnibus route fees'),
'p0306_2':E(['transportation'],['road-transport'],0,'omnibus fares'),
'p0313_1':E(['crime-and-justice','transportation'],['offences-and-convictions','road-transport'],1,'ricsha breaches penalties'),
'p0313_2':E(['transportation'],['road-transport'],1,'ricsha questionnaire'),
'p0314_1':E(['transportation'],['road-transport'],1,'ricsha conditions by city'),
'p0333_1':E(['utilities'],['water-and-sewerage'],0,'water pumped forecast'),
'p0334_1':E(['utilities','finance'],['water-and-sewerage'],0,'water capital employed'),
'p0334_2':E(['utilities','finance'],['water-and-sewerage'],0,'water working expenses'),
'p0334_3':E(['utilities'],['water-and-sewerage'],0,'meter minimum rates'),
'p0338_1':E(['utilities'],['water-and-sewerage'],0,'meter minimum rates'),
'p0347_1':E(['welfare'],['charitable-institutions'],1,'charity committee members'),
'p0347_2':E(['welfare','population'],['poor-relief','nationality-and-ethnicity'],0,'relief cases by nationality'),
'p0349_1':E(['finance','welfare'],['charitable-institutions'],0,'charity working account'),
'p0350_1':E(['finance','welfare'],['charitable-institutions'],0,'charity estimates'),
'p0353_1':E(['transportation','finance'],['navigation-aids'],0,'semaphore service accounts'),
'p0357_1':E(['culture'],['arts-and-music'],1,'symphonies list'),
'p0357_2':E(['culture'],['arts-and-music'],1,'orchestral works list'),
'p0358_1':E(['culture'],['arts-and-music'],1,'chamber works list'),
'p0359_1':E(['culture'],['libraries'],1,'library committee'),
'p0359_2':E(['culture'],['libraries'],0,'library subscriptions'),
'p0361_1':E(['government'],['government-offices'],1,'municipal staff roster'),
'p0368_1':E(['government'],['government-offices'],1,'PWD staff roster'),
'p0370_1':E(['government'],['government-offices'],1,'electricity staff roster'),
'p0382_1':E(['transportation'],['roads-and-bridges'],1,'bridge works list'),
'p0382_2':E(['government'],['public-property'],1,'building works list'),
'p0382_3':E(['transportation'],['roads-and-bridges'],1,'road works list'),
'p0382_4':E(['utilities'],['water-and-sewerage'],1,'drainage works'),
},
'b08':{
'p0382_5':E(['utilities'],['water-and-sewerage'],0,'sewer lengths'),
'p0382_6':E(['utilities'],['river-conservancy'],1,'bunding works'),
'p0382_7':E(['transportation'],['ports'],1,'landing stages'),
'p0384_1':E(['transportation'],['road-transport'],0,'traffic census'),
'p0388_1':E(['transportation'],['roads-and-bridges'],1,'timber bridge repairs'),
'p0388_2':E(['geography'],['land-surveys'],0,'survey work by year'),
'p0388_3':E(['geography','informal-imperialism'],['land-surveys','foreign-concessions'],0,'plans by consulate'),
'p0389_1':E(['geography','informal-imperialism'],['land-surveys','foreign-concessions'],0,'boundary stones by consulate'),
'p0389_2':E(['finance','geography'],['land-tax'],0,'lots taxed by district'),
'p0389_3':E(['geography'],['land-surveys'],0,'lots revised for area'),
'p0389_4':E(['finance'],['land-tax'],0,'assessed value of land'),
'p0389_5':E(['transportation','geography'],['roads-and-bridges','land-surveys'],0,'lots surveyed for roads'),
'p0390_1':E(['transportation','finance'],['roads-and-bridges','real-estate'],0,'land acquired for roads'),
'p0390_2':E(['government'],['public-property'],1,'properties acquired'),
'p0401_1':E(['transportation'],['roads-and-bridges'],1,'asphalt laid'),
'p0401_2':E(['transportation'],['roads-and-bridges'],1,'asphalt treated roads'),
'p0401_3':E(['transportation'],['roads-and-bridges'],0,'road mileage by type'),
'p0402_1':E(['utilities','transportation'],['roads-and-bridges'],0,'trenches by company'),
'p0402_2':E(['utilities'],['water-and-sewerage'],1,'drains replaced'),
'p0403_1':E(['utilities'],['water-and-sewerage'],0,'sewers laid'),
'p0405_1':E(['utilities'],[],0,'road sweepings cartloads'),
'p0405_2':E(['government','utilities'],[],0,'rolling stock inventory'),
'p0406_1':E(['utilities'],['water-and-sewerage'],0,'municipal water use'),
'p0406_2':E(['utilities'],['water-and-sewerage'],0,'hydrants and mains'),
'p0406_3':E(['labour'],['employment-and-unemployment'],0,'men employed monthly'),
'p0407_1':E(['crime-and-justice'],['prison-labour'],0,'convict labour earnings'),
'p0407_2':E(['welfare','population'],['work-relief','nationality-and-ethnicity'],0,'shelter inmates nationality'),
'p0407_3':E(['welfare'],['work-relief'],0,'shelter admissions and work'),
'p0409_1':E(['transportation'],['river-conservancy'],0,'mud dredged'),
'p0409_2':E(['utilities'],['gas'],0,'gas street lamps'),
'p0410_1':E(['utilities'],['electricity'],0,'electric street lamps'),
'p0410_2':E(['utilities','crime-and-justice'],['electricity','gas'],0,'lamp fines'),
'p0413_1':E(['utilities'],['construction'],0,'building permits'),
'p0413_2':E(['utilities'],['construction'],0,'new buildings'),
'p0413_3':E(['utilities'],['construction'],0,'plans submitted'),
'p0413_4':E(['utilities'],['construction'],0,'permits all purposes'),
'p0415_1':E(['utilities'],['construction'],0,'building inspection work'),
'p0416_1':E(['mining','utilities'],['construction'],0,'quarry materials'),
'p0417_1':E(['trade','utilities'],['prices','construction'],0,'material contract prices'),
'p0418_1':E(['government'],[],1,'plant list'),
}}
voc=json.load(open(base+'vocabulary.json'))
tp={t['id'] for t in voc['topics']};tg={t['id'] for t in voc['tags']}
for b,m in A.items():
    inp=json.load(open(base+'runs/new-china-smc-1922/batches/%s.json'%b))
    out=[]
    for r in inp:
        t,g,f,w=m[r['key'].split(':')[1]]
        assert set(t)<=tp and set(g)<=tg and len(t)<=2 and len(g)<=3
        out.append({'key':r['key'],'topics':t,'tags':g,'flags':f,'why':w})
    assert len(out)==len(m)
    json.dump(out,open(base+'runs/new-china-smc-1922/results/%s.json'%b,'w'),ensure_ascii=False,indent=1)
    print(b,len(out),sum(1 for o in out if o['tags']))
