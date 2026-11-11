import json,sys,os
HERE=os.path.dirname(os.path.abspath(__file__))
V=json.load(open(os.path.join(HERE,'..','..','vocabulary.json')))
TOP={t if isinstance(t,str) else t['id'] for t in V['topics']}
g=V['tags']
TAG={x['id'] for x in g} if isinstance(g,list) else set(g)
def write(b,M):
    inp=json.load(open(f'{HERE}/batches/{b}.json'))
    out=[]
    for r in inp:
        s=r['key'].split(':')[1]
        t,g_,f,w=M[s]
        t=t.split(); g_=g_.split()
        assert all(x in TOP for x in t),(s,t)
        assert all(x in TAG for x in g_),(s,g_)
        assert 1<=len(t)<=2 and len(g_)<=3,s
        out.append(dict(key=r['key'],topics=t,tags=g_,flags=['text-tables'] if f else [],why=w))
    os.makedirs(HERE+'/results',exist_ok=True)
    json.dump(out,open(f'{HERE}/results/{b}.json','w'),ensure_ascii=False,indent=1)
    print(b,len(out),sum(1 for o in out if o['tags']))
