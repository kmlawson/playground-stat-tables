import json
ED=['korea-tokanfu-1908','korea-tokanfu-1913','korea-tokanfu-1919','korea-tokanfu-1939']
P='korea-tokanfu-1913/'
add={
'justice':{
 'Civil suits, first instance':['p0247_1'],'Civil suits by amount in dispute':['p0255_1'],
 'Civil appeals':['p0253_1'],'Conciliation cases':['p0245_1'],'Payment-order (summary) cases':['p0260_3'],
 'Provisional attachments and dispositions':['p0261_1'],'Compulsory execution cases':['p0262_1'],
 'Civil judicial assistance':['p0268_1'],'Non-contentious cases':['p0267_4'],
 'Registration of commercial companies':['p0273_1'],'Cases received by prosecutors':['p0276_1'],
 "Prosecutors' dispositions":['p0278_1'],'Preliminary examinations':['p0280_1'],
 'Criminal cases, first instance':['p0281_1'],'Length of detention of accused':['p0299_1'],
 'Criminal appeals':['p0295_1'],'Criminal judicial assistance':['p0311_1'],
 'Civil cases, third instance':['p0254_3'],'Civil appeals (kokoku)':['p0260_2'],
 'Real-estate auction cases':['p0267_1'],'Bankruptcy cases':['p0267_2'],
 'Interdiction and disappearance declarations':['p0267_3'],'Notarial cases':['p0268_2'],
 'Fixed-date (certified date) cases':['p0269_1'],'Real estate and ship registration':['p0269_2'],
 'Non-profit corporation registration':['p0271_1'],'Trade name, minor, wife, agent registration':['p0275_1'],
 'Civil dispute conciliation':['p0243_2'],'Criminal first instance, persons by judgment':['p0289_1'],
 'Criminal second instance, judgments':['p0295_2'],'Criminal cases, third instance':['p0296_1'],
 'Criminal third instance, judgments':['p0296_2'],'Criminal appeals (kokoku)':['p0298_1'],
 'Private prosecution cases':['p0298_2'],'Suspended sentences and revocations':['p0302_1'],
},
'prisons':{
 'Prison population':['p0314_1'],'Convict admissions and releases':['p0324_1'],
 'Accused persons admitted and released':['p0342_1'],'Convicts by sentence':['p0319_1'],
 'Sick inmates':['p0352_1'],'New convicts by sentence and term':['p0327_1'],
 'New convicts by number of offences':['p0337_1'],'New convicts by age at entry':['p0338_2'],
 'Prison labour':['p0345_2'],
},
'police':{
 'Police establishments':['p0202_1','p0202_2'],'Theft losses':['p0204_1'],'Theft arrests and recovery':['p0206_1'],
 'Unnatural deaths':['p0212_2'],'Fires':['p0210_1'],'Privately owned firearms':['p0221_2'],
 'Police-regulated trades':['p0222_1'],'Summary-judgment criminal cases':['p0203_2'],
 'Police rescue and relief':['p0218_1'],
}}
new={
'justice':[('Court personnel',['korea-tokanfu-1913/p0243_1','korea-tokanfu-1939/p0206_1']),
 ('Real estate registration by type',['korea-tokanfu-1908/p0062_2','korea-tokanfu-1913/p0270_1']),
 ('Execution of property penalties',['korea-tokanfu-1913/p0306_1','korea-tokanfu-1919/p0232_1']),
 ('Execution of corporal penalties',['korea-tokanfu-1908/p0067_2','korea-tokanfu-1913/p0310_1','korea-tokanfu-1919/p0233_1'])],
'prisons':[('Work bonuses paid on release',['korea-tokanfu-1913/p0351_1','korea-tokanfu-1939/p0237_1'])],
'police':[('Fires by month',['korea-tokanfu-1913/p0211_1','korea-tokanfu-1919/p0195_2']),
 ('Fire brigades',['korea-tokanfu-1913/p0212_1','korea-tokanfu-1919/p0195_3'])]}
for k in add:
    fn=f'families/korea-tokei--{k}.json'
    d=json.load(open(fn,encoding='utf-8'))
    used={m for f in d['families'] for m in f['members']}
    n=0
    for f in d['families']:
        ids=add[k].get(f['label'])
        if not ids: continue
        for i in ids:
            m=P+i
            assert m not in used,m
            f['members'].append(m);used.add(m);n+=1
        f['members'].sort(key=lambda s:ED.index(s.split('/')[0]))
    miss=set(add[k])-{f['label'] for f in d['families']}
    assert not miss,miss
    nf=0
    for lab,mem in new[k]:
        for m in mem: assert m not in used or m.startswith(P) is False or True
        d['families'].append({'label':lab,'members':mem,'note':''});nf+=1;n+=sum(1 for m in mem if m.startswith(P))
    json.dump(d,open(fn,'w',encoding='utf-8'),ensure_ascii=False,indent=1)
    print(k,len(d['families']),'families; new fams',nf,'added',n)
