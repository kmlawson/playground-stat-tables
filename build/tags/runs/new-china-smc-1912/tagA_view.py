import json,sys
b=json.load(open(f'batches/b{int(sys.argv[1]):02d}.json'))
for i,r in enumerate(b):
    cols=[];rows=[]
    for p in r['parts']:
        cols+=p['columns'][:4]; rows+=p['row_labels'][:4]
    pr=r.get('prior')
    print(i,r['key'].split(':')[1],'|',r['title'][:60],'|',r['chapter'][:22],'|',(r.get('caption_extra') or '')[:50],'|C:',';'.join(c[:18] for c in cols[:4]),'|R:',';'.join(x[:22] for x in rows[:4]),'|P:',(pr['topics'],pr['tags']) if pr else '')
