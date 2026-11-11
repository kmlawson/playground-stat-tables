import json,sys
for r in json.load(open(f'batches/b{int(sys.argv[1]):02d}.json')):
    ps=[]
    for p in r['parts']:
        ps.append((p.get('label') or '')[:40]+'|'+';'.join(map(str,p['columns']))[:110]+'|'+';'.join(map(str,p['row_labels'][:8]))[:130]+f"|n{p['rows']}")
    print(r['key'].split(':')[1],'|',r['title'][:80],'|',(r.get('en') or '')[:60],'|',r['chapter'],'|',(r.get('caption_extra') or '')[:80],'|prior:',r.get('prior'))
    for x in ps[:3]: print('   ',x)
