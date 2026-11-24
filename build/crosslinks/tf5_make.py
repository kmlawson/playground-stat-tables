import json
A='korea-tokanfu-1919/';B='korea-tokanfu-1939/'
def f(l,a,b,note=""):
    return {"label":l,"members":[A+x for x in a]+[B+x for x in b],"note":note}
D={
"foreign-trade":[
f("Trade totals by year",["p0150_1"],["p0125_1"]),
f("Trade by port",["p0150_2"],["p0125_2","p0126_1"],"1939 splits it into exports/shipments and imports/receipts."),
f("Trade by country",["p0151_1"],["p0127_1"]),
f("Trade by month",["p0152_1"],["p0126_2","p0126_3"],"1939 splits exports and imports."),
f("Principal exports by destination",["p0153_1"],["p0127_4"]),
f("Principal imports by origin",["p0156_1"],["p0129_1"]),
f("Vessels entering and leaving port by flag",["p0161_2"],["p0130_1","p0130_2"],"1939 splits entering and leaving."),
f("Customs revenue",["p0162_1"],["p0131_2"]),
f("Bonded warehouses",["p0162_2"],["p0131_1"]),
],
"communications":[
f("Communication facilities",["p0181_3"],["p0142_1"]),
f("Ordinary mail",["p0182_1"],["p0142_5"]),
f("Parcel post",["p0182_2"],["p0143_1"]),
f("Postal money orders",["p0183_1","p0183_2"],["p0144_1"],"1919 splits domestic and international."),
f("Postal savings deposits and withdrawals",["p0184_1"],["p0144_4"]),
f("Postal transfer savings",["p0184_3"],["p0144_2"]),
f("Telegraph lines",["p0184_4"],["p0142_3"]),
f("Telegrams sent and received",["p0185_1"],["p0143_3"]),
f("Telephone lines",["p0186_1"],["p0142_4"]),
f("Telephone subscribers and calls",["p0186_2","p0187_1"],["p0143_2"],"1919 splits calls within one exchange area and between two."),
],
"railways":[
f("State railway line lengths and stations",["p0164_1"],["p0148_1"]),
f("State railway passenger and freight traffic",["p0165_2"],["p0148_2","p0149_1"],"1939 splits passengers and freight."),
f("Principal freight by commodity",["p0167_1"],["p0149_2"]),
f("Through traffic",["p0166_2"],["p0150_1"]),
f("Traffic by station",["p0168_1"],["p0150_2"]),
f("State railway transport revenue",["p0166_1"],["p0151_1"]),
f("State railway revenue and expenditure",["p0174_3"],["p0152_1"]),
f("Construction and improvement expenditure",["p0173_1"],["p0152_2"]),
f("State railway investment",["p0175_1"],["p0152_3"]),
f("Private railways and tramways, capital",["p0177_2"],["p0152_4","p0155_1"],"1919 combines railways and tramways; 1939 splits them."),
f("Private railways and tramways, traffic",["p0178_1"],["p0153_2","p0155_2"],"1919 combines railways and tramways; 1939 splits them."),
f("Private railways, construction costs",["p0178_2"],["p0154_2"]),
f("Private railways and tramways, revenue and expenditure",["p0179_1"],["p0154_1","p0155_3"],"1919 combines railways and tramways; 1939 splits them."),
],
"public-works-and-shipping":[
f("Navigation marks",["p0180_2"],["p0140_1"]),
f("Ships",["p0180_3"],["p0140_2"]),
f("Government-ordered shipping routes",["p0180_4"],["p0140_4"]),
f("Waterworks",["p0190_1"],["p0138_4"]),
f("Flood damage",["p0191_1"],["p0139_1"]),
]}
for k,v in D.items():
    json.dump({"listing":"korea-tokanfu--"+k,"families":v},open("families/korea-tokanfu--%s.json"%k,"w"),ensure_ascii=False,indent=1)
    print(k,len(v),sum(len(x["members"]) for x in v))
