import json
def cls(k,t):
    T=t
    PB="public-budgets"
    def r(tp,tg,w): return tp,tg,w
    if 'Ordinary Income' in T:
        if 'Rate' in T: return ["finance","government"],[PB,"taxation"],"municipal rates income"
        if 'Wharfage' in T: return ["finance"],[PB,"customs-revenue"],"wharfage dues income"
        if 'Licence' in T: return ["finance","government"],[PB,"taxation"],"licence fee income"
        if 'Rent' in T: return ["finance"],[PB,"public-property"],"rent of municipal property"
        if 'Undertakings' in T: return ["finance","economy"],[PB,"securities-and-investment"],"dividends from utility companies"
        return ["finance"],[PB],"misc income"
    if 'Extraordinary Income' in T: return ["finance"],[PB],"extraordinary income"
    if 'Deficit' in T: return ["finance"],[PB],"deficit"
    if 'Extraordinary Expenditure' in T:
        if 'Bridges' in T: return ["finance","transportation"],[PB,"roads-and-bridges"],"bridge capital works"
        if 'Bundings' in T: return ["finance","utilities"],[PB,"river-conservancy"],"bunding works"
        if 'Drainage' in T or 'Sewerage' in T: return ["finance","utilities"],[PB,"water-and-sewerage"],"drainage capital"
        if 'Landing' in T: return ["finance","transportation"],[PB,"ports"],"landing stages"
        if 'Volunteer' in T: return ["finance","military"],[PB,"militias-and-volunteer-forces"],"volunteer corps works"
        if 'Fire' in T: return ["finance","government"],[PB,"firefighting"],"fire brigade works"
        if 'Police' in T: return ["finance","crime-and-justice"],[PB,"police"],"police works"
        if 'Health' in T: return ["finance","health"],[PB,"public-health"],"health works"
        if 'Parks' in T: return ["finance","culture"],[PB,"recreation-and-amusements"],"parks works"
        if 'Public Works' in T: return ["finance","utilities"],[PB,"construction"],"PWD buildings"
        if T.endswith('Land'): return ["finance"],[PB,"real-estate"],"land purchase"
        return ["finance"],[PB,"construction"],"building works"
    if 'Interest' in T or 'Redemption' in T: return ["finance"],[PB,"public-debt"],"loan interest/redemption"
    if 'Volunteer' in T or 'Stock and Stores' in T and False: pass
    if 'Volunteer Corps' in T: return ["finance","military"],[PB,"militias-and-volunteer-forces"],"volunteer corps"
    if 'Fire Brigade' in T: return ["finance","government"],[PB,"firefighting"],"fire brigade"
    if 'Police Force' in T: return ["finance","crime-and-justice"],[PB,"police"],"police"
    if 'Health Department' in T or 'Nursing Staff' in T or 'Hospitals' in T:
        tg=[PB]
        if 'Plague' in T or 'Mosquito' in T: tg.append("epidemics")
        elif 'Cesspool' in T: tg.append("water-and-sewerage")
        elif 'Hospital' in T or 'Nursing' in T or 'Sanatorium' in T or 'Ambulance' in T: tg.append("medical-services")
        else: tg.append("public-health")
        return ["finance","health"],tg[:3],"health dept"
    if 'Allocated to the Various Hospitals' in T or 'Details of Pay' in T: return ["finance","health"],[PB,"medical-services"],"nursing"
    if 'Public Works' in T:
        if 'Creeks' in T: return ["finance","utilities"],[PB,"river-conservancy"],"creeks"
        if 'Drainage' in T: return ["finance","utilities"],[PB,"water-and-sewerage"],"drainage"
        if 'Roads' in T: return ["finance","transportation"],[PB,"roads-and-bridges"],"roads"
        if 'Lighting' in T: return ["finance","utilities"],[PB,"electricity"],"lighting"
        if 'Parks' in T: return ["finance","culture"],[PB,"recreation-and-amusements"],"parks"
        if 'Buildings' in T: return ["finance","utilities"],[PB,"construction"],"buildings"
        return ["finance","utilities"],[PB],"PWD"
    if 'Orchestra' in T: return ["finance","culture"],[PB,"arts-and-music"],"orchestra"
    if 'Library' in T: return ["finance","culture"],[PB,"libraries"],"library"
    if 'Educational' in T:
        return ["finance","education"],[PB,"education-finance","schools-and-pupils"] if 'Grants' not in T else [PB,"education-finance"],"school budget"
    if 'Finance Department' in T or 'Secretariat' in T: return ["finance","government"],[PB],"admin dept"
    if 'Grants in Aid' in T: return ["finance","welfare"],[PB],"grants in aid"
    if 'Pensions' in T: return ["finance","government"],[PB,"insurance-and-pensions"],"pensions"
    if 'Rent' in T: return ["finance"],[PB,"public-property"],"rent"
    if 'Credit' in T or 'Stock and Stores' in T: return ["finance"],[PB],"credit/stores"
    return ["finance"],[PB],"budget"
for b in ('b15','b16','b17'):
    d=json.load(open(f'batches/{b}.json')); out=[]
    for x in d:
        t=x['title']
        tp,tg,w=cls(x['key'],t)
        if 'Educational' in t and 'Grants' in t: tg=[ "public-budgets","education-finance"]
        if 'Educational' in t and 'Stock' in t: tg=["public-budgets","education-finance"]
        out.append({"key":x['key'],"topics":tp,"tags":tg,"flags":[],"why":w})
    json.dump(out,open(f'results/{b}.json','w'),ensure_ascii=False,indent=1)
    print(b,len(out))
