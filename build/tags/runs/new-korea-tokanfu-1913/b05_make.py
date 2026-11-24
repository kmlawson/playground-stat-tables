import json
d=json.load(open('batches/b05.json'))
B=(['finance'],['banking'])
m={
'p0097_3':(['trade','economy'],['business-associations'],'chambers of commerce'),
'p0098_1':(['economy','finance'],['companies'],'companies by sector, capital'),
'p0099_1':(['economy','finance'],['companies'],'branch companies, capital'),
'p0099_2':(['manufacturing'],['industrial-output'],'factories, workers, power'),
'p0100_1':(['trade','economy'],['business-associations'],'trade associations'),
'p0100_2':(['trade'],['markets-and-exchanges'],'markets, sales'),
'p0101_1':(['education','manufacturing'],['vocational-education'],'industrial training institutes'),
'p0101_2':(['trade','science-and-technology'],['measurement-and-units'],'weights and measures sellers'),
'p0101_3':(['trade','science-and-technology'],['measurement-and-units'],'weights and measures sales'),
'p0101_4':(['utilities','geography'],['hydroelectricity','rivers-and-waterways'],'hydropower site survey'),
'p0102_1':(['utilities'],['electricity'],'electric utilities'),
'p0102_2':(['manufacturing','government'],['printing'],'government printing office'),
'p0103_1':(['economy','finance'],['companies'],'company particulars'),
'p0108_1':(['economy','finance'],['companies'],'branch company particulars'),
'p0111_1':(['manufacturing'],['industrial-output'],'factory particulars'),
'p0132_1':(['finance'],['banking'],'bank offices'),
'p0132_2':(['finance'],['banking'],'banks by type'),
'p0133_1':(['finance'],['banking','savings-and-loans'],'deposits by type'),
'p0133_2':(['finance'],['banking','savings-and-loans'],'deposits by month'),
'p0133_3':(['finance'],['banking','savings-and-loans'],'loans by type'),
'p0134_1':(['finance'],['banking','savings-and-loans'],'loans by month'),
'p0134_2':(['finance'],['banking','savings-and-loans'],'deposits and loans by province'),
'p0134_3':(['finance'],['banking'],'Bank of Chosen business'),
'p0135_1':(['finance'],['banking','savings-and-loans'],'Bank of Chosen deposits'),
'p0135_2':(['finance'],['banking'],'Bank of Chosen borrowings'),
'p0135_3':(['finance'],['banking','savings-and-loans'],'Bank of Chosen loans'),
'p0135_4':(['finance'],['banking'],'Bank of Chosen funds placed'),
'p0136_1':(['finance'],['banking'],'Bank of Chosen exchange business'),
'p0136_2':(['finance'],['banking','agricultural-credit'],'agri-industrial banks business'),
'p0136_3':(['finance'],['banking','savings-and-loans'],'agri-industrial bank deposits'),
'p0137_1':(['finance'],['banking'],'agri-industrial bank borrowings'),
'p0137_2':(['finance'],['banking','agricultural-credit','savings-and-loans'],'agri-industrial bank loans'),
'p0138_1':(['finance','agriculture'],['agricultural-credit','savings-and-loans'],'loans by purpose'),
'p0138_2':(['finance'],['banking'],'agri-industrial bank funds placed'),
'p0138_3':(['finance'],['banking'],'agri-industrial bank exchange'),
'p0139_1':(['finance'],['banking'],'ordinary banks business'),
'p0139_2':(['finance'],['banking','savings-and-loans'],'ordinary bank deposits'),
'p0140_1':(['finance'],['banking'],'ordinary bank borrowings'),
'p0140_2':(['finance'],['banking','savings-and-loans'],'ordinary bank loans'),
'p0140_3':(['finance'],['banking'],'ordinary bank funds placed'),
}
out=[]
for r in d:
  t,g,w=m[r['key'].split(':')[1]]
  out.append({'key':r['key'],'topics':t,'tags':g,'flags':[],'why':w})
json.dump(out,open('results/b05.json','w'),ensure_ascii=False,indent=1)
print(len(out),len(d))
