import json
B='runs/new-china-smc-1925/'
F=["finance"]
PB="public-budgets"
def r(t,g,w): return (t,g,w)
b11=[
(["finance","disasters"],[PB,"firefighting"],"fire brigade stores"),
(["finance","crime-and-justice"],[PB,"police"],"police budget"),
]+[(["finance","crime-and-justice"],[PB,"police"],"police pay")]*4+[
(["finance","crime-and-justice"],[PB,"police","vocational-education"],"chauffeur school"),
(["finance","crime-and-justice"],[PB,"medical-services","police"],"police medical aid"),
(["finance","crime-and-justice"],[PB,"police"],"patrol ponies"),
(["finance","crime-and-justice"],[PB,"police"],"police lighting"),
(["finance","crime-and-justice"],[PB,"police","prisons"],"prisoner expenses"),
(["finance","crime-and-justice"],[PB,"police"],"police maintenance"),
(["finance","crime-and-justice"],[PB,"courts","police"],"mixed court"),
(["finance","crime-and-justice"],[PB,"courts","offences-and-convictions"],"court fines deducted"),
(["finance","crime-and-justice"],[PB,"police"],"police stores"),
(["finance","health"],[PB,"public-health"],"health office pay"),
(["finance","health"],[PB,"epidemics","public-health"],"plague prevention"),
(["finance","health"],[PB,"public-health"],"mosquito and fly"),
(["finance","health"],[PB,"public-health"],"health dept receipts"),
]+[(["finance","health"],[PB,"medical-services"],"hospital budget")]*8+[
(["finance","health"],[PB,"medical-services"],"hospital pay details"),
(["finance","health"],[PB,"medical-services"],"hospital allocation"),
(["finance","health"],[PB,"public-health"],"cemeteries mortuary"),
(["finance","health"],[PB,"recreation-and-amusements"],"swimming baths"),
(["finance","health"],[PB,"medical-services","quarantine"],"port health, hospital grants"),
(["finance","health"],[PB,"medical-services","pharmaceuticals"],"health stores"),
(["finance","utilities"],[PB,"construction"],"public works general"),
(["finance","utilities"],[PB,"construction"],"buildings upkeep"),
(["finance","utilities"],[PB,"rivers-and-waterways","roads-and-bridges"],"creeks, bridges"),
(["finance","utilities"],[PB,"water-and-sewerage"],"drainage"),
(["finance","utilities"],[PB,"water-and-sewerage"],"sewerage"),
(["finance","health"],[PB,"public-health"],"refuse disposal"),
(["finance","transportation"],[PB,"roads-and-bridges"],"road maintenance"),
]
RB=["finance","transportation"]
E_=["finance","education"]
b12=[
(RB,[PB,"roads-and-bridges"],"road cleansing"),
(["finance","utilities"],[PB,"electricity","gas"],"lighting"),
(["finance","culture"],[PB,"recreation-and-amusements"],"parks"),
(["finance","government"],[PB],"PWD extra-departmental"),
(RB,[PB,"roads-and-bridges"],"PWD stores rollers trucks"),
(["finance","culture"],[PB,"arts-and-music"],"orchestra"),
(["finance","culture"],[PB,"arts-and-music"],"orchestra stores"),
(["finance","culture"],[PB,"libraries"],"public library"),
]+[(E_,["education-finance","schools-and-pupils"],"school budget")]*16+[
(E_,["education-finance","schools-and-pupils"],"grants in aid to schools"),
(["finance","government"],[PB],"treasurer office"),
(["finance","government"],[PB],"compradore office"),
(["finance","government"],[PB],"finance stores"),
(["finance","government"],[PB,"government-offices"],"secretary office"),
(["finance","government"],[PB,"government-offices"],"revenue office"),
(["finance","government"],[PB],"secretariat stores"),
(["finance","government"],[PB,"government-offices"],"commissioner general"),
(["finance","government"],[PB],"commissioner stores"),
(["finance","government"],[PB],"general charges"),
(["finance","government"],[PB,"insurance-and-pensions"],"pensions"),
(["finance","welfare"],[PB,"charitable-institutions"],"grants in aid"),
(["finance","economy"],[PB,"real-estate"],"rent of properties"),
(["finance"],[PB,"public-debt"],"interest, brokerage"),
(["finance"],["public-debt",PB],"debenture redemption"),
(["finance"],["public-debt",PB],"loan proceeds income"),
]
v=json.load(open('vocabulary.json'));T={t['id'] for t in v['topics']};G={t['id'] for t in v['tags']}
for n,L in (('b11',b11),('b12',b12)):
    ins=json.load(open(B+'batches/%s.json'%n)); assert len(ins)==len(L),(n,len(ins),len(L))
    out=[]
    for r,(t,g,w) in zip(ins,L):
        assert set(t)<=T and set(g)<=G,(t,g)
        out.append({"key":r['key'],"topics":t,"tags":g,"flags":[],"why":w})
    import os; os.makedirs(B+'results',exist_ok=True)
    json.dump(out,open(B+'results/%s.json'%n,'w'),ensure_ascii=False,indent=1)
    print(n,len(out))
