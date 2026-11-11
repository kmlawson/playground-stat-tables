import json,sys
for f in sys.argv[1:]:
    for i,r in enumerate(json.load(open(f))):
        print(f[-8:-5],i,r['key'].split(':')[1],'|',r['title'],'|',r['chapter'],'|',(r.get('caption_extra') or '')[:90],'| P:',(r.get('prior') or {}).get('topics'),(r.get('prior') or {}).get('tags'))
        for p in r['parts'][:2]:
            print('   ',p.get('label'),'C:',[str(c)[:18] for c in p['columns'][:7]],'R:',[str(c)[:20] for c in (p.get('row_labels') or [])[:6]])
