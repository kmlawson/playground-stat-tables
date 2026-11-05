import json
P="japan-labor-conditions-1928:"
R=[("p0187_1",["labour"],["labour-disputes"],[],"strikes by duration"),
("p0232_1",["labour"],["working-conditions"],[],"shop committees by industry; no exact term"),
("p0236_1",["labour"],["working-conditions"],[],"travel expense conditions, factories reporting"),
("p0239_1",["labour","welfare"],["working-conditions"],[],"factory benevolent work by industry"),
("p0244_1",["labour"],["working-conditions"],["text-tables"],"employee contract termination conditions list"),
("p0244_2",["labour"],["working-conditions"],["text-tables"],"employer contract termination conditions list"),
("p0248_1",["labour"],["business-associations"],[],"employers' associations with members"),
("p0274_1",["labour","welfare"],["insurance-and-pensions","wages"],[],"health insurance remuneration classes"),
("p0276_1",["labour","finance"],["insurance-and-pensions"],[],"insurance society premium rates"),
("p0277_1",["labour","finance"],["insurance-and-pensions"],[],"employer contribution health insurance societies")]
b=json.load(open('batches/b02.json'))
assert [r['key'] for r in b]==[P+x[0] for x in R]
json.dump([{"key":P+k,"topics":t,"tags":g,"flags":f,"why":w} for k,t,g,f,w in R],open('results/b02.json','w'),ensure_ascii=False,indent=1)
