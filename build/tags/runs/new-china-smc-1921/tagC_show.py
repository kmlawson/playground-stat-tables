import json,sys
d=json.load(open('batches/%s.json'%sys.argv[1]))
for i,r in enumerate(d):
    ps=[]
    for p in r['parts']:
        ps.append('[%s|cols:%s|rows:%s|n=%s]'%(p.get('label'),';'.join(map(str,p['columns']))[:150],';'.join(map(str,p['row_labels'][:6]))[:160],p['rows']))
    print(i,r['key'].split(':')[1],'|',r['title'],'|',r['en'],'|',r['chapter'],'|',' '.join(ps[:3]),'|prior',r.get('prior'))
