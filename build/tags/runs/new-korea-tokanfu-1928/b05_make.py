import json
d=json.load(open('batches/b05.json'))
F,T,R='finance','trade','transportation'
m={
139:([F],['banking','agricultural-credit']),140:None}
spec=[
([F],['agricultural-credit','banking'],'AgInd bank borrowings'),
([F],['agricultural-credit','savings-and-loans'],'AgInd bank loans'),
([F],['agricultural-credit','savings-and-loans'],'loans by purpose'),
([F],['banking','savings-and-loans'],'deposits with banks'),
([F],['banking'],'exchange business'),
([F],['mutual-credit','banking'],'financial assoc federation'),
([F],['mutual-credit','banking'],'federation yearly'),
([F],['mutual-credit','banking'],'financial assoc'),
([F],['mutual-credit','banking'],'financial assoc yearly'),
([F],['mutual-credit'],'mujin'),
([F],['banking'],'clearing house'),
([F],['interest-rates','banking'],'BoC rates'),
([F],['interest-rates','banking'],'industrial bank rates'),
([F],['interest-rates','banking'],'ordinary bank rates'),
([F],['interest-rates','mutual-credit'],'federation rates'),
([F],['interest-rates','mutual-credit'],'assoc rates'),
([F],['interest-rates'],'moneylender rates'),
([T],['foreign-trade','intra-imperial-trade'],'trade value'),
([T],['foreign-trade','ports'],'trade by port'),
([T],['foreign-trade'],'trade by country'),
([T],['foreign-trade'],'trade by month'),
([T],['exports'],'main exports'),
([T],['imports'],'main imports'),
([T],['gold','silver'],'gold silver trade'),
([R,T],['shipping'],'vessels by nationality'),
([T,F],['customs-revenue'],'customs revenue'),
([T],[],'bonded warehouse goods'),
([R],['railways'],'mileage stations'),
([R],['railways'],'land rolling stock'),
([R],['railways'],'passenger freight traffic'),
([R],['railways'],'train operating'),
([R,F],['railways'],'transport revenue'),
([R],['railways'],'through traffic'),
([R],['railways'],'freight tonnage'),
([R],['railways'],'station traffic'),
([R,F],['railways'],'construction expenditure'),
([R,F],['railways'],'construction costs'),
([R,F],['railways'],'repair expenditure'),
([R,F],['railways'],'revenue and expenditure'),
([R,F],['railways'],'investment'),
]
assert len(spec)==len(d)==40
out=[{"key":r['key'],"topics":s[0],"tags":s[1],"flags":[],"why":s[2]} for r,s in zip(d,spec)]
import os;os.makedirs('results',exist_ok=True)
json.dump(out,open('results/b05.json','w'),ensure_ascii=False,indent=1)
v=json.load(open('../../vocabulary.json'));ids={t['id'] for t in v['tags']}|{t['id'] for t in v['topics']}
print(all(i in ids for o in out for i in o['topics']+o['tags']),sum(1 for o in out if o['tags']))
