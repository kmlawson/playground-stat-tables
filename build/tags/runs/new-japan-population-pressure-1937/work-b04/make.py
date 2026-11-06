import json
P='japan-population-pressure-1937:'
D=[
('p0230_2',['population','labour'],['occupations','nationality-and-ethnicity'],'Korean occupations in Japan'),
('p0237_1',['manufacturing','economy'],['industrial-output','electricity','coal'],'coal, power, output index'),
('p0239_1',['trade'],['foreign-trade'],'trade by degree of manufacture'),
('p0240_1',['trade'],['imports'],'imports by commodity'),
('p0241_1',['trade'],['exports'],'exports by commodity'),
('p0250_1',['manufacturing','labour'],['industrial-output','women-workers'],'factories and operatives by sex'),
('p0251_1',['labour','population'],['age-and-sex','occupations'],'manufacturing workers by age and sex'),
('p0252_1',['labour','manufacturing'],['textiles','labour-productivity'],'operatives per spindles/looms'),
('p0253_1',['labour'],['employment-and-unemployment'],'unemployment, 24 centres'),
('p0254_1',['labour'],['employment-and-unemployment'],'unemployment estimates'),
('p0255_1',['labour'],['employment-and-unemployment','occupations'],'unemployment census by occupation'),
('p0256_1',['labour'],['employment-and-unemployment'],'dismissed workers destinations'),
('p0266_1',['population'],['births-and-deaths','marriage-and-divorce'],'births and marriage age by income'),
('p0266_2',['population'],['births-and-deaths'],'births per woman by income'),
('p0267_1',['population','welfare'],['births-and-deaths','housing'],'births by living space'),
('p0268_1',['population'],['births-and-deaths','marriage-and-divorce'],'births by class and marriage duration'),
]
b=json.load(open('batches/b04.json'))
out=[{'key':P+k,'topics':t,'tags':g,'flags':[],'why':w} for k,t,g,w in D]
assert [o['key'] for o in out]==[r['key'] for r in b]
voc=open('../../VOCABULARY.md').read()
for o in out:
    for g in o['tags']: assert '`%s`'%g in voc,g
json.dump(out,open('results/b04.json','w'),ensure_ascii=False,indent=1)
print(len(out),sum(1 for o in out if o['tags']))
