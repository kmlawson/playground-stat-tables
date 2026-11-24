import json
d=json.load(open('batches/b07.json'))
T='transportation';C='communications';F='finance'
m={
'p0175_1':([T],['railways'],'railway construction costs by line'),
'p0176_1':([T],['railways'],'railway repair expenditure'),
'p0177_1':([T,F],['railways'],'railway revenue and expenditure'),
'p0177_2':([T],['railways','tourism'],'station hotels'),
'p0178_1':([T],['railways','warehousing'],'railway warehouse business'),
'p0178_2':([T],['transport-accidents','railways'],'railway casualties'),
'p0178_3':([T,'crime-and-justice'],['railways','offences-and-convictions'],'railway law offenders'),
'p0178_4':([T,'welfare'],['railways','insurance-and-pensions'],'railway staff relief association'),
'p0179_1':([T],['railways','trams'],'tram and light railway companies'),
'p0179_2':([T],['railways','trams'],'tram/light rail traffic'),
'p0180_1':([T],['railways','trams'],'tram/light rail construction cost'),
'p0180_2':([T,F],['railways','trams'],'tram/light rail revenue'),
'p0181_1':([T],['navigation-aids'],'lighthouses and beacons'),
'p0181_2':([T],['shipping','navigation-aids'],'ships passing lighted coasts'),
'p0181_3':([T],['shipping','inland-navigation'],'Yalu pilotage ships'),
'p0181_4':([T],['shipping'],'registered vessels'),
'p0181_5':([T],['shipping'],'unregistered vessels'),
'p0181_6':([T],['shipping'],'ordered shipping routes'),
'p0182_1':([T],['shipping'],'ferry list'),
'p0182_2':([T],['shipping'],'ferry passengers freight fares'),
'p0182_3':([T],['transport-accidents','shipping'],'shipwrecks'),
'p0184_1':([C],['postal-services'],'post/telegraph offices by province'),
'p0184_2':([C],['postal-services'],'postal business'),
'p0184_3':([C],['postal-services'],'postal routes'),
'p0185_1':([C],['postal-services'],'ordinary mail'),
'p0186_1':([C],['postal-services'],'special mail'),
'p0186_2':([C],['postal-services'],'parcel post'),
'p0187_1':([C,F],['postal-remittances'],'domestic money orders'),
'p0188_1':([C,F],['postal-remittances'],'international money orders'),
'p0188_2':([C],['postal-services'],'postal money collection'),
'p0188_3':([F,C],['savings-and-loans','nationality-and-ethnicity'],'postal savings by nationality'),
'p0188_4':([F,C],['savings-and-loans'],'postal savings deposits/withdrawals'),
'p0189_1':([F,C],['savings-and-loans','occupations'],'postal savings by occupation'),
'p0189_2':([F,C],['securities-and-investment'],'securities via post offices'),
'p0189_3':([F,C],['savings-and-loans'],'postal giro accounts'),
'p0190_1':([C],['telegraph'],'telegraph lines'),
'p0190_2':([C],['telegraph'],'telegrams'),
'p0191_1':([C],['telephone'],'telephone lines'),
'p0192_1':([C],['telephone'],'local calls'),
'p0193_1':([C],['telephone'],'trunk calls'),
}
out=[]
for r in d:
    k=r['key'].split(':')[1];t,g,w=m[k]
    out.append({'key':r['key'],'topics':t,'tags':g,'flags':[],'why':w})
json.dump(out,open('results/b07.json','w') if __import__('os').makedirs('results',exist_ok=True) is None else None,ensure_ascii=False,indent=1)
print(len(out),sum(1 for o in out if o['tags']))
