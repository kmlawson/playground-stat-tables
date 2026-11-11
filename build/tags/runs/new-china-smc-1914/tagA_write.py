import json,sys
V=json.load(open('../../vocabulary.json'))
T={t['id'] for t in V['topics']};G={t['id'] for t in V['tags']}
def w(b,spec):
    d=json.load(open(f'batches/{b}.json'))
    assert len(d)==len(spec),(b,len(d),len(spec))
    out=[]
    for r,(tp,tg,fl,why) in zip(d,spec):
        tp=tp.split();tg=tg.split()
        assert all(x in T for x in tp) and 1<=len(tp)<=2,(r['key'],tp)
        assert all(x in G for x in tg) and len(tg)<=3,(r['key'],tg)
        out.append({"key":r['key'],"topics":tp,"tags":tg,"flags":["text-tables"] if fl else [],"why":why})
    json.dump(out,open(f'results/{b}.json','w'),ensure_ascii=False,indent=1)
    print(b,len(out),sum(1 for o in out if o['tags']))
