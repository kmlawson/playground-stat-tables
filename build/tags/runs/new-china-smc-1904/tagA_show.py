import json,sys
d=json.load(open('batches/b0%s.json'%sys.argv[1]))
for i,r in enumerate(d):
    ps=[]
    for p in r['parts'][:2]:
        ps.append((p.get('label') or '')[:40]+'|C:'+';'.join(str(c) for c in p['columns'][:8])[:110]+'|R:'+';'.join(str(c) for c in p['row_labels'][:7])[:110]+'|n%s'%p['rows'])
    pr=r.get('prior')
    print(i,r['key'].split(':')[1],'|',r['title'],'|',r.get('en'),'|',r['chapter'],'|',(r.get('caption_extra') or '')[:80],'|',' // '.join(ps),'|P:',(pr['topics'],pr['tags'],pr['flags']) if pr else '')
