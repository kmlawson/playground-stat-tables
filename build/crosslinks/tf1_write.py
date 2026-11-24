import json
A='korea-tokanfu-1919/';B='korea-tokanfu-1939/'
def F(label,a,b,note=""):
    return {"label":label,"members":[A+x for x in a]+[B+x for x in b],"note":note}
out={
"public-finance":[
F("Government-General special account revenue and expenditure by year",["p0269_1"],["p0246_1"]),
F("Railway supplies fund special account",["p0272_1"],["p0246_2"]),
F("Special account revenue by item",["p0271_1"],["p0246_4"],"1919 gives budget years only; 1939 gives budget and settlements."),
F("Special account expenditure by item",["p0271_2"],["p0246_5"],"1919 gives budget years only; 1939 gives budget and settlements."),
F("Land tax by province",["p0275_2"],["p0251_1"]),
F("Income tax by province",["p0280_1"],["p0248_2"]),
F("Income tax payers by amount paid",["p0281_1"],["p0250_1"]),
F("Liquor tax by province and type",["p0281_3","p0281_4","p0282_1","p0282_2"],["p0254_3"],"1919 splits the table by type of liquor across four tables."),
F("Imported liquor tax",["p0283_1","p0283_2","p0283_3"],["p0255_1"],"1919 splits the table by type of liquor across three tables."),
F("Sugar consumption tax",["p0285_2"],["p0256_2"]),
F("Mining taxes",["p0286_1","p0287_1"],["p0254_1"],"1919 prints mining-area tax and mineral-output tax separately; 1939 combines them."),
F("National tax receipts",["p0293_1"],["p0248_1"],"1919 by tax item; 1939 by year with tax columns."),
F("Non-tax revenue receipts",["p0295_2"],["p0257_1"]),
F("Revenue stamp receipts",["p0295_1"],["p0257_2"]),
F("Direct tax burden by city and county",["p0297_2","p0298_1"],["p0267_3","p0269_1"],"Each edition splits the table in two (cities/counties in 1919; two parts in 1939)."),
F("Provincial revenue and expenditure",["p0299_1"],["p0257_4"],"1919 calls provincial finance 地方費."),
F("Provincial expenditure by item and province",["p0300_1"],["p0258_2"]),
F("Provincial levies by province",["p0300_2"],["p0259_1"]),
F("Provincial tax collection",["p0301_1"],["p0260_1"]),
F("City revenue budget",["p0303_1"],["p0261_2"],"1939 is the general account; separate special accounts are not linked."),
F("City expenditure budget",["p0303_2"],["p0262_1"],"1939 is the general account; separate special accounts are not linked."),
F("Township revenue budget",["p0304_1"],["p0263_1" if False else "p0264_3"]),
F("Township expenditure budget",["p0305_1"],["p0265_1"]),
F("Average township burden",["p0306_1"],["p0265_4"]),
F("School association revenue and expenditure budget",["p0306_2"],["p0266_2"]),
F("Government debt",["p0309_2"],["p0257_3"]),
F("City debt",["p0309_3"],["p0264_1"]),
F("School association debt",["p0310_1"],["p0267_2"]),
],
"officials-and-pensions":[
F("Government officials and salaries",["p0314_1","p0314_2"],["p0272_1"],"1919 prints by year and by office separately."),
F("Local officials paid from local funds",["p0320_1"],["p0274_1","p0276_1"]),
F("Township officials",["p0321_1"],["p0276_2"]),
F("Yi Household Office staff and salaries",["p0322_2"],["p0276_3"]),
F("Pensions and allowances",["p0323_1"],["p0277_1"]),
],
"monopolies":[
F("Fresh ginseng cultivation, harvest and receipts",["p0311_1","p0311_2","p0312_1"],["p0157_6"],"1919 splits the table in three."),
F("Red ginseng and ginseng products manufactured",["p0312_2"],["p0158_1"]),
F("Red ginseng sales",["p0312_3"],["p0158_2"]),
F("Ginseng exports and imports",["p0313_2"],["p0158_3"]),
],
"land":[
F("Position and area of Korea",["p0015_1"],["p0014_1","p0014_2"],"1939 splits position and area."),
F("Administrative divisions by province",["p0015_2"],["p0014_3"]),
F("State-owned land",["p0016_1"],["p0014_4"]),
F("Privately owned land",["p0017_1","p0017_2"],["p0014_5"],"1919 separates taxed and untaxed private land."),
F("Land sale prices",["p0018_1"],["p0015_1","p0016_1"],"1939 combines sale and rental prices, in cities and counties."),
F("Land rental prices",["p0021_1"],["p0015_1","p0016_1"] if False else []),
],
"prices-and-wages":[
F("Retail prices",["p0143_1"],["p0132_1"]),
F("Wages",["p0147_1"],["p0134_1"]),
],
}
# land: rental prices fold into one family with sale prices
l=out["land"]; l[-2]["members"].insert(1,A+"p0021_1"); l.pop()
l[-1]["label"]="Land sale and rental prices"
for k,v in out.items():
    json.dump({"listing":"korea-tokanfu--"+k,"families":v},open("families/korea-tokanfu--%s.json"%k,"w"),ensure_ascii=False,indent=1)
    json.load(open("families/korea-tokanfu--%s.json"%k))
    print(k,len(v),sum(len(f["members"]) for f in v))
