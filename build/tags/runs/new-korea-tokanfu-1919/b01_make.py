import json
d=json.load(open('batches/b01.json'))
W=['weather']
m={
'p0015_1':(['geography'],['land-area'],'extreme points and area'),
'p0015_2':(['government','geography'],['administrative-divisions','land-area'],'provincial divisions, area'),
'p0015_3':(['government'],['administrative-divisions'],'provincial jurisdictions'),
'p0016_1':(['agriculture','geography'],['land-tenure'],'state-owned land'),
'p0017_1':(['agriculture','finance'],['land-tenure','land-tax'],'private taxable land'),
'p0017_2':(['agriculture','geography'],['land-tenure','land-tax'],'private tax-exempt land'),
'p0018_1':(['agriculture','economy'],['land-tenure','real-estate'],'land sale prices'),
'p0021_1':(['agriculture','economy'],['land-tenure','real-estate'],'land rental prices'),
'p0032_2':(['geography'],['earthquakes-and-volcanoes'],'earthquake counts'),
'p0057_1':(['population'],['nationality-and-ethnicity','age-and-sex'],'race and sex ratios'),
'p0057_2':(['population'],['births-and-deaths','marriage-and-divorce'],'vital events'),
'p0059_1':(['population'],['births-and-deaths'],'vital rate ratios'),
'p0059_2':(['population'],['births-and-deaths'],'births by month'),
'p0062_1':(['population','health'],['births-and-deaths','diseases'],'deaths by cause'),
'p0064_1':(['population','health'],['births-and-deaths','diseases','age-and-sex'],'deaths by cause and age'),
'p0067_1':(['population'],['marriage-and-divorce','age-and-sex'],'marriages by age'),
'p0067_2':(['population','government'],['passports-and-travel-permits'],'passports issued'),
'p0067_3':(['population'],['migration','overseas-communities'],'overseas travellers'),
'p0068_1':(['transportation','population'],['shipping','migration'],'ferry passengers'),
'p0069_1':(['agriculture'],['arable-land'],'cultivated area'),
'p0033_1':(['population'],['population-totals','households','nationality-and-ethnicity'],'population by year'),
'p0033_2':(['population'],['population-totals','nationality-and-ethnicity','households'],'population by city/county'),
'p0040_1':(['population'],['population-totals','households','nationality-and-ethnicity'],'urban population'),
'p0047_1':(['population'],['migration','nationality-and-ethnicity'],'Japanese by prefecture of origin'),
'p0049_1':(['population'],['nationality-and-ethnicity','population-totals'],'foreigners by nationality'),
'p0051_1':(['population'],['occupations','households'],'by occupation'),
'p0026_1':(['geography'],W,'pressure'),
'p0029_1':(['geography'],W,'humidity'),
'p0029_2':(['geography'],W,'wind'),
'p0030_1':(['geography'],W,'rain/snow'),
'p0030_2':(['geography'],W,'cloud'),
'p0030_3':(['geography'],W,'rain/snow days'),
'p0031_1':(['geography'],W,'weather days'),
'p0031_2':(['geography'],W,'frost snow seasons'),
'p0032_1':(['geography'],W,'wind direction'),
}
out=[]
for r in d:
    k=r['key'].split(':')[1]
    if k in m: t,g,w=m[k]
    elif r['chapter'].startswith('2'): t,g,w=['geography'],W,'temperature'
    else: raise Exception(k)
    out.append(dict(key=r['key'],topics=t,tags=g,flags=[],why=w))
json.dump(out,open('results/b01.json','w'),ensure_ascii=False,indent=1)
print(len(out),sum(1 for o in out if o['tags']))
