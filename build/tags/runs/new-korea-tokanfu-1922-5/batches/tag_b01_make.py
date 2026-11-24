import json
P="korea-tokanfu-1922-5:"
R=[
("p0007_1",["crime-and-justice","government"],["police"],"police offices and staff by rank"),
("p0008_1",["crime-and-justice"],["offences-and-convictions","police"],"offences detected and disposition"),
("p0015_1",["crime-and-justice"],["offences-and-convictions"],"crimes and detections by offence"),
("p0018_1",["crime-and-justice"],["offences-and-convictions"],"crimes by province"),
("p0018_2",["crime-and-justice"],["summary-justice","offences-and-convictions"],"summary judgment cases"),
("p0019_1",["crime-and-justice"],["summary-justice","offences-and-convictions"],"persons sentenced summarily"),
("p0020_1",["crime-and-justice"],["offences-and-convictions"],"theft fraud victims"),
("p0021_1",["crime-and-justice"],["offences-and-convictions"],"theft fraud detection"),
("p0021_2",["transportation","disasters"],["transport-accidents","shipping"],"ships in distress"),
("p0022_1",["disasters"],["fires","disaster-losses"],"fires by cause and loss"),
("p0022_2",["disasters"],["fires"],"fires by month"),
("p0022_3",["disasters"],["fires"],"fire causes"),
("p0023_1",["disasters","government"],["firefighting"],"fire brigades"),
("p0023_2",["population","crime-and-justice"],["births-and-deaths","suicide"],"unnatural deaths by cause"),
("p0024_1",["population","health"],["suicide","age-and-sex"],"suicides by age and reason"),
("p0026_1",["welfare","population"],["child-welfare"],"abandoned children"),
("p0027_1",["crime-and-justice","welfare"],["police"],"police rescue"),
("p0029_1",["crime-and-justice","government"],[],"private firearms; no fitting tag"),
("p0030_1",["government","trade"],[],"licensed trades under police control"),
("p0033_1",["health"],["medical-services","pharmaceuticals"],"hospitals and medical personnel"),
("p0034_1",["health"],["diseases","epidemics"],"infectious disease patients and deaths"),
("p0039_1",["health"],["diseases","occupations"],"infectious disease by occupation"),
("p0040_1",["health"],["diseases","age-and-sex"],"infectious disease by age"),
("p0042_1",["health"],["diseases","epidemics"],"infectious disease by month"),
("p0043_1",["health","crime-and-justice"],["sex-work","medical-services"],"health examination of prostitutes"),
("p0045_1",["health"],["vaccination"],"vaccinations by province"),
("p0048_1",["health"],["vaccination","age-and-sex"],"vaccinations by age"),
("p0048_2",["health","government"],["medical-services","government-offices"],"government hospital staff and expenses"),
("p0049_1",["health","government"],["medical-services"],"charity hospital staff and expenses"),
("p0050_1",["health"],["diseases","medical-services"],"hospital patients by disease"),
("p0054_1",["health","welfare"],["medical-services"],"itinerant clinics, free treatment"),
("p0055_1",["health","transportation"],["quarantine","shipping"],"ship quarantine"),
]
b=json.load(open("batches/b01.json"))
assert [x["key"] for x in b]==[P+r[0] for r in R]
v=json.load(open("../../vocabulary.json"))
json.dump([{"key":P+k,"topics":t,"tags":g,"flags":[],"why":w} for k,t,g,w in R],open("results/b01.json","w"),ensure_ascii=False,indent=1)
print(len(R),sum(1 for r in R if r[2]))
