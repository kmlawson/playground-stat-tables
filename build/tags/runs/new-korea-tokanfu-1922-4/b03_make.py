import json
d=json.load(open('batches/b03.json'))
T,C,F,U,D,E_='transportation','communications','finance','utilities','disasters','education'
m={
'p0040_3':([T],['railways']),'p0041_1':([T],['railways']),'p0042_1':([T,F],['railways']),'p0044_1':([T,F],['railways']),'p0045_1':([T],['railways']),
'p0045_2':([T],['shipping']),'p0046_1':([T],['navigation-aids']),'p0046_2':([T],['shipping']),'p0047_1':([T],['shipping']),'p0047_2':([T],['shipping']),
'p0047_3':([T],['shipping']),'p0047_4':([T],['shipping']),'p0048_1':([C],['postal-services']),'p0049_1':([C],['postal-services','telegraph','telephone']),
'p0050_1':([C],['postal-services']),'p0051_1':([C],['postal-services']),'p0051_2':([C,F],['postal-remittances']),'p0052_1':([C,F],['postal-remittances']),
'p0053_1':([F,C],['savings-and-loans','postal-services']),'p0053_2':([F,C],['savings-and-loans','postal-services']),'p0053_3':([F,C],['securities-and-investment','postal-services']),
'p0054_1':([F,C],['savings-and-loans','postal-services']),'p0055_1':([C],['telegraph']),'p0055_2':([C],['telegraph']),'p0057_1':([C],['telephone']),
'p0057_2':([C],['telephone']),'p0058_1':([C],['telephone']),'p0059_1':([C,E_],['vocational-education']),
'p0061_1':([T],['roads-and-bridges']),'p0061_2':([T],['roads-and-bridges']),'p0062_1':([T],['roads-and-bridges']),'p0062_2':([F,T],['public-budgets','roads-and-bridges']),
'p0063_1':([U],['water-and-sewerage']),'p0064_1':([F,T],['public-budgets','roads-and-bridges']),'p0064_2':([T],['ports']),'p0065_1':([D,T],['floods','roads-and-bridges']),
}
out=[]
for r in d:
    t,g=m[r['key'].split(':')[1]]
    out.append({'key':r['key'],'topics':t,'tags':g,'flags':[],'why':r['en']['t'][:60]})
json.dump(out,open('results/b03.json','w'),ensure_ascii=False,indent=1)
v=json.load(open('../../vocabulary.json'));ids={x['id'] for x in v['tags']}|{x['id'] for x in v['topics']}
assert all(i in ids for o in out for i in o['topics']+o['tags']);print(len(out))
