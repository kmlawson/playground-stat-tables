import json,sys
b=json.load(open(f'batches/b{int(sys.argv[1]):02d}.json'))
for i,r in enumerate(b):
    p=r['parts']
    cols=[c for x in p[:1] for c in x['columns']][:4]
    rl=[c for x in p[:1] for c in x['row_labels']][:3]
    print(i,'|',r['title'][:75],'|',r['chapter'][:28],'|',','.join(cols)[:50],'|',','.join(rl)[:40])
