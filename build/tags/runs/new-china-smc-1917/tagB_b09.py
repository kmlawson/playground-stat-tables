import json
b=json.load(open('batches/b09.json'))
def cl(t):
    s=t.split('—',2)[-1] if t.count('—')>=2 else t
    tl=t.lower()
    if 'ordinary income' in tl:
        if 'land tax' in tl: return ["finance"],["land-tax"]
        if 'wharfage' in tl: return ["finance","transportation"],["taxation","ports"]
        if 'licence' in tl: return ["finance"],["taxation"]
        if 'markets' in tl: return ["finance","trade"],["markets-and-exchanges","public-property"]
        if 'firemen' in tl: return ["finance"],["public-property","firefighting"]
        if 'undertakings' in tl: return ["finance","utilities"],["public-budgets"]
        return ["finance"],["public-property"]
    if 'volunteer' in tl: return ["finance","military"],["militias-and-volunteer-forces","public-budgets"]
    if 'fire brigade' in tl: return ["finance","disasters"],["firefighting","public-budgets"]
    if 'police' in tl and 'buildings' not in tl and 'hospital' not in tl: return ["finance","crime-and-justice"],["police","public-budgets"]
    if 'plague' in tl: return ["finance","health"],["epidemics","public-budgets"]
    if 'mosquito' in tl: return ["finance","health"],["malaria","public-budgets"]
    if 'hospital' in tl or 'nursing' in tl or 'sanatorium' in tl: return ["finance","health"],["medical-services","public-budgets"]
    if 'health' in tl and 'buildings' not in tl: return ["finance","health"],["public-health","public-budgets"]
    if 'cemeter' in tl: return ["finance","health"],["public-health","public-budgets"]
    if 'swimming' in tl: return ["finance","sport"],["sports-organisations-and-facilities","public-budgets"]
    if 'buildings' in tl: return ["finance","utilities"],["construction","public-budgets"]
    if 'creeks' in tl: return ["finance","utilities"],["rivers-and-waterways","public-budgets"]
    if 'drainage' in tl: return ["finance","utilities"],["water-and-sewerage","public-budgets"]
    if 'roads' in tl: return ["finance","utilities"],["roads-and-bridges","public-budgets"]
    return ["finance","government"],["public-budgets"]
out=[]
for r in b:
    t,g=cl(r['title']); out.append({"key":r['key'],"topics":t,"tags":g,"flags":[],"why":"budget line: "+r['title'].split('—')[-1].strip()[:50]})
json.dump(out,open('results/b09.json','w'),ensure_ascii=False,indent=1)
for r,o in zip(b,out): print(r['title'][-70:],o['topics'],o['tags'])
