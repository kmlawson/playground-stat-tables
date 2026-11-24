import json
b=json.load(open('batches/b01.json'))
v=json.load(open('../../vocabulary.json'))
T={t['id'] for t in v['topics']};G={t['id'] for t in v['tags']}
S="""
transportation|railways|summary railway totals
geography,population|land-area,population-totals|area and population by province
geography|land-area|area and position
geography|weather|temperature rain snow
government|administrative-divisions,land-area|units per province
population|households,nationality-and-ethnicity|households by nationality
population|population-totals,nationality-and-ethnicity|population by nationality
population|births-and-deaths,nationality-and-ethnicity|birth death rates
population|population-totals,nationality-and-ethnicity|town populations
population,labour|occupations,nationality-and-ethnicity|population by occupation
agriculture|arable-land|cultivated area, farm households
agriculture|land-tenure|state land leased
economy,agriculture|economic-indicators|value of products by sector
agriculture|rice|rice harvest
agriculture|cereals,barley,wheat|barley wheat harvest
agriculture|crop-production,soybeans|pulses and grains
agriculture|industrial-crops,cotton|cotton hemp tobacco
agriculture|horticulture|fruit harvest
agriculture|sericulture|silkworm rearing
agriculture|livestock|livestock counts
forestry|forest-area|forest area
forestry|timber,forest-management|forestry office output
mining|mineral-production|mineral output
fisheries|fishing,fish-and-fish-products|catch and marine products
manufacturing,trade|salt,imports|salt production and imports
economy,trade|prices|retail prices
labour|wages|daily wages
finance|banking|banks
finance|cooperatives,savings-and-loans|financial associations
economy,finance|companies|companies HQ in Korea
economy,finance|companies|companies with branches in Korea
trade|exports,imports|trade by port
trade|exports,imports|principal goods
transportation|ports|harbour works
transportation|roads-and-bridges|road lengths
transportation|railways|state railways
transportation|railways|private railways
transportation|shipping|vessels
transportation|shipping|shipping routes
communications|postal-services,telegraph,telephone|communication facilities
""".strip().split('\n')
assert len(S)==len(b)
out=[]
for r,s in zip(b,S):
    t,g,w=s.split('|')
    t=t.split(',');g=[x for x in g.split(',') if x]
    assert set(t)<=T,t
    assert set(g)<=G,g
    out.append({"key":r['key'],"topics":t,"tags":g,"flags":[],"why":w})
json.dump(out,open('results/b01.json','w'),ensure_ascii=False,indent=1)
print(len(out),sum(1 for o in out if o['tags']))
