import json
b=json.load(open('batches/b13.json'))
F=lambda t,g,w:(["finance"]+([] if False else []),t,w)
m={
479:(["finance","government"],["taxation"],"delinquent national tax dispositions"),
480:(["finance","crime-and-justice"],["taxation","offences-and-convictions","smuggling"],"indirect tax offenders, fines"),
481:(["finance","government"],["taxation"],"tax collection costs"),
482:(["finance","population"],["taxation"],"direct tax burden per household, cities"),
483:(["finance","population"],["taxation"],"direct tax burden counties"),
484:(["finance","government"],["public-budgets","local-government"],"local expense revenue/expenditure"),
485:(["finance","government"],["public-budgets","taxation","local-government"],"local revenue by tax"),
486:(["finance","government"],["public-budgets","local-government"],"local expenditure by item"),
487:(["finance","government"],["taxation","local-government"],"local tax levies"),
488:(["finance","government"],["taxation","local-government"],"local tax receipts"),
489:(["finance","government"],["taxation","local-government"],"delinquent local tax"),
490:(["finance","government"],["public-budgets","local-government"],"city revenue budgets"),
491:(["finance","government"],["public-budgets","local-government"],"city expenditure budgets"),
492:(["finance","government"],["public-budgets","local-government"],"township revenue budgets"),
493:(["finance","government"],["public-budgets","local-government"],"township expenditure budgets"),
494:(["finance","government"],["taxation","local-government"],"township levy rates"),
495:(["finance","government"],["taxation","local-government"],"township burden per household"),
496:(["finance","education"],["education-finance","public-budgets"],"school association budgets"),
497:(["finance","agriculture"],["irrigation","public-budgets"],"irrigation association budgets"),
498:(["finance","education"],["education-finance","public-budgets"],"school expense revenue"),
499:(["finance","education"],["education-finance","public-budgets"],"school expense expenditure"),
500:(["finance","religion"],["public-budgets","confucianism"],"Confucian school property budgets"),
501:(["finance","government"],["public-debt"],"government-general bonds"),
502:(["finance","government"],["public-debt","local-government"],"city bonds"),
503:(["finance","education"],["public-debt","education-finance"],"school association bonds"),
504:(["finance","agriculture"],["public-debt","irrigation"],"irrigation association bonds"),
505:(["agriculture","economy"],["ginseng","state-monopolies"],"ginseng cultivation"),
506:(["agriculture","economy"],["ginseng","state-monopolies"],"fresh ginseng harvest"),
507:(["agriculture","economy"],["ginseng","state-monopolies"],"fresh ginseng collected"),
508:(["economy","manufacturing"],["ginseng","state-monopolies"],"red ginseng production"),
509:(["economy","trade"],["ginseng","state-monopolies"],"red ginseng sales"),
510:(["economy","manufacturing"],["ginseng","state-monopolies"],"ginseng products"),
511:(["economy","agriculture"],["tobacco","state-monopolies"],"leaf tobacco purchased"),
}
V=json.load(open('../../vocabulary.json'))
def ids(x): return {i['id'] if isinstance(i,dict) else i for i in (x.values() if isinstance(x,dict) else x)} if not isinstance(x,dict) else set(x.keys())|{i.get('id') for i in x.values() if isinstance(i,dict)}
T=ids(V['topics']);G=ids(V['tags'])
out=[]
for r in b:
    t,g,w=m[int(r['table_no'])]
    assert all(x in T for x in t),t
    assert all(x in G for x in g),g
    out.append(dict(key=r['key'],topics=t,tags=g,flags=[],why=w))
json.dump(out,open('results/b13.json','w'),ensure_ascii=False,indent=1)
print(len(out),len(b),sum(1 for o in out if o['tags']))
