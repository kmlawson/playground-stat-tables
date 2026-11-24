import json
d=json.load(open('batches/b05.json'))
v={t['id'] for t in json.load(open('../../vocabulary.json')).get('tags',[])} if False else None
R=[("158",["finance"],["interest-rates","savings-and-loans"],"deposit/loan rates"),
("160",["trade","agriculture"],["prices","cereals"],"grain prices"),
("161",["trade","agriculture"],["prices","rice"],"unhulled rice prices"),
("162",["trade","agriculture"],["prices","rice"],"polished rice prices"),
("163",["trade","agriculture"],["prices","soybeans"],"soybean prices"),
("164",["trade","agriculture"],["prices","barley"],"barley prices"),
("165",["trade","agriculture"],["prices","wheat"],"wheat prices"),
("166",["trade","economy"],["prices"],"commodity prices by town"),
("167",["labour"],["wages","nationality-and-ethnicity"],"daily wages by trade and nationality"),
("168",["trade"],["exports","imports","intra-imperial-trade"],"exports/shipments/imports by year"),
("169",["trade"],["exports","imports","ports"],"trade by port"),
("170",["trade"],["exports","imports"],"trade by country"),
("171",["trade"],["exports","imports"],"trade by month"),
("172",["trade"],["exports"],"principal exports by destination"),
("173",["trade"],["imports"],"principal imports by origin"),
("174",["trade","finance"],["gold","silver","imports"],"gold and silver trade"),
("175",["transportation","trade"],["shipping","ports"],"vessels by flag"),
("176",["finance","trade"],["customs-revenue"],"customs duties collected"),
("177",["trade"],["warehousing"],"bonded warehouse goods"),
("178",["trade"],["transit-trade"],"transit goods"),
("179",["trade"],["exports","imports"],"overland border trade"),
("180",["trade"],["exports","imports"],"border trade by commodity"),
("181",["transportation"],["railways"],"railway mileage"),
("182",["transportation"],["railways"],"railway land, rolling stock"),
("183",["transportation"],["railways"],"train operations"),
("184",["transportation"],["railways"],"passengers and freight"),
("185",["transportation"],["railways"],"transport revenue"),
("186",["transportation"],["railways"],"through traffic"),
("187",["transportation","trade"],["railways"],"freight tonnage by commodity"),
("188",["transportation"],["railways"],"traffic by station"),
("189",["transportation","finance"],["railways","construction"],"construction expenses"),
("190",["transportation","finance"],["railways","construction"],"construction budget"),
("191",["transportation","finance"],["railways"],"repair costs"),
("192",["transportation","finance"],["railways"],"railway revenue/expenditure"),
("193",["transportation","finance"],["railways"],"railway investment"),
("194",["transportation","economy"],["railways","tourism"],"railway hotels"),
("195",["transportation","trade"],["railways","warehousing"],"railway warehouses"),
("196",["transportation","health"],["railways","transport-accidents"],"railway casualties"),
("197",["transportation","crime-and-justice"],["railways","offences-and-convictions"],"railway law violators"),
("198",["transportation","labour"],["railways","wages"],"railway workers and wages")]
assert len(R)==len(d)
out=[]
for r,(n,t,g,w) in zip(d,R):
    assert r['table_no']==n
    out.append({"key":r['key'],"topics":t,"tags":g,"flags":[],"why":w})
json.dump(out,open('results/b05.json','w'),ensure_ascii=False,indent=1)
voc=json.load(open('../../vocabulary.json'))
ids=set()
def walk(o):
    if isinstance(o,dict):
        if 'id' in o: ids.add(o['id'])
        for x in o.values(): walk(x)
    elif isinstance(o,list):
        for x in o: walk(x)
walk(voc)
print([x for o in out for x in o['topics']+o['tags'] if x not in ids])
