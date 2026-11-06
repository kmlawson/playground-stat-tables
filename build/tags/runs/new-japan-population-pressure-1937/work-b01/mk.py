import json
B='/Users/kml/shell/projects/yearbooks/japanyearbooks/stat-tables-site/build/tags/runs/new-japan-population-pressure-1937/'
P='population'
T={
'p0026_1':([P],['population-totals'],'estimated population by early period'),
'p0027_1':([P],['population-totals'],'estimated population early times to Tokugawa, with authorities'),
'p0028_1':([P],['population-totals'],'population Japan and Europe c.1580'),
'p0030_1':([P],['population-totals','age-and-sex'],'Tokugawa census population by sex'),
'p0032_1':([P],['population-totals'],'19th c. population Japan vs Western nations'),
'p0033_1':([P],['population-totals'],'clan population growth rates'),
'p0036_1':(['disasters',P],['disaster-losses'],'frequency of calamities, Tokugawa'),
'p0047_1':(['economy'],['economic-indicators','companies'],'economic development indicators 1894-1930'),
'p0050_1':(['government'],['elections-and-parties'],'electoral campaign expenses'),
'p0051_1':(['government'],['elections-and-parties','age-and-sex'],'age of Diet members'),
'p0058_1':([P],['births-and-deaths'],'births and birth rate Chiba'),
'p0076_1':([P],['census-and-survey-methods','population-totals'],'population statistic types by year'),
'p0076_2':([P],['household-registration','census-and-survey-methods'],'domicile population excess/deficit'),
'p0080_1':([P],['population-totals','age-and-sex'],'preliminary 1935 empire population, sex ratio'),
'p0081_1':([P,'geography'],['population-totals','land-area'],'area, population, density of empire 1930'),
'p0081_2':([P],['nationality-and-ethnicity'],'nativity/nationality of population 1930'),
'p0082_1':([P],['population-totals'],'population trend 1872-1935'),
'p0083_1':([P],['population-totals'],'annual increase rate and index'),
'p0085_1':([P],['population-totals'],'growth Japan vs Western nations'),
'p0086_1':([P,'geography'],['population-totals','land-area'],'area, population, density by country'),
'p0087_1':([P],['administrative-divisions'],'regions and prefectures list'),
'p0088_1':([P],['administrative-divisions'],'regions and prefectures list'),
'p0088_2':([P],['population-totals'],'regional population 1881-85 vs 1927-31'),
'p0089_1':([P],['migration'],'birthplace classification'),
'p0090_1':([P],['migration'],'net immigration gain by prefecture'),
'p0092_1':([P],['administrative-divisions'],'community classification definitions'),
'p0093_1':([P],['local-government'],'local units by community size'),
'p0094_1':([P],['population-totals'],'population by community size'),
'p0095_1':([P],['population-totals'],'urban/rural increase by community class'),
'p0096_1':([P],['population-totals'],'urban/rural increase periods'),
'p0096_2':([P],['population-totals'],'increase in industrial centres'),
'p0098_1':([P],['age-and-sex'],'age distribution city vs non-city'),
'p0098_2':([P],['births-and-deaths','marriage-and-divorce'],'vital rates great cities'),
'p0100_1':([P,'labour'],['occupations'],'occupational distribution 1930'),
'p0101_1':([P,'labour'],['occupations'],'occupational distribution 1872-6'),
'p0102_1':([P,'labour'],['occupations','age-and-sex'],'occupations workers/dependents by sex'),
'p0103_1':([P,'labour'],['occupations'],'occupations 1872,1920,1930'),
'p0106_1':([P,'labour'],['occupations'],'occupational distribution international'),
'p0107_1':([P,'labour'],['occupations'],'workers per 100 population, international'),
'p0111_1':([P],['age-and-sex'],'sex ratio by community size'),
}
d=json.load(open(B+'batches/b01.json'))
out=[]
for r in d:
    t,g,w=T[r['key'].split(':')[1]]
    out.append({'key':r['key'],'topics':t,'tags':g,'flags':[],'why':w})
v=json.load(open('/Users/kml/shell/projects/yearbooks/japanyearbooks/stat-tables-site/build/tags/vocabulary.json'))
ids={x['id'] for x in v['tags']}|{x['id'] for x in v['topics']}
for o in out:
    assert all(i in ids for i in o['topics']+o['tags']),o
assert len(out)==len(d)
import os; os.makedirs(B+'results',exist_ok=True)
json.dump(out,open(B+'results/b01.json','w'),ensure_ascii=False,indent=1)
print(len(out),sum(1 for o in out if o['tags']))
