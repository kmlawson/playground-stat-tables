import json
P='korea-tokanfu-'
def k(y,i): return f'{P}{y}/{i}'
E_ORDER=['1908','1913','1919','1939']
def srt(ms):
    return sorted(ms,key=lambda m:E_ORDER.index(m.split('/')[0][-4:]))  # stable
def A(i): return [k(1913,x) for x in i.split()]
cfg={
'population':{
 'add':{
  'Resident households and population':'p0028_1',
  'Resident Japanese by domicile':'p0033_1',
  'Births and deaths':'p0041_1 p0049_1',
  'Residents by occupation':'p0031_1 p0047_2',
  'Resident foreigners by nationality':'p0055_1',
  'Population by race, percentage':'p0028_2 p0029_1'},
 'new':[
  ('Households and population of principal urban areas',[k(1913,'p0059_1'),k(1919,'p0040_1')],''),
  ('Overseas passports issued',[k(1913,'p0057_4'),k(1919,'p0067_2')],''),
  ('Overseas travellers',[k(1913,'p0057_5'),k(1919,'p0067_3')],'1913 by destination and purpose; 1919 by purpose.'),
  ('Shimonoseki-Pusan ferry passengers',[k(1913,'p0058_1'),k(1919,'p0068_1')],'1908 gives the ferry by month and is not linked.'),
  ('Marriages by age',[k(1913,'p0046_3'),k(1913,'p0053_2'),k(1919,'p0036_x')],'1913 splits Japanese and Koreans.'),
  ('Deaths by cause',[k(1913,'p0042_1'),k(1913,'p0050_1'),k(1913,'p0057_1'),k(1919,'p0062_1')],'1913 splits Japanese, Koreans and foreigners.'),
  ('Deaths by cause and age',[k(1913,'p0045_1'),k(1913,'p0053_1'),k(1919,'p0064_1')],'1913 splits Japanese and Koreans.'),
  ('Births by month',[k(1913,'p0041_3'),k(1913,'p0041_4'),k(1913,'p0049_3'),k(1913,'p0049_4'),k(1913,'p0056_3'),k(1919,'p0059_2')],'1913 splits nationalities and live births/stillbirths.'),
  ('Vital statistics ratios',[k(1913,'p0041_2'),k(1913,'p0049_2'),k(1919,'p0059_1')],'1913 splits Japanese and Koreans.'),
  ('Japanese by age',[k(1908,'p0018_2'),k(1913,'p0029_4')],'1908 broad age groups by locality; 1913 ten-year groups.'),
  ('Japanese settlers\' associations',[k(1908,'p0023_1'),k(1913,'p0034_1')],''),
  ('Foreigners by locality',[k(1908,'p0030_1'),k(1908,'p0030_2'),k(1913,'p0056_1')],'1908 splits households/population and sex.'),
 ]},
'land-and-climate':{
 'add':{
  'Position and area of Korea':'p0018_1',
  'Administrative divisions by province':'p0018_2',
  'State-owned land':'p0196_3',
  'Privately owned land':'p0196_4',
  'Land sale and rental prices':'p0020_3 p0021_1'},
 'new':[('Jurisdictions of the provinces',[k(1913,'p0018_3'),k(1919,'p0015_3')],'')]+[
  (n,[k(1913,a),k(1919,b)],'') for n,a,b in [
  ('Mean atmospheric pressure','p0023_3','p0026_1'),('Mean temperature','p0023_4','p0026_2'),
  ('Mean maximum temperature','p0024_1','p0027_1'),('Mean minimum temperature','p0024_2','p0028_1'),
  ('Extreme maximum temperature','p0024_3','p0028_2'),('Extreme minimum temperature','p0025_1','p0028_3'),
  ('Humidity','p0025_2','p0029_1'),('Wind velocity','p0025_3','p0029_2'),
  ('Rainfall and snowfall','p0026_1','p0030_1'),('Cloudiness','p0026_2','p0030_2'),
  ('Days of rain and snow','p0026_3','p0030_3'),('Days by weather type','p0027_1','p0031_1'),
  ('Seasons of frost and snow','p0027_2','p0031_2'),('Wind direction','p0027_3','p0032_1')]]+[
  ('Meteorological observatories',[k(1908,'p0014_1'),k(1913,'p0023_1')],''),
  ('Storm warning signal stations',[k(1908,'p0014_2'),k(1913,'p0023_2')],'')]},
'public-health':{
 'add':{
  'Health facilities':'p0229_1',
  'Infectious disease cases and deaths':'p0230_1 p0233_1 p0236_2',
  'Infectious disease by age and disease':'p0232_2 p0236_1',
  'Vaccination':'p0237_1 p0238_1',
  'Government hospital staff and expenses':'p0238_2 p0240_1',
  'Hospital patients':'p0239_1 p0241_1',
  'Provincial hospital itinerant clinics':'p0241_2',
  'Quarantine of vessels':'p0242_1'},
 'new':[
  ('Infectious disease cases and deaths by month',[k(1913,'p0231_1'),k(1913,'p0234_1'),k(1913,'p0236_3'),k(1939,'p0199_2')],'1913 splits Japanese, Koreans and foreigners.'),
  ('Infectious disease deaths by age',[k(1913,'p0232_1'),k(1913,'p0235_1'),k(1919,'p0205_1')],'1913 splits Japanese and Koreans.'),
  ('Health examinations',[k(1913,'p0236_5'),k(1919,'p0208_1'),k(1939,'p0200_2')],'1939 covers prostitutes, geisha and waitresses.')]}}
for t,c in cfg.items():
    n=f'korea-tokei--{t}'
    d=json.load(open(f'families/{n}.json'))
    ids={l.split('|')[0].strip()+'/'+l.split('|')[1].strip() for l in open(f'listings/{n}.txt') if l.count('|')>5}
    for f in d['families']:
        if f['label'] in c['add']:
            f['members']=srt(f['members']+A(c['add'][f['label']]))
    missing=set(c['add'])-{f['label'] for f in d['families']}
    assert not missing,missing
    for lab,ms,note in c['new']:
        if any(m.endswith('p0036_x') for m in ms): ms=[m if not m.endswith('p0036_x') else k(1919,'p0067_1') for m in ms]
        f={'label':lab,'members':srt(ms)}
        if note: f['note']=note
        d['families'].append(f)
    seen={}
    for f in d['families']:
        for m in f['members']:
            assert m in ids,(m)
            assert m not in seen,(m,f['label'],seen[m])
            seen[m]=f['label']
    json.dump(d,open(f'families/{n}.json','w'),ensure_ascii=False,indent=1)
    new=[m for m in seen if '1913' in m]
    print(n,len(d['families']),sum(len(f['members']) for f in d['families']),len(new))
