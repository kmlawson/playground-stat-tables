import json,sys
def write(b,specs):
    d=json.load(open(f'batches/{b}.json'))
    assert len(d)==len(specs),(len(d),len(specs))
    voc=json.load(open('../../vocabulary.json'))
    T={x['id'] for x in voc['topics']};G={x['id'] for x in voc['tags']}
    out=[]
    for r,s in zip(d,specs):
        top,tags,fl,why=s
        top=top.split();tags=tags.split();
        assert all(t in T for t in top),top
        assert all(t in G for t in tags),tags
        out.append({'key':r['key'],'topics':top,'tags':tags,'flags':['text-tables'] if fl else [],'why':why})
    import os;os.makedirs('results',exist_ok=True)
    json.dump(out,open(f'results/{b}.json','w'),ensure_ascii=False,indent=1)
    print(b,len(out),sum(1 for o in out if o['tags']))
