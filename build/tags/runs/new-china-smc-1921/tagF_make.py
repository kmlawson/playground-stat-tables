import json
PB="public-budgets"
def R(t,g,w): return (t,g,w)
rules=[ # (substring in title, topics, tags, why)
("Police Hospital",["health","finance"],["medical-services",PB],"police hospital budget"),
("Sanatorium",["health","finance"],["medical-services",PB],"sanatorium budget"),
("Nursing",["health","finance"],["medical-services",PB],"nursing service budget"),
("Ambulance",["health","finance"],["medical-services",PB],"ambulance budget"),
("Cemeteries",["health","finance"],["public-health",PB],"cemeteries/mortuary budget"),
("Swimming Bath",["finance","culture"],[PB,"recreation-and-amusements"],"swimming bath budget"),
("Health Department — Extra",["health","finance"],["public-health",PB],"health dept extra-departmental"),
("Health Department — Stock",["health","finance"],["public-health",PB],"health dept stores"),
("Public Works Department — General",["finance","government"],[PB],"public works general budget"),
("Buildings",["finance","government"],[PB],"public works buildings"),
("Creeks and River",["finance","transportation"],[PB,"rivers-and-waterways"],"creeks and river budget"),
("Drainage",["finance","utilities"],[PB,"water-and-sewerage"],"drainage budget"),
("Maintenance of Roads",["finance","transportation"],[PB,"roads-and-bridges"],"road maintenance budget"),
("Cleansing and Watering",["finance","transportation"],[PB,"roads-and-bridges"],"road cleansing budget"),
("Lighting",["finance","utilities"],[PB,"electricity"],"lighting budget"),
("Parks",["finance","culture"],[PB,"recreation-and-amusements"],"parks budget"),
("Public Works Department — Extra",["finance","government"],[PB],"public works extra-departmental"),
("Public Works Department — Stock",["finance","government"],[PB],"public works stores"),
("Orchestra",["finance","culture"],[PB,"arts-and-music"],"orchestra/band budget"),
("Library",["finance","culture"],[PB,"libraries"],"library budget"),
("Grants in Aid",None,None,None),
("Educational Department",["education","finance"],["education-finance","schools-and-pupils",PB],"school budget"),
("Treasurer",["finance","government"],[PB],"finance dept budget"),
("Compradore",["finance","government"],[PB],"finance dept budget"),
("Finance Department",["finance","government"],[PB],"finance dept stores"),
("Secretariat",["finance","government"],[PB],"secretariat budget"),
("Ordinary Expenditure — Stock",["finance","government"],[PB],"stores budget"),
("General Charges — General",["finance","government"],[PB],"general charges"),
("Rent of Municipal",["finance","government"],[PB,"real-estate"],"rent of premises"),
("Interest, Brokerage",["finance"],[PB,"public-debt","interest-rates"],"debt interest"),
("Redemption of Debentures",["finance"],[PB,"public-debt"],"debenture redemption"),
("Extraordinary Income",["finance"],[PB],"extraordinary income"),
("Extraordinary Expenditure — Bridges",["finance","transportation"],[PB,"roads-and-bridges"],"bridges capital"),
("Bundings",["finance","utilities"],[PB,"flood-control"],"bunding capital"),
("Extraordinary Expenditure — Drainage",["finance","utilities"],[PB,"water-and-sewerage"],"drainage capital"),
("Landing Stages",["finance","transportation"],[PB,"ports"],"landing stages capital"),
("Extraordinary Expenditure — Land",["finance"],[PB,"real-estate"],"land purchase"),
("Extraordinary Expenditure — Buildings",["finance"],[PB,"construction"],"buildings capital"),
("Extraordinary Expenditure — Roads",["finance","transportation"],[PB,"roads-and-bridges"],"roads capital"),
("Extraordinary Expenditure",["finance"],[PB],"extraordinary expenditure"),
("Summary — Ordinary Expenditure — Health",["finance","health"],[PB],"summary health"),
("Summary — Ordinary Expenditure — Public Works",["finance","government"],[PB],"summary public works"),
("Summary — Ordinary Expenditure — Educ",["finance","education"],[PB,"education-finance"],"summary education"),
("Summary",["finance"],[PB],"budget summary"),
]
out={}
for b in ['b15','b16']:
    d=json.load(open('batches/%s.json'%b)); res=[]
    for r in d:
        t=r['title']
        if t.startswith("Municipal Budget 1922 — Ordinary Expenditure — Educational"): t2="Educational Department"
        else: t2=t
        if t.startswith("Municipal Budget 1922 — Ordinary Expenditure — General Charges — Grants"): 
            m=(["finance","government"],[PB],"grants in aid")
        elif t=="Municipal Budget 1922 — Ordinary Expenditure — Stock and Stores": m=(["finance","government"],[PB],"stores budget")
        elif "Ordinary Expenditure — Educational Department — Grants" in t: m=(["education","finance"],["education-finance",PB],"education grants in aid")
        else:
            m=None
            for s,tp,tg,w in rules:
                if tp is None: continue
                if s in t2 or s in t: m=(tp,tg,w);break
        assert m,t
        if t.startswith("Municipal Budget 1922 — Ordinary Expenditure — Educational") and "Stock" in t: m=(["education","finance"],["education-finance",PB],"school stores")
        res.append(dict(key=r['key'],topics=m[0],tags=m[1][:3],flags=[],why=m[2]))
    json.dump(res,open('results/%s.json'%b,'w'),ensure_ascii=False,indent=1)
    print(b,len(res),sum(1 for x in res if x['tags']),[ (x['key'][-7:],x['why']) for x in res][:0])
