import json,sys
v=json.load(open('../../vocabulary.json'))
T={t['id'] for t in v['topics']};G={t['id'] for t in v['tags']}
for n in sys.argv[1:]:
    b=json.load(open(f'batches/{n}.json'));o=json.load(open(f'results/{n}.json'))
    assert len(b)==len(o),n
    for r,x in zip(b,o):
        assert r['key']==x['key']
        assert 1<=len(x['topics'])<=2 and set(x['topics'])<=T,x
        assert len(x['tags'])<=3 and set(x['tags'])<=G,x
    print(n,len(o),sum(1 for x in o if x['tags']))
