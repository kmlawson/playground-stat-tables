import json
d=json.load(open('batches/b04.json'))
B=['banking']; SL=['banking','savings-and-loans']
m={
'p0121_1':(['currency'],'note issue'),'p0121_2':(['currency'],'note issue monthly'),'p0121_3':(['currency'],'notes by denomination'),'p0121_4':(['currency','banking'],'note reserves'),
'p0122_1':(['banking'],'bank business summary'),'p0122_2':(SL,'deposits'),'p0122_3':(SL,'deposit balances monthly'),
'p0123_1':(SL,'loans'),'p0123_2':(SL,'loan balances monthly'),'p0124_1':(SL,'deposits/loans by province'),'p0124_2':(['banking'],'exchange receipts/payments'),
'p0125_1':(['banking','currency'],'Bank of Chosen'),'p0125_2':(SL,'BoC deposits'),'p0125_3':(['banking'],'BoC borrowings'),'p0125_4':(SL,'BoC loans'),
'p0126_1':(SL,'BoC loans by security'),'p0126_2':(['banking'],'BoC funds with banks'),'p0126_3':(['banking','agricultural-credit'],'Industrial Bank'),'p0126_4':(SL,'IB deposits'),'p0126_5':(['banking'],'BoC exchange'),'p0126_6':(['banking'],'IB borrowings'),
'p0127_1':(SL,'IB loans'),'p0127_2':(SL,'IB loans by security'),'p0127_3':(['banking'],'IB funds with banks'),'p0127_4':(['banking'],'IB exchange'),'p0127_5':(['banking','agricultural-credit'],'agri-industrial banks'),
'p0128_1':(['banking'],'ordinary banks'),'p0128_2':(SL,'deposits'),'p0129_1':(['banking'],'borrowings'),'p0129_2':(SL,'loans'),'p0129_3':(SL,'loans by security'),'p0129_4':(['banking'],'funds with banks'),'p0129_5':(['banking'],'exchange'),
'p0130_1':(['banking','agricultural-credit'],'financial associations'),'p0130_2':(['banking','agricultural-credit'],'financial associations yearly'),'p0130_3':(['banking','markets-and-exchanges'],'clearing houses'),
'p0131_1':(['interest-rates','banking'],'average rates'),'p0132_1':(['interest-rates','banking'],'average rates'),'p0132_2':(['interest-rates','banking'],'average rates'),'p0132_3':(['interest-rates'],'moneylender rates'),
}
out=[]
for r in d:
    t,w=m[r['key'].split(':')[1]]
    out.append({"key":r['key'],"topics":["finance"],"tags":t,"flags":[],"why":w})
json.dump(out,open('results/b04.json','w'),ensure_ascii=False,indent=1)
assert [o['key'] for o in out]==[r['key'] for r in d]
print(len(out))
