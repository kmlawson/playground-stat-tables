import json
R={
"p0028_1":(["economy","manufacturing"],["industrial-output"]),
"p0028_2":(["manufacturing"],["industrial-output"]),
"p0031_1":(["economy","military"],["national-income-and-wealth"]),
"p0032_1":(["economy","military"],["war-and-mobilisation","national-income-and-wealth"]),
"p0033_1":(["economy"],["national-income-and-wealth"]),
"p0036_1":(["manufacturing","mining"],["mineral-production","iron-and-steel"]),
"p0037_1":(["military","economy"],["economic-controls","war-and-mobilisation"]),
"p0038_1":(["labour","military"],["war-and-mobilisation","employment-and-unemployment"]),
"p0040_1":(["military","manufacturing"],["air-force","machinery"]),
"p0041_1":(["manufacturing"],["industrial-output"]),
"p0041_2":(["manufacturing","military"],["industrial-output","air-force"]),
"p0042_1":(["transportation"],["shipping"]),
"p0042_2":(["manufacturing","transportation"],["shipbuilding"]),
"p0042_3":(["manufacturing","transportation"],["shipbuilding","shipping"]),
"p0043_1":(["military","manufacturing"],["navy","shipbuilding"]),
"p0043_2":(["military","manufacturing"],["arms-and-arsenals"]),
"p0043_3":(["military","manufacturing"],["arms-and-arsenals"]),
"p0044_1":(["military","manufacturing"],["arms-and-arsenals","shipbuilding"]),
"p0044_2":(["mining","manufacturing"],["mineral-production","iron-and-steel"]),
"p0044_3":(["mining"],["coal"]),
"p0045_1":(["mining","manufacturing"],["coal","iron-ore","iron-and-steel"]),
"p0046_1":(["manufacturing"],["iron-and-steel"]),
"p0046_2":(["mining"],["petroleum"]),
"p0047_1":(["labour"],["occupations","women-workers"]),
"p0048_1":(["labour"],["occupations"]),
"p0049_1":(["manufacturing","labour"],["cotton","textiles"]),
"p0049_2":(["manufacturing"],["textiles","cotton","wool"]),
"p0051_1":(["military"],["air-force"]),
"p0051_2":(["military"],["air-force","navy"]),
"p0051_3":(["military"],["air-force"]),
"p0054_1":(["military"],["air-force"]),
"p0055_1":(["military"],["air-force"]),
"p0055_2":(["military"],["navy","air-force"]),
"p0059_1":(["military","transportation"],["shipping","war-and-mobilisation"]),
"p0063_1":(["military","mining"],["petroleum"]),
"p0092_1":(["mining"],["coal"]),
"p0093_1":(["manufacturing"],["iron-and-steel"]),
"p0093_2":(["manufacturing"],["iron-and-steel"]),
"p0096_1":(["mining"],["petroleum"]),
"p0096_2":(["mining"],["petroleum"]),
}
b=json.load(open('batches/b01.json'))
out=[]
for r in b:
    k=r['key'];t,g=R[k.split(':')[1]]
    out.append({"key":k,"topics":t,"tags":g,"flags":[],"why":r['title'][:60]})
v=json.load(open('../../vocabulary.json'))
T={x['id'] for x in v['topics']};G={x['id'] for x in v['tags']}
assert all(set(o['topics'])<=T and set(o['tags'])<=G for o in out) and len(out)==len(b)
json.dump(out,open('results/b01.json','w'),ensure_ascii=False,indent=1)
print(len(out),sum(1 for o in out if o['tags']))
