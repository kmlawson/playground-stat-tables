import json
P='korea-tokanfu-'
def ed(m):
    s=m.split('/')[0].replace(P,'')
    return {'1908':0,'1913':1,'1919':2,'1922':3,'1928':4,'1939':5}[s[:4]]
def run(name,add,new):
    fn=f'families/korea-tokei--{name}.json'
    d=json.load(open(fn))
    placed={m for f in d['families'] for m in f['members']}
    labels={f['label']:f for f in d['families']}
    cnt=0
    def full(x): return x if x.startswith(P) else P+x
    for lab,ms in add.items():
        f=labels[lab]
        for m in ms:
            m=full(m); assert m not in placed; placed.add(m); f['members'].append(m); cnt+=1
        f['members']=sorted(f['members'],key=ed)
    for lab,ms in new.items():
        ms=[full(m) for m in ms]
        for m in ms: assert m not in placed; placed.add(m)
        d['families'].append({'label':lab,'members':sorted(ms,key=ed),'note':''}); cnt+=len(ms)
    json.dump(d,open(fn,'w'),ensure_ascii=False,indent=1)
    json.load(open(fn))
    print(name,len(d['families']),cnt)
run('population',{
'Resident households and population':['1928/p0022_1'],
'Population by locality':['1928/p0022_2'],
'Resident Japanese by domicile':['1928/p0030_1'],
'Resident foreigners by nationality':['1928/p0031_1'],
'Residents by occupation':['1928/p0033_1'],
'Population by race, percentage':['1928/p0037_1'],
'Births and deaths':['1928/p0038_1'],
'Marriages by age':['1928/p0039_1'],
'Vital statistics ratios':['1928/p0039_2'],
'Births by month':['1928/p0040_1'],
'Deaths by cause':['1928/p0045_1'],
'Deaths by cause and age':['1928/p0051_1'],
'Overseas passports issued':['1928/p0053_1'],
'Overseas travellers':['1928/p0054_1'],
},{
'Deaths by month':['1913/p0043_1','1913/p0051_1','1913/p0057_2','1928/p0043_1'],
'Deaths by cause and month':['1913/p0043_2','1913/p0051_2','1928/p0050_1'],
})
L=['Mean atmospheric pressure','Mean temperature','Mean maximum temperature','Mean minimum temperature','Extreme maximum temperature','Extreme minimum temperature','Humidity','Wind velocity','Rainfall and snowfall','Cloudiness','Days of rain and snow','Days by weather type','Seasons of frost and snow','Wind direction']
ids=['p0017_1','p0017_2','p0018_1','p0018_2','p0019_1','p0019_2','p0019_3','p0019_4','p0020_1','p0020_2','p0020_3','p0021_1','p0021_2','p0021_3']
add={l:['1928/'+i] for l,i in zip(L,ids)}
add.update({'Position and area of Korea':['1928/p0011_1'],'Administrative divisions by province':['1928/p0011_2'],'Jurisdictions of the provinces':['1928/p0011_3'],'State-owned land':['1928/p0012_1'],'Privately owned land':['1928/p0012_3','1928/p0012_2'],'Land sale and rental prices':['1928/p0013_1','1928/p0015_1']})
run('land-and-climate',add,{'Earthquakes':['1919/p0032_2','1928/p0021_4']})
run('public-health',{
'Health facilities':['1928/p0202_1'],
'Infectious disease cases and deaths':['1928/p0203_1'],
'Infectious disease fatality rates':['1928/p0208_1'],
'Infectious disease by age and disease':['1928/p0210_1'],
'Vaccination':['1928/p0215_1'],
'Government hospital staff and expenses':['1928/p0217_1','1928/p0217_2'],
'Hospital patients':['1928/p0219_1'],
'Provincial hospital itinerant clinics':['1928/p0221_1'],
'Quarantine of vessels':['1928/p0222_1'],
'Infectious disease cases and deaths by month':['1928/p0212_1'],
'Health examinations':['1928/p0213_1'],
},{'Infectious disease by occupation':['1922-5/p0039_1','1928/p0209_1','1939/p0198_1']})
