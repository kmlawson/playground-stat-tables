import json
a,b,c='korea-kani-kokusei-1925','korea-kokusei-1930','korea-kokusei-1935'
def m(s,*ids): return [f"{s}/{i}" for i in ids]
prov=['p0027_1','p0031_1','p0033_1','p0036_1','p0039_1','p0044_1','p0049_1','p0053_1','p0057_1','p0060_1','p0064_1','p0067_1','p0070_1']
F=[
("Area, households and population by province",m(a,'p0026_1')+m(b,'p0023_1')+m(c,'p0053_1'),""),
("Households (ordinary/quasi) and population by province",m(b,'p0184_1')+m(c,'p0059_1'),""),
("Households and population by municipality, county and township",[f"{a}/{i}" for i in prov]+m(b,'p0185_1')+m(c,'p0060_1'),"1925 is split into one table per province."),
("Population of municipal and county areas by province",m(b,'p0023_2')+m(c,'p0085_1','p0019_3'),"1935 p0019_3 is the small summary version."),
("Municipalities by population size class",m(b,'p0024_1','p0025_1')+m(c,'p0086_1','p0020_2'),"1930 split into whole-country and by-province tables; 1935 p0020_2 is the summary version."),
("Population by selected age groups and province",m(b,'p0026_1')+m(c,'p0092_1'),""),
("Population by age (three classes), province and municipalities",m(b,'p0027_1')+m(c,'p0091_1'),""),
("Population by marital status, province and municipalities",m(b,'p0028_1')+m(c,'p0093_1'),""),
("Population by single year of age and marital status, whole country",m(a,'p0072_1')+m(b,'p0029_1')+m(c,'p0103_1'),""),
("Population by age group and marital status, whole country",m(b,'p0031_1')+m(c,'p0095_1'),""),
("Population by age group and marital status, by province",m(a,'p0075_1')+m(b,'p0032_1')+m(c,'p0098_1'),"1925 also gives single years of age."),
("Population by nationality, whole country",m(b,'p0049_1')+m(c,'p0125_1','p0040_3'),"1935 p0040_3 is the summary version."),
("Population by nationality and province",m(b,'p0049_2')+m(c,'p0125_2'),""),
("Population by nationality and municipality",m(b,'p0050_1')+m(c,'p0126_1'),""),
("Population by nationality and age, whole country",m(a,'p0294_1')+m(b,'p0051_1')+m(c,'p0127_1'),""),
("Proportions by nationality and age, whole country",m(b,'p0052_1')+m(c,'p0128_1'),""),
("Foreigners by age and nationality, whole country",m(b,'p0053_1')+m(c,'p0129_1'),""),
]
json.dump({"listing":"korea-kokusei--census-results","families":[{"label":l,"members":x,"note":n} for l,x,n in F]},open('families/korea-kokusei--census-results.json','w'),ensure_ascii=False,indent=1)
print(len(F),sum(len(x) for l,x,n in F))
