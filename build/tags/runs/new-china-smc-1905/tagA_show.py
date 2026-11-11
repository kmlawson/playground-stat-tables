import json,sys
for n in sys.argv[1:]:
    for i,r in enumerate(json.load(open(f'batches/b0{n}.json'))):
        cols=[]
        for p in r['parts'][:2]:
            cols.append((p.get('label') or '')[:40]+'|'+','.join(c[:18] for c in p['columns'][:7])+'|'+','.join(x[:14] for x in p['row_labels'][:5]))
        pr=r.get('prior') or {}
        print(i,r['key'].split(':')[1],r['title'][:60],'#',(r.get('en') or '')[:50],'#',r['chapter'][:30],'##',' ## '.join(cols)[:230],'PRIOR',pr.get('topics'),pr.get('tags'),pr.get('flags'))
