import json
P='korea-tokanfu-1922-5/'
def run(name, add, new):
    fn=f'families/korea-tokei--{name}.json'
    d=json.load(open(fn))
    by={f['label']:f for f in d['families']}
    for lab,ids in add.items():
        m=by[lab]['members']
        for i in ids:
            # insert before 1939 members
            pos=len(m)
            for k,x in enumerate(m):
                if x.startswith('korea-tokanfu-1939'): pos=k;break
            m.insert(pos,P+i)
    for lab,mem in new:
        d['families'].append({'label':lab,'members':mem,'note':''})
    json.dump(d,open(fn,'w'),ensure_ascii=False,indent=1)
    json.load(open(fn))
    print(name,len(d['families']),sum(len(f['members']) for f in d['families']))
run('police',{
'Police establishments':['p0007_1'],'Theft losses':['p0020_1'],'Theft arrests and recovery':['p0021_1'],
'Arrests by offence':['p0015_1'],'Unnatural deaths':['p0023_2'],'Fires':['p0022_1'],
'Privately owned firearms':['p0029_1'],'Police-regulated trades':['p0030_1'],
'Summary-judgment criminal cases':['p0018_2'],'Summary judgments: persons sentenced':['p0019_1'],
'Suicides by age and cause':['p0024_1'],'Abandoned children':['p0026_1'],'Police rescue and relief':['p0027_1'],
'Fires by month':['p0022_2'],'Fire brigades':['p0023_1']},
[('Crimes and arrests by province',['korea-tokanfu-1922-5/p0018_1','korea-tokanfu-1939/p0185_2']),
 ('Disposition of arrested criminal cases',['korea-tokanfu-1922-5/p0008_1','korea-tokanfu-1939/p0186_1']),
 ('Fires by cause',['korea-tokanfu-1922-5/p0022_3','korea-tokanfu-1939/p0189_3']),
 ('Ships in distress',['korea-tokanfu-1919/p0194_3','korea-tokanfu-1922-5/p0021_2'])])
run('public-health',{
'Health facilities':['p0033_1'],'Infectious disease cases and deaths':['p0034_1'],
'Infectious disease by age and disease':['p0040_1'],'Vaccination':['p0045_1'],
'Government hospital staff and expenses':['p0048_2','p0049_1'],'Hospital patients':['p0050_1'],
'Provincial hospital itinerant clinics':['p0054_1'],'Quarantine of vessels':['p0055_1'],
'Infectious disease cases and deaths by month':['p0042_1'],'Health examinations':['p0043_1']},[])
