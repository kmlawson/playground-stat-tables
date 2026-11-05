import json
d=json.load(open('batches/b01.json'))
v=json.load(open('../../vocabulary.json'))
T={t['id'] for t in v['topics']}; G={t['id'] for t in v['tags']}
L=[(["finance","history"],["currency"],"coinage metal ratios"),
(["economy"],["economic-indicators"],"multi-domain indicators"),
(["trade","economy"],["commodity-origins"],"foreign monopolies of materials"),
(["mining"],["coal","mineral-reserves"],"coal reserves"),
(["manufacturing"],["iron-and-steel","coal"],"coal cost in iron/steel"),
(["trade"],["imports"],"raw material imports"),
(["manufacturing"],["iron-and-steel"],"pig iron/steel supply"),
(["trade","finance"],["balance-of-payments"],"balance of trade"),
(["labour","manufacturing"],["labour-productivity","cotton"],"cotton mill output per worker"),
(["agriculture"],["arable-land"],"farm families by acreage"),
(["agriculture","welfare"],["household-budgets","land-tenure"],"farm household accounts"),
(["agriculture"],["land-tenure"],"farm rent"),
(["labour"],["occupations"],"worker experience by industry"),
(["labour"],["employment-and-unemployment"],"discharged miners reemployed"),
(["labour","population"],["occupations"],"workers by occupation"),
(["labour"],["occupations"],"workers by sector and sex"),
(["labour"],[],"workers under Factory Act"),
(["labour"],["occupations"],"workers by industry"),
(["labour"],[],"workers by factory size"),
(["labour"],["child-labour"],"child workers"),
(["labour"],["women-workers"],"women workers"),
(["labour","welfare"],["working-conditions","housing"],"factory dormitories"),
(["labour"],["labour-disputes"],"workers' demands"),
(["labour"],["employment-and-unemployment"],"unemployed persons"),
(["labour","education"],["employment-and-unemployment"],"unemployed graduates"),
(["labour","education"],["employment-and-unemployment"],"graduate unemployment Osaka"),
(["labour"],["wages"],"daily income"),
(["labour"],["wages"],"bonuses in kind"),
(["labour","economy"],["wages","prices"],"wages vs prices"),
(["labour","welfare"],["cost-of-living","household-budgets"],"living standard"),
(["labour","welfare"],["household-budgets","cost-of-living"],"worker income and expenses"),
(["welfare","labour"],["household-budgets"],"budget expenditure shares"),
(["labour"],["working-conditions"],"hours of work"),
(["labour"],["working-conditions"],"hours and rest"),
(["labour"],["working-conditions"],"hours by industry"),
(["labour"],["working-conditions"],"overtime"),
(["labour","manufacturing"],["working-conditions","labour-productivity","silk"],"silk reelers hours"),
(["labour"],["trade-unions"],"unions and membership"),
(["labour"],["labour-disputes"],"strikes by year"),
(["labour"],["labour-disputes"],"strike causes")]
assert len(L)==len(d)
out=[]
for r,(t,g,w) in zip(d,L):
    assert set(t)<=T and set(g)<=G
    out.append({"key":r['key'],"topics":t,"tags":g,"flags":[],"why":w})
json.dump(out,open('results/b01.json','w'),ensure_ascii=False,indent=1)
print(len(out),sum(1 for o in out if o['tags']))
