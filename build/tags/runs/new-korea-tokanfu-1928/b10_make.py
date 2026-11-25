import json
recs=json.load(open('batches/b10.json'))
P='primary-education';S='schools-and-pupils';T='teachers';F='education-finance';V='vocational-education';H='higher-education';Sec='secondary-education'
m={359:(["crime-and-justice","welfare"],["prisoner-aftercare"],"discharged prisoner aid"),
360:(["education","population"],[S,P],"school-age children enrolment")}
def st(l,w): return (["education"],l,w)
def fin(l,w): return (["education","finance"],l,w)
for n in (361,362,363,364,365,369): m[n]=st([P,S],"elementary school status")
m[366]=fin([F,P],"elementary expenses");m[367]=fin([F,P],"elementary assets")
m[368]=st([T,P],"elementary teachers pay")
for n in (370,371,372,373,374,378): m[n]=st([P,S],"common school status")
m[375]=fin([F,P],"common school expenses");m[376]=fin([F,P],"common school assets")
m[377]=st([T,P],"common school teachers pay")
m[379]=st([Sec,S],"middle schools");m[380]=fin([F,Sec],"middle school assets")
for n in (381,383,384,386,388): m[n]=st([Sec,S],"higher/secondary school status")
for n in (382,385,387): m[n]=fin([F,Sec],"school assets")
for n in (389,391,393,394): m[n]=st([V,S],"vocational schools")
for n in (390,392): m[n]=fin([F,V],"vocational school assets")
for n in (395,396,397): m[n]=st([H,S],"professional colleges")
m[398]=fin([F,H],"college assets")
out=[]
for r in recs:
    t,g,w=m[int(r['table_no'])]
    out.append({"key":r['key'],"topics":t,"tags":g,"flags":[],"why":w})
json.dump(out,open('results/b10.json','w'),ensure_ascii=False,indent=1)
print(len(out),len(recs))
