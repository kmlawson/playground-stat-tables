import json,sys
for b in sys.argv[1:]:
    for i,r in enumerate(json.load(open(f'batches/{b}.json'))):
        p=r['parts'][0] if r['parts'] else {}
        pr=r.get('prior')
        print(i,r['key'].split(':')[1],'|',r['title'][:70],'|',r['chapter'],'|',(r['caption_extra'] or '')[:90],'|C:',';'.join(p.get('columns',[])[:4])[:60],'|R:',';'.join(p.get('row_labels',[])[:3])[:50],'|P:',(pr['topics'],pr['tags']) if pr else '')
