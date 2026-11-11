import json,sys
for n in sys.argv[1:]:
    for i,r in enumerate(json.load(open(f'batches/b{n}.json'))):
        p=r['parts']
        cols=[c for x in p[:2] for c in x['columns']][:8]
        rows=[c for x in p[:1] for c in x['row_labels']][:6]
        print(f"{n}.{i} {r['key'].split(':')[1]}|{r['title']}|{r['chapter']}|{(r.get('caption_extra') or '')[:50]}|C:{';'.join(cols)[:70]}|R:{';'.join(rows)[:70]}|pr:{r.get('prior') and (r['prior'].get('topics'),r['prior'].get('tags'))}")
