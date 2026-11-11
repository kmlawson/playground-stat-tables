import json
b=json.load(open('batches/b10.json'))
def cl(t):
    tl=t.lower()
    if 'extraordinary income' in tl:
        if 'debenture' in tl: return ["finance"],["public-debt","public-budgets"]
        return ["finance","government"],["public-budgets"]
    if 'redemption of debentures' in tl or tl.endswith('interest'): return ["finance"],["public-debt","interest-rates"]
    if 'deficit from 1916' in tl: return ["finance","government"],["public-budgets"]
    if 'public school' in tl or 'hanbury' in tl or 'polytechnic' in tl or 'educational' in tl and 'grants' not in tl:
        return ["finance","education"],["schools-and-pupils","education-finance"]
    if 'grants in aid' in tl and 'educational' in tl: return ["finance","education"],["education-finance"]
    if 'library' in tl: return ["finance","culture"],["libraries","public-budgets"]
    if 'band' in tl: return ["finance","culture"],["arts-and-music","public-budgets"]
    if 'lighting' in tl: return ["finance","utilities"],["public-budgets"]
    if 'parks' in tl: return ["finance","utilities"],["public-budgets","horticulture"]
    if 'cleansing' in tl: return ["finance","utilities"],["roads-and-bridges","public-budgets"]
    if 'rent of municipal' in tl: return ["finance","government"],["public-property","public-budgets"]
    if 'grants in aid' in tl: return ["finance","government"],["public-budgets"]
    return ["finance","government"],["public-budgets"]
out=[]
for r in b:
    t,g=cl(r['title']); out.append({"key":r['key'],"topics":t,"tags":g,"flags":[],"why":"budget line: "+r['title'].split('—')[-1].strip()[:50]})
json.dump(out,open('results/b10.json','w'),ensure_ascii=False,indent=1)
for r,o in zip(b,out): print(r['title'][-60:],o['topics'],o['tags'])
