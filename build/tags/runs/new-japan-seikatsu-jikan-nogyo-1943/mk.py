import json,re
v=json.load(open('../../vocabulary.json'))
ids=set()
def walk(o):
    if isinstance(o,dict):
        if 'id' in o: ids.add(o['id'])
        for x in o.values(): walk(x)
    elif isinstance(o,list):
        for x in o: walk(x)
walk(v)
def cl(r):
    k=r['key'].split(':')[1]; t=r['title']; ch=r['chapter']
    if k=='p0004_1': return ["population","agriculture"],["census-and-survey-methods"],[],"survey design: districts and households"
    if k=='p0004_2': return ["labour","population"],["census-and-survey-methods"],[],"survey design: workplaces and persons"
    if k=='p0004_3': return ["science-and-technology"],["census-and-survey-methods"],[],"survey seasons and dates"
    if k=='p0004_4': return ["science-and-technology","welfare"],["census-and-survey-methods"],["text-tables"],"diary activity classification"
    if k=='p0005_1': return ["geography","agriculture"],["census-and-survey-methods"],["text-tables"],"list of surveyed villages"
    if '聽取' in ch: return ["communications","culture"],["radio"],[],"suitability of times for radio listening"
    if '消費時間' in ch: return ["welfare","labour"],["working-conditions","recreation-and-amusements"],[],"daily time budget by activity"
    return ["welfare","labour"],["working-conditions"],[],"time-of-day activity percentages, farm households"
for b in ['b01','b02','b03']:
    d=json.load(open('batches/%s.json'%b)); out=[]
    for r in d:
        t,g,f,w=cl(r)
        for x in t+g+f: assert x in ids or x=='text-tables',x
        out.append({"key":r['key'],"topics":t,"tags":g,"flags":f,"why":w})
    json.dump(out,open('results/%s.json'%b,'w'),ensure_ascii=False,indent=1)
    print(b,len(out),len(d))
