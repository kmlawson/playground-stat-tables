import json
b=json.load(open('batches/b02.json'))
P=["population"];PH=["population","health"]
BD="births-and-deaths";N="nationality-and-ethnicity"
m={
'p0041_1':(P,[BD,"marriage-and-divorce",N]),
'p0041_2':(P,[BD,N]),
'p0041_3':(P,[BD,N]),'p0041_4':(P,[BD,N]),
'p0042_1':(PH,["diseases",BD,N]),
'p0043_1':(P,[BD,N]),'p0043_2':(PH,["diseases",BD,N]),
'p0044_1':(P,[BD,"age-and-sex",N]),'p0045_1':(PH,["diseases","age-and-sex",N]),
'p0046_2':(P,["marriage-and-divorce",N]),'p0046_3':(P,["marriage-and-divorce","age-and-sex",N]),
'p0046_4':(P,["population-totals","households",N]),
'p0047_1':(P,["age-and-sex",N]),'p0047_2':(P,["occupations","households",N]),
'p0049_1':(P,[BD,"marriage-and-divorce",N]),'p0049_2':(P,[BD,N]),'p0049_3':(P,[BD,N]),'p0049_4':(P,[BD,N]),
'p0050_1':(PH,["diseases",BD,N]),'p0051_1':(P,[BD,N]),'p0051_2':(PH,["diseases",BD,N]),
'p0052_1':(P,[BD,"age-and-sex",N]),'p0053_1':(PH,["diseases","age-and-sex",N]),
'p0053_2':(P,["marriage-and-divorce","age-and-sex",N]),
'p0054_1':(P,["population-totals","households",N]),'p0055_1':(P,["occupations",N,"households"]),
'p0056_1':(P,["population-totals","households",N]),'p0056_2':(P,[BD,N]),'p0056_3':(P,[BD,N]),
'p0057_1':(PH,["diseases",BD,N]),'p0057_2':(P,[BD,N]),'p0057_3':(P,[BD,"age-and-sex",N]),
'p0057_4':(["population","government"],["passports-and-travel-permits",N]),
'p0057_5':(P,["migration","occupations"]),
'p0058_1':(["transportation","population"],["shipping","migration"]),
'p0059_1':(P,["population-totals","households",N]),
'p0062_1':(["agriculture","population"],["arable-land","occupations"]),
'p0062_2':(["agriculture"],["rice","crop-production"]),
'p0063_1':(["agriculture"],["barley","wheat"]),
'p0064_1':(["agriculture"],["soybeans","crop-production"]),
}
out=[]
for r in b:
    t,g=m[r['key'].split(':')[1]]
    out.append({"key":r['key'],"topics":t,"tags":g[:3],"flags":[],"why":r['en']['t'][:60]})
json.dump(out,open('results/b02.json','w'),ensure_ascii=False,indent=1)
v=json.load(open('../../vocabulary.json'));ids={t['id'] for t in v['tags']}|{t['id'] for t in v['topics']}
print(len(out),len(b),[x for o in out for x in o['topics']+o['tags'] if x not in ids])
