import json
def cls(r):
    t=r['title']; k=r['key']
    T=lambda *w: any(x in t for x in w)
    if T('Educational Department','Public School for Girls — Stock') or T('Rent of Municipal Properties and Leased Premises — Public School','Thomas Hanbury School for Boys'):
        if 'Rent of' in t: return ['finance','education'],['public-budgets','education-finance'],'school premises rent'
        return ['education','finance'],['education-finance','public-budgets'],'school budget'
    if T('Public Band'): 
        if 'Summary' in t: return ['finance','culture'],['public-budgets'],'summary band/library'
        return ['finance','culture'],['public-budgets'],'band budget'
    if T('Public Library'): return ['finance','culture'],['public-budgets','libraries'],'library budget'
    if T('Parks and Open Spaces','Stock and Stores','Public Works Department'):
        return ['finance','government'],['public-budgets'],'PWD budget'
    if T('Volunteer Corps'): return ['finance','military'],['public-budgets','militias-and-volunteer-forces'],'volunteer corps rent'
    if T('Police Force'): return ['finance','crime-and-justice'],['public-budgets','police'],'police budget'
    if T('Health Department'): return ['finance','health'],['public-budgets'],'health budget'
    if T('Fire Brigade'): return ['finance','disasters'],['public-budgets','firefighting'],'fire brigade budget'
    if T('Interest, Brokerage','Redemption of Debentures'): return ['finance'],['public-debt','public-budgets'],'loan interest/redemption'
    if T('Bridges','Drainage','Landing Stages','Roads','Land'): 
        tg={'Bridges':'roads-and-bridges','Drainage':'water-and-sewerage','Landing Stages':'ports','Roads':'roads-and-bridges'}
        for a,b in tg.items():
            if t.endswith(a): return ['finance','transportation' if b!='water-and-sewerage' else 'utilities'],['public-budgets',b],'extraordinary capital works'
        return ['finance'],['public-budgets'],'extraordinary expenditure'
    return ['finance'],['public-budgets'],'municipal budget'
for b in ('b14','b15'):
    d=json.load(open('batches/%s.json'%b)); out=[]
    for r in d:
        tp,tg,w=cls(r); out.append(dict(key=r['key'],topics=tp,tags=tg,flags=[],why=w))
    import os; os.makedirs('results',exist_ok=True)
    json.dump(out,open('results/%s.json'%b,'w'),ensure_ascii=False,indent=1)
    v=json.load(open('../../vocabulary.json')); ids={x['id'] for x in v['tags']}; tid={x['id'] for x in v['topics']}
    assert all(set(o['tags'])<=ids and set(o['topics'])<=tid for o in out), [o for o in out if not set(o['tags'])<=ids]
    print(b,len(out),sum(1 for o in out if o['tags']))
    for o,r in zip(out,d): print(o['key'][-8:],o['topics'],o['tags'],r['title'][-50:])
