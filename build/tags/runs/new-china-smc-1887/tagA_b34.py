import json,sys
from tagA_fin import fin
b=sys.argv[1]
recs=json.load(open(f'batches/{b}.json'))
FD=['disasters'];FF=['firefighting']
man={}
if b=='b03':
  man={0:(['culture','finance'],['arts-and-music','public-budgets'],[],'band accounts'),1:(['culture','finance'],['arts-and-music','public-budgets'],[],'band estimate'),
  2:(['government'],FF,['text-tables'],'fire board roster'),3:(['government'],FF,['text-tables'],'officers roster'),4:(['government'],FF,['text-tables'],'officers roster'),
  5:(FD,FF,[],'hose distribution'),6:(FD,['fires','firefighting'],[],'fires and houses burnt'),7:(['finance','disasters'],FF+['public-budgets'],[],'fire dept accounts'),
  8:(['finance','disasters'],FF+['public-budgets'],[],'fire dept estimate'),9:(['government'],FF,['text-tables'],'commission roster'),10:(FD,['fires','firefighting'],[],'fire record')}
out=[]
for i,r in enumerate(recs):
  out.append(man[i] if i in man else fin(r['title']))
json.dump(out,sys.stdout)
