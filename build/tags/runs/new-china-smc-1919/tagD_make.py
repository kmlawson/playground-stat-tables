import json
def cls(k,t):
    T=t
    PB="public-budgets"
    def r(tp,tg,why): return tp,tg,why
    if 'Balance Sheet' in T: return r(["finance"],["public-budgets"],"municipal balance sheet")
    if T.endswith('Summary'): return r(["finance"],[PB],"summary of income and expenditure")
    if 'Redemption of Debentures' in T or 'Interest, Brokerage' in T: return r(["finance"],["public-debt"],"debt service")
    if 'Extraordinary Income' in T: return r(["finance"],[PB],"extraordinary income")
    if 'Extraordinary Expenditure' in T:
        if 'Bridges' in T: return r(["finance","transportation"],[PB,"roads-and-bridges"],"extraordinary: bridges")
        if 'Drainage' in T: return r(["finance","utilities"],[PB,"water-and-sewerage"],"extraordinary: drainage")
        if 'Roads' in T: return r(["finance","transportation"],[PB,"roads-and-bridges"],"extraordinary: roads")
        if 'Land' in T: return r(["finance"],[PB,"public-property"],"extraordinary: land")
        return r(["finance"],[PB],"extraordinary expenditure")
    if 'Educational Department' in T:
        if 'Grants in Aid' in T: return r(["education","finance"],["education-finance",PB],"school grants")
        return r(["education","finance"],["education-finance",PB],"school expenditure")
    if 'Public Library' in T: return r(["finance","culture"],[PB,"libraries"],"library expenditure")
    if 'Public Band' in T: return r(["finance","culture"],[PB,"arts-and-music"],"band expenditure")
    if 'Health Department' in T:
        if 'Plague' in T or 'Mosquito' in T: return r(["finance","health"],[PB,"public-health"],"disease prevention spending")
        if 'Hospitals' in T or 'Ambulance' in T or 'Nursing' in T: return r(["finance","health"],[PB,"medical-services"],"hospital spending")
        if 'Cemeteries' in T or 'Mortu' in T: return r(["finance","health"],[PB,"public-health"],"cemeteries/mortuary spending")
        return r(["finance","health"],[PB,"public-health"],"health dept spending")
    if 'Public Works' in T:
        if 'Buildings' in T: return r(["finance","utilities"],[PB,"construction"],"building works spending")
        if 'Drainage' in T: return r(["finance","utilities"],[PB,"water-and-sewerage"],"drainage spending")
        if 'Creeks' in T: return r(["finance","utilities"],[PB,"river-conservancy"],"creeks spending")
        if 'Roads' in T: return r(["finance","transportation"],[PB,"roads-and-bridges"],"road spending")
        if 'Lighting' in T: return r(["finance","utilities"],[PB,"electricity"],"lighting spending")
        if 'Parks' in T: return r(["finance","culture"],[PB,"recreation-and-amusements"],"parks spending")
        return r(["finance"],[PB],"public works spending")
    if 'Sewage' in T: return r(["finance","utilities"],[PB,"water-and-sewerage"],"sewage/water spending")
    if 'Rent of Municipal' in T: return r(["finance"],[PB,"public-property"],"municipal property rents")
    return r(["finance"],[PB],"departmental expenditure")
out={}
for b in ('b10','b11'):
    res=[]
    for rec in json.load(open('batches/%s.json'%b)):
        tp,tg,why=cls(rec['key'],rec['title'])
        res.append({"key":rec['key'],"topics":tp,"tags":tg,"flags":[],"why":why})
    json.dump(res,open('results/%s.json'%b,'w'),ensure_ascii=False,indent=1)
    print(b,len(res))
