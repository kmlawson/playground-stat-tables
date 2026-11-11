import json
S={}
def a(keys,topics,tags,why,flags=()):
    for k in keys.split(): S[k]=(topics.split(),tags.split(),list(flags),why)
# b07
a('p0311_2 p0312_1 p0312_2','utilities government','construction','building permits/new buildings')
a('p0311_3','utilities government','construction','building plans submitted')
a('p0313_1 p0314_1','manufacturing utilities','cement-and-bricks','municipal concrete yard stock/products')
a('p0319_1','government finance','public-property land-area','schedule of municipal properties and areas')
a('p0323_1 p0324_1','finance government','roads-and-bridges public-budgets','land and road construction spend')
a('p0325_1 p0325_2 p0325_3 p0326_1 p0327_1 p0331_1 p0336_1 p0336_2 p0339_1 p0340_1 p0342_1','government finance','roads-and-bridges real-estate','land compensation for road widening')
a('p0346_1 p0346_2 p0346_3 p0347_1 p0347_3 p0347_4 p0347_5 p0347_6','utilities geography','','parks planting counts')
a('p0347_2','sport culture','sports-participation','sports at recreation ground')
a('p0351_1 p0351_2 p0351_3 p0355_1 p0355_2 p0358_1 p0358_2 p0359_1 p0359_2','utilities','electricity','electricity plant/network')
a('p0351_4 p0354_1','utilities','electricity','load factor/units sold')
# b08
a('p0359_3','utilities','electricity','street lighting outage fines')
a('p0362_1 p0362_2 p0362_3 p0362_4 p0363_1 p0363_2 p0363_3 p0363_4 p0363_5 p0367_1','utilities','electricity','electricity network/connections')
a('p0366_1','utilities manufacturing','electricity industrial-output','power installed by industry')
a('p0379_1','utilities','electricity','electricity growth by year')
a('p0383_1 p0387_1 p0388_1 p0389_1','utilities finance','electricity','electricity department accounts')
a('p0383_2','utilities government','electricity wages','electricity dept salaries')
a('p0384_1 p0384_2 p0386_1 p0386_2','utilities finance','electricity','capital expenditure power station')
a('p0387_2 p0390_1 p0392_1 p0392_2 p0392_3 p0392_4 p0393_1 p0393_2 p0393_3 p0393_4 p0394_1 p0395_1 p0396_1','utilities finance','electricity','electricity department accounts')
a('p0398_1 p0398_2 p0399_1 p0399_2 p0400_1','finance government','public-budgets','municipal budget/expenditure')
# b09
a('p0400_2 p0401_1 p0401_2 p0401_3','finance government','public-budgets','budget items outside estimate')
a('p0402_1 p0403_1','finance','securities-and-investment','municipal investments by investor')
a('p0404_1 p0411_1','finance government','public-budgets','ordinary income/expenditure')
a('p0405_1 p0416_5 p0417_4','finance government','public-budgets','ordinary income vs estimate')
a('p0406_1 p0407_1 p0416_1','finance','taxation land-tax','land tax')
a('p0406_2 p0406_3 p0412_1 p0413_1 p0416_2','finance','taxation','municipal rate houses assessment')
a('p0407_2 p0416_4','finance transportation','customs-revenue ports','wharfage dues')
a('p0407_3 p0414_1 p0415_1 p0417_1','finance government','taxation','licence fees')
a('p0409_1 p0409_2','transportation finance','road-transport taxation','vehicle licences')
a('p0410_1 p0417_2','finance government','public-property','market fees/rents')
a('p0416_3','finance','taxation','special advertisement rate')
a('p0417_3','finance','securities-and-investment','revenue from undertakings')
a('p0418_1 p0418_2 p0418_3 p0418_4','finance military','public-budgets','volunteer corps expenditure')
a('p0419_1 p0419_2','finance','public-budgets firefighting','fire brigade expenditure')
a('p0420_1 p0421_1 p0421_2','finance crime-and-justice','public-budgets police','police expenditure')
for b in ['b07','b08','b09']:
    d=json.load(open(f'batches/{b}.json')); out=[]
    for r in d:
        k=r['key'].split(':')[1]; t,g,f,w=S[k]
        out.append(dict(key=r['key'],topics=t,tags=g,flags=f,why=w))
    import os; os.makedirs('results',exist_ok=True)
    json.dump(out,open(f'results/{b}.json','w'),ensure_ascii=False,indent=1)
    print(b,len(out),sum(1 for o in out if o['tags']))
