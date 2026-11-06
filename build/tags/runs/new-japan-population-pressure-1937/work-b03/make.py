import json
P="japan-population-pressure-1937:"
R=[
("p0165_1",["agriculture"],["arable-land"],"farms count and acreage per farm"),
("p0166_1",["agriculture"],["arable-land"],"farm size distribution"),
("p0167_1",["agriculture"],["arable-land"],"average farm size by country"),
("p0169_1",["agriculture"],["household-budgets"],"farm account receipts outlay"),
("p0169_2",["agriculture"],["household-budgets"],"farmer income and outlay"),
("p0170_1",["agriculture"],["household-budgets","arable-land"],"farm surplus by acreage"),
("p0172_1",["agriculture"],["household-budgets"],"farm income and wages 1921-9"),
("p0173_1",["agriculture"],["fertilisers","crop-production"],"fertiliser and production"),
("p0175_1",["agriculture"],["real-estate"],"paddy and upland values"),
("p0175_2",["agriculture"],["real-estate","rice"],"land values vs rice value"),
("p0177_1",["agriculture"],["land-tenure"],"tenant acreage share"),
("p0177_2",["agriculture"],["land-tenure"],"landed and tenant farmers"),
("p0179_1",["agriculture"],["land-tenure"],"rent ratios paddy upland"),
("p0179_2",["agriculture"],["land-tenure"],"villages by rent ratio"),
("p0186_1",["agriculture","economy"],["crop-production","food-supply-and-rationing"],"food crop supply and demand"),
("p0186_2",["agriculture","health"],["food-supply-and-rationing","crop-production"],"per capita consumption of crops"),
("p0188_1",["agriculture"],["rice","food-supply-and-rationing"],"rice supply and consumption"),
("p0190_1",["agriculture","trade"],["rice","intra-imperial-trade"],"rice supply by source"),
("p0191_1",["agriculture"],["rice"],"rice yield by country"),
("p0192_1",["trade"],["rice","prices"],"rice prices by origin"),
("p0193_1",["trade"],["rice","prices"],"retail rice prices"),
("p0194_1",["agriculture","economy"],["rice"],"rice production cost"),
("p0195_1",["agriculture"],["rice","food-supply-and-rationing"],"rice carry-over"),
("p0202_1",["agriculture","economy"],["food-supply-and-rationing","cereals"],"projected grain consumption"),
("p0204_1",["agriculture"],["land-reclamation","arable-land"],"reclaimable land"),
("p0205_1",["agriculture"],["arable-land"],"arable land extension contraction"),
("p0207_1",["health"],["nutrition"],"nutritive requirements"),
("p0208_1",["health"],["nutrition"],"nutritive value of food consumed"),
("p0209_1",["health","economy"],["nutrition","food-supply-and-rationing"],"per capita food available"),
("p0214_1",["population"],["overseas-communities","colonies-and-leased-territories"],"Japanese in colonies"),
("p0216_1",["population","labour"],["occupations","overseas-communities"],"occupations of Japanese in colonies"),
("p0219_1",["population"],["migration","migrant-remittances"],"emigration returns remittances"),
("p0220_1",["population"],["overseas-communities"],"Japanese abroad by country"),
("p0221_1",["population","labour"],["occupations","overseas-communities"],"occupations of Japanese abroad"),
("p0223_1",["population"],["migration"],"emigration to Brazil"),
("p0224_1",["population"],["migration"],"emigration to Philippines"),
("p0224_2",["population"],["overseas-communities"],"Japanese distribution in Philippines"),
("p0225_1",["population","labour"],["occupations","overseas-communities"],"occupations of Japanese in Philippines"),
("p0228_1",["labour"],["wages"],"daily wages Chinese and Japanese"),
("p0230_1",["population"],["migration","nationality-and-ethnicity"],"Chosenese migration to Japan"),
]
inp=json.load(open('batches/b03.json'))
assert [r['key'] for r in inp]==[P+k for k,*_ in R]
out=[{"key":P+k,"topics":t,"tags":g,"flags":[],"why":w} for k,t,g,w in R]
json.dump(out,open('results/b03.json','w'),ensure_ascii=False,indent=1)
print(len(out),sum(1 for o in out if o['tags']))
