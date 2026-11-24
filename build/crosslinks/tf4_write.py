import json
A='korea-tokanfu-1919/';B='korea-tokanfu-1939/'
def F(l,a,b,note=""):
    return {"label":l,"members":[A+x for x in a]+[B+x for x in b],"note":note}
D={
"korea-tokanfu--agriculture":[
F("Farm households",["p0069_2"],["p0030_1"],"1919 also gives farm population."),
F("Cultivated land area",["p0069_1"],["p0030_2"]),
F("Rice acreage and yield",["p0070_1"],["p0031_2"]),
F("Barley and wheat acreage and yield",["p0071_1"],["p0031_3"]),
F("Pulses acreage and yield",["p0072_1"],["p0032_1"]),
F("Miscellaneous grains",["p0073_1"],["p0032_2"]),
F("Industrial crops",["p0073_2"],["p0033_1"]),
F("Vegetables",["p0075_1"],["p0034_1"]),
F("Domestic silkworms and mulberry fields",["p0077_1"],["p0035_2","p0036_1"],"1919 combines mulberry fields with silkworm rearing; 1939 splits them."),
F("Tussah silkworms",["p0077_2"],["p0035_3"]),
F("Cooperative silkworm rearing",["p0078_2"],["p0035_5"]),
F("Silkworm egg production",["p0078_3"],["p0035_4"]),
F("Mulberry seedling production",["p0078_4"],["p0036_2"]),
F("Breeding bulls by age",["p0079_1"],["p0036_5"]),
F("Cattle births and deaths",["p0081_1"],["p0036_4"]),
F("Slaughterhouses",["p0081_2"],["p0039_1"]),
F("Livestock products",["p0082_1"],["p0040_1"]),
F("Oriental Development Company business",["p0083_3"],["p0043_1"]),
F("Oriental Development Company settlers and allotted land",["p0083_4"],["p0043_2"]),
],
"korea-tokanfu--forestry":[
F("Forest area",["p0084_1"],["p0044_1"]),
F("Protection forests",["p0084_2"],["p0047_2"]),
F("Commemorative tree planting",["p0087_1"],["p0046_1"]),
F("Tree nurseries",["p0087_2"],["p0044_3","p0044_4"],"1939 splits state-run and public/private nurseries."),
F("State afforestation",["p0086_2"],["p0045_1"]),
F("Local and private afforestation",["p0086_3"],["p0045_2"]),
F("Forestry station timber purchases and sales",["p0091_1"],["p0049_4"]),
],
"korea-tokanfu--fisheries":[
F("Fishery households and population",["p0092_1"],["p0051_1"]),
F("Fishery vessels",["p0092_2"],["p0051_2"]),
F("Fishing gear",["p0093_1"],["p0051_3"]),
F("Fishing boats and catch",["p0095_1"],["p0051_4","p0052_1"],"1939 splits boats from annual catch."),
F("Catch by species",["p0095_2"],["p0052_2"]),
F("Aquaculture",["p0096_1"],["p0054_1"]),
F("Marine products by type",["p0097_1"],["p0056_1"]),
F("Fish markets",["p0097_3"],["p0062_4"]),
F("Fishery applications and licences",["p0094_1"],["p0062_3"]),
],
"korea-tokanfu--mining-and-industry":[
F("Mining applications",["p0099_1","p0099_2"],["p0064_1"]),
F("Mining permits by mineral",["p0100_1"],["p0064_2"]),
F("Permitted mining areas by mineral",["p0101_1"],["p0065_1"],"1919 by province, 1939 by year."),
F("Factories",["p0118_1"],["p0066_1"]),
F("Industrial products value",["p0119_1"],["p0073_2"],"1919 by province per year; 1939 by province per year (Part 2)."),
],
"korea-tokanfu--population":[
F("Resident population by year",["p0033_1"],["p0018_1"]),
F("Resident population by city, county and island",["p0033_2"],["p0018_2"]),
F("Resident Japanese by origin",["p0047_1"],["p0028_1"]),
F("Resident foreigners by nationality",["p0049_1"],["p0028_2"]),
F("Population by occupation",["p0051_1"],["p0023_1"]),
F("Population by race, percentage",["p0057_1"],["p0028_3"]),
F("Births, deaths, marriages",["p0057_2"],["p0029_1","p0029_2","p0029_3"],"1939 splits vital events into three tables."),
]}
import os
for k,v in D.items():
    json.dump({"listing":k,"families":v},open("families/%s.json"%k.split("--")[1].join(["korea-tokanfu--",""]) ,"w"),ensure_ascii=False,indent=1)
    # validate ids
    txt=open("listings/%s.txt"%k).read()
    for f in v:
        for m in f["members"]:
            s,i=m.split("/")
            assert s+" | "+i+" |" in txt,m
