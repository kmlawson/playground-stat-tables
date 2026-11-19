import json
fn='families/china-smc--budget-general.json'
d=json.load(open(fn));F=d['families']
L={f['label']:f for f in F}
m={'Ordinary income: land tax':['p0270_1'],'Ordinary income: general municipal rate':['p0270_2','p0270_3'],
'Ordinary income: wharfage dues':['p0270_4'],'Ordinary income: licence fees':['p0270_5'],
'Budget: Police charges':['p0271_1','p0271_2','p0271_3','p0271_4','p0271_5','p0271_6']+['p0273_%d'%i for i in range(2,10)],
'Budget: Income: sanitary branch':['p0272_1'],'Budget: Police: Bubbling Well Road Station':['p0273_1'],
'Budget: Relief of the poor':['p0273_10'],'Budget: Sanitary: foreign and native hospitals':['p0275_1'],
'Budget: Sanitary: medical':['p0275_2'],'Budget: Sanitary: nuisance and market':['p0275_3'],'Budget: Water supply':['p0275_4'],
'Public Works: lighting':['p0275_5'],'Budget: Telephone lines':['p0277_1'],"Budget: Surveyor's office":['p0277_2'],
'Budget: Income: permit fees':['p0280_1'],'Budget: Income: cemeteries':['p0280_2'],'Budget: Income: local post office':['p0280_3'],
'Budget: Public Works: outside roads':['p0281_1'],'Public Works: parks and open spaces':['p0281_2'],
'Health: cemeteries, crematorium and mortuary':['p0281_3'],'Budget: Expenditure: local post office':['p0281_4'],
"Secretariat: Secretary's office":['p0283_1'],'General charges':['p0283_2'],'Budget: Stud':['p0285_1'],
'Fire Brigade expenditure':['p0285_2'],'Volunteer Corps: volunteer units':['p0285_3'],'Municipal Orchestra and Band':['p0285_4'],
'Budget: Shanghai Museum':['p0285_5'],'Public Library':['p0285_6'],'Budget: Education grants':['p0285_7'],
'Budget: Income: interest':['p0286_2'],'Budget: Income: sinking fund':['p0286_3'],'Budget: Income: stock and stores':['p0286_4'],
'Interest, brokerage etc.':['p0287_2'],'Extraordinary expenditure: loan redemption':['p0287_3'],
'Budget: Municipal loan of 1883':['p0287_4'],'Budget: Land and buildings':['p0287_5'],'Budget: Expenditure: stock and stores':['p0287_6'],
'Budget: Municipal stock and stores account':['p0287_8'],'Budget: Summary of expenditure':['p0288_1']}
n=0
for k,v in m.items():
    f=L[k]; new=['china-smc-1886/'+x for x in v]
    assert not any(x in f['members'] for x in new)
    f['members']=new+f['members'];n+=len(new)
json.dump(d,open(fn,'w'),ensure_ascii=False,indent=1);print(len(m),n)
