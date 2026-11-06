import json
P=["population"]
m={
"p0112_1":(P,["age-and-sex","households"],"sex ratio by household kind"),
"p0113_1":(P,["age-and-sex"],"age distribution"),
"p0113_2":(P,["age-and-sex"],"functional age groups"),
"p0114_1":(P,["age-and-sex"],"age distribution international"),
"p0117_1":(P,["marriage-and-divorce","age-and-sex"],"marital condition by age sex"),
"p0120_1":(P,["marriage-and-divorce"],"marriage rates"),
"p0121_1":(P,["marriage-and-divorce","age-and-sex"],"age at first marriage"),
"p0121_2":(P,["marriage-and-divorce","age-and-sex"],"age at marriage groups"),
"p0123_1":(P,["marriage-and-divorce"],"divorce rates Japan US"),
"p0124_1":(P,["marriage-and-divorce","births-and-deaths"],"marriage and birth rates"),
"p0124_2":(P,["marriage-and-divorce","births-and-deaths"],"marriage and birth rates"),
"p0126_1":(P,["births-and-deaths","age-and-sex"],"fertility by age of married"),
"p0127_1":(P,["births-and-deaths","marriage-and-divorce"],"fertility decline from marriage delay"),
"p0129_1":(P,["births-and-deaths"],"birth rates"),
"p0130_1":(P,["births-and-deaths"],"births and rate"),
"p0132_1":(P,["births-and-deaths","age-and-sex"],"female age ratios and births"),
"p0133_1":(P,["births-and-deaths"],"birth rate, births per female"),
"p0134_1":(P,["births-and-deaths"],"birth and reproduction rates"),
"p0135_1":(P,["births-and-deaths"],"net reproduction rate"),
"p0137_1":(P,["births-and-deaths"],"deaths and rate"),
"p0139_1":(P,["births-and-deaths","age-and-sex"],"average age at death by sex"),
"p0139_2":(P,["births-and-deaths","age-and-sex"],"life expectancy"),
"p0139_3":(P,["births-and-deaths","age-and-sex"],"life expectancy comparison"),
"p0140_1":(P,["births-and-deaths","age-and-sex"],"specific and adjusted death rates"),
"p0141_1":(P,["births-and-deaths","age-and-sex"],"death rates by age"),
"p0142_1":(P+["health"],["births-and-deaths","suicide"],"causes of death"),
"p0143_1":(["health","population"],["diseases","births-and-deaths"],"deaths by disease"),
"p0144_1":(["health","population"],["diseases","age-and-sex"],"tuberculosis share of deaths by age"),
"p0146_1":(["health","population"],["diseases","infant-mortality"],"tuberculosis and infant mortality"),
"p0147_1":(P,["births-and-deaths"],"birth death natural increase"),
"p0150_1":(P,["population-totals"],"future population estimate"),
"p0151_1":(P,["population-totals"],"projection by Bureau"),
"p0152_1":(P,["population-totals","births-and-deaths"],"projection Shimojo"),
"p0154_1":(P,["age-and-sex"],"survival rates by age"),
"p0154_2":(P,["population-totals","age-and-sex"],"projection by age Ueda"),
"p0155_1":(P,["births-and-deaths","age-and-sex"],"births per women by age"),
"p0156_1":(P,["population-totals","births-and-deaths"],"projection births Soda"),
"p0157_1":(P,["population-totals"],"projection comparison"),
"p0159_1":(P,["age-and-sex","population-totals"],"projected functional age classes"),
"p0159_2":(P,["age-and-sex","population-totals"],"projected middle-aged group"),
}
d=json.load(open('batches/b02.json'));out=[]
for r in d:
    t,g,w=m[r['key'].split(':')[1]]
    out.append({"key":r['key'],"topics":t,"tags":g,"flags":[],"why":w})
json.dump(out,open('results/b02.json','w'),ensure_ascii=False,indent=1)
v=json.load(open('../../vocabulary.json'));print(list(v.keys()))
print(len(out),sum(1 for o in out if o['tags']))
