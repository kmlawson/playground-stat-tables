import json,sys
for n in sys.argv[1:]:
    for i,r in enumerate(json.load(open(f'batches/{n}.json'))):
        ps=[(p['label'],(p['columns'] or [])[:7],(p['row_labels'] or [])[:5],p['rows']) for p in r['parts']][:2]
        print(n,i,r['key'].split(':')[1],'|',r['title'],'|',r.get('en'),'|',r['chapter'],'|',(r.get('caption_extra') or '')[:80],'|prior',r.get('prior'),'|',json.dumps(ps,ensure_ascii=False)[:330])
