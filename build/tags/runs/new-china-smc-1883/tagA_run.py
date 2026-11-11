import json,re
B='batches/b0%d.json'
# explicit non-financial / special, keyed by (batch,idx)
E={
(1,0):(["military"],["arms-and-arsenals","militias-and-volunteer-forces"]),
(1,1):(["military"],["arms-and-arsenals","militias-and-volunteer-forces"]),
(1,2):(["finance"],["public-debt"]),
(1,3):(["finance"],["public-budgets"]),
(1,4):(["finance"],["public-budgets"]),
(1,5):(["finance"],["public-budgets"]),
(1,14):(["finance"],["taxation","real-estate"]),
(1,15):(["finance"],["taxation","real-estate"]),
(1,16):(["finance"],["taxation","real-estate"]),
(1,17):(["finance","economy"],["land-tax","real-estate","land-registration"]),
(1,18):(["communications"],["postal-services"]),
(1,19):(["utilities"],["electricity"]),
(1,20):(["utilities"],["electricity"]),
(1,21):(["utilities"],["gas"]),
(1,22):(["utilities"],["gas","electricity"]),
(1,23):(["utilities"],["electricity","gas"]),
(1,24):(["crime-and-justice"],["police","offences-and-convictions","nationality-and-ethnicity"]),
(1,25):(["crime-and-justice"],["police","offences-and-convictions"]),
(1,26):(["crime-and-justice","education"],["offences-and-convictions","literacy-and-adult-education"]),
(1,27):(["crime-and-justice"],["corporal-punishment","offences-and-convictions"]),
(1,28):(["health"],["public-health"]),
(1,29):(["health","trade"],["food-inspection","livestock"]),
(1,30):(["population","health"],["age-and-sex","births-and-deaths"]),
(1,31):(["population","health"],["births-and-deaths"]),
(1,32):(["health"],["epidemics","diseases"]),
(1,33):(["health"],["epidemics","diseases"]),
(1,34):(["health"],["epidemics","diseases","nationality-and-ethnicity"]),
(1,35):(["population","health"],["births-and-deaths","diseases"]),
(1,36):(["population","health"],["births-and-deaths","diseases"]),
(1,37):(["population","health"],["births-and-deaths","infant-mortality"]),
(1,38):(["finance","utilities"],["real-estate","land-reclamation"]),
(1,39):(["finance","transportation"],["roads-and-bridges","real-estate"]),
(2,0):(["finance","culture"],["recreation-and-amusements"]),
(2,1):(["population","health"],["births-and-deaths"]),
(2,2):(["utilities"],["water-and-sewerage"]),
(2,3):(["utilities"],["water-and-sewerage"]),
(2,4):(["transportation"],["roads-and-bridges"]),
(2,5):(["education","finance"],["education-finance","mission-schools"]),
(2,6):(["health"],["diseases","vaccination"]),
(2,7):(["utilities"],["gas"]),
(2,8):(["utilities","finance"],["gas","electricity"]),
(2,9):(["culture"],["arts-and-music"]),
(2,10):(["culture","finance"],["arts-and-music"]),
(2,11):(["culture","finance"],["arts-and-music"]),
(2,12):(["finance"],["firefighting","public-budgets"]),
(2,13):(["finance"],["firefighting","public-budgets"]),
(2,14):(["government"],["firefighting"]),
(2,14):(["government"],["firefighting"]),
(6,18):(["finance"],["public-budgets"]),
(6,21):(["finance"],["public-budgets"]),
(6,23):(["finance"],["public-budgets"]),
(6,24):(["finance"],["public-budgets"]),
(5,0):(["finance"],["public-budgets"]),
(5,1):(["finance"],["public-budgets"]),
(5,2):(["finance"],["public-budgets"]),
(5,3):(["finance"],["public-budgets"]),
(4,2):(["finance","government"],["public-budgets","government-offices"]),
}
# keyword rules for finance statements/budget; first match wins; applied to title
K=[
("Police Savings|Savings Bank|Guarantee Fund",(["finance","crime-and-justice"],["savings-and-loans","police"])),
("Police Pension|Pension Fund",(["finance","crime-and-justice"],["insurance-and-pensions","police"])),
("Police Gratuity",(["finance","crime-and-justice"],["insurance-and-pensions","police"])),
("Police Recreation",(["finance","crime-and-justice"],["police"])),
("Police",(["finance","crime-and-justice"],["public-budgets","police"])),
("Land Tax",(["finance"],["taxation","land-tax"])),
("Municipal Rate",(["finance"],["taxation"])),
("License|Liquor|Livery|Billiard",(["finance"],["taxation"])),
("Permit",(["finance"],["taxation"])),
("Contribution|Taotai",(["finance"],["public-budgets"])),
("Lock Hospital|Medical|Sanitary|Night-Soil|Poundage",(["finance","health"],["public-budgets","public-health"])),
("Relief of Poor",(["finance","welfare"],["poor-relief","public-budgets"])),
("Lighting",(["finance","utilities"],["public-budgets","gas"])),
("Water Supply",(["finance","utilities"],["public-budgets","water-and-sewerage"])),
("Telegraph",(["finance","communications"],["telegraph","public-budgets"])),
("Post Office",(["finance","communications"],["postal-services","public-budgets"])),
("Fire",(["finance"],["firefighting","public-budgets"])),
("Volunteers",(["finance","military"],["militias-and-volunteer-forces","public-budgets"])),
("Band",(["finance","culture"],["arts-and-music","public-budgets"])),
("Museum",(["finance","culture"],["museums-and-heritage","public-budgets"])),
("Library",(["finance","culture"],["libraries","public-budgets"])),
("Education",(["finance","education"],["education-finance"])),
("Cemeter",(["finance"],["public-budgets"])),
("Sinking Fund|Loan|Interest|Debenture",(["finance"],["public-debt","public-budgets"])),
("Bridges|Roads|Drainage|Landing|Widening|Bundings|Latrines|Fire Wells|Buildings|Public Works|Outside Roads",(["finance","transportation"],["public-budgets","roads-and-bridges"])),
("Surveyor|Secretariat|General Charges|Nuisance",(["finance","government"],["public-budgets","government-offices"])),
("Public Garden",(["finance","culture"],["public-budgets","recreation-and-amusements"])),
("Market",(["finance"],["public-budgets"])),
("Stud|Stock|Land and Buildings|Land, Buildings",(["finance"],["public-budgets"])),
]
for n in range(1,7):
    d=json.load(open(B%n)); out=[]
    for i,r in enumerate(d):
        t=r['title']
        if (n,i) in E: tp,tg=E[(n,i)]; why="content-based"
        elif (n,i) in () : pass
        else:
            tp,tg=(["finance"],["public-budgets"]); why="municipal accounts"
            for k,v in K:
                if re.search(k,t,re.I): tp,tg=v; why="statement head: "+k.split('|')[0]; break
        fl=[]
        if (n,i)==(2,14): fl=["text-tables"]
        # Summary of correspondence etc fine; rate summaries
        if re.match(r'Summary of General Municipal Rate',t): tp,tg,why=["finance"],["taxation","real-estate"],"rate assessment summary"
        if (n,i)==(1,6) or (n,i)==(1,7): pass
        out.append({"key":r['key'],"topics":tp[:2],"tags":tg[:3],"flags":fl,"why":why})
    assert [o['key'] for o in out]==[r['key'] for r in d]
    json.dump(out,open('results/b0%d.json'%n,'w'),ensure_ascii=False,indent=1)
    print(n,len(out),sum(1 for o in out if o['tags']))
