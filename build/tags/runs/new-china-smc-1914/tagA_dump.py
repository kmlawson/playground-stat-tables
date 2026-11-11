import json,sys
d=json.load(open(f'batches/{sys.argv[1]}.json'))
for i,r in enumerate(d):
    print(i,r['key'].split(':')[1],'|',r['title'],'|',r.get('en') if isinstance(r.get('en'),str) else '', '|',r['chapter'],'|',(r.get('caption_extra') or '')[:80])
    for p in r['parts'][:2]:
        print('   ',(p.get('label') or '')[:50],'C:',[c[:25] for c in p['columns'][:6]],'R:',[c[:25] for c in p['row_labels'][:5]],p['rows'])
    if r.get('prior'):print('   prior',r['prior'])
