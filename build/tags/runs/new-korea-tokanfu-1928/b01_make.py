import json
d=json.load(open('batches/b01.json'))
G=['geography']
m={
'p0011_1':(G,['land-area']),'p0011_2':(['government','geography'],['administrative-divisions','land-area']),
'p0011_3':(['government'],['administrative-divisions']),
'p0012_1':(['agriculture','geography'],['land-area']),'p0012_2':(['agriculture','geography'],['land-area']),
'p0012_3':(['agriculture','geography'],['land-area','land-tax']),
'p0013_1':(['agriculture','economy'],['prices']),'p0015_1':(['agriculture','economy'],['prices','land-tenure']),
'p0021_4':(['disasters','geography'],['earthquakes-and-volcanoes']),
'p0022_1':(['population'],['population-totals','households']),
'p0022_2':(['population'],['population-totals','households','administrative-divisions']),
'p0027_1':(['population'],['population-totals','households']),
'p0030_1':(['population'],['nationality-and-ethnicity','migration']),
'p0031_1':(['population'],['nationality-and-ethnicity']),
'p0033_1':(['population','labour'],['occupations','households']),
'p0037_1':(['population'],['nationality-and-ethnicity','age-and-sex']),
'p0038_1':(['population'],['births-and-deaths','marriage-and-divorce']),
'p0039_1':(['population'],['marriage-and-divorce','age-and-sex']),
'p0039_2':(['population'],['births-and-deaths','marriage-and-divorce']),
'p0040_1':(['population'],['births-and-deaths']),'p0041_1':(['population'],['births-and-deaths']),
'p0043_1':(['population'],['births-and-deaths']),
'p0045_1':(['population','health'],['births-and-deaths','diseases']),
'p0050_1':(['population','health'],['births-and-deaths','diseases']),
'p0051_1':(['population','health'],['births-and-deaths','diseases','age-and-sex']),
'p0053_1':(['foreign-relations','population'],['passports-and-travel-permits']),
}
out=[]
for r in d:
    k=r['key'].split(':')[1]
    if k in m: t,g=m[k]
    else: t,g=G,['weather']
    out.append(dict(key=r['key'],topics=t,tags=g,flags=[],why=r['en']['t'][:60]))
json.dump(out,open('results/b01.json','w'),ensure_ascii=False,indent=1)
print(len(out))
