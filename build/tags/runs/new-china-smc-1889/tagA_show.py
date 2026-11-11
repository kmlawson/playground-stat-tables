import json,sys
for b in sys.argv[1:]:
    for i,r in enumerate(json.load(open(f'batches/{b}.json'))):
        p=r.get('prior') or {}
        cols=[c for pt in r['parts'][:2] for c in pt['columns']][:6]
        rl=[x for pt in r['parts'][:2] for x in pt['row_labels']][:5]
        print(b,i,r['key'].split(':')[1],'|',r['title'][:70],'|',r['chapter'][:30],'|',(r.get('caption_extra') or '')[:60],'|C',cols,'|R',rl,'|P',p.get('topics'),p.get('tags'))
