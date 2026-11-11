import json,sys
for b in sys.argv[1:]:
  for i,r in enumerate(json.load(open(f'batches/{b}.json'))):
    p=r['parts'][0] if r['parts'] else {}
    pr=r.get('prior')
    print(i,r['key'].split(':')[1],'|',r['title'],'|',r.get('en'),'|',r['chapter'],'|',(r.get('caption_extra') or '')[:80],'|C:',','.join(p.get('columns',[]))[:80],'|R:',','.join(p.get('row_labels',[]))[:90],'|P:',(pr['topics'],pr['tags'],pr['flags']) if pr else '')
