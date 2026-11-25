import json,sys
# usage: ti6_add.py X  'label=id' ...  (label existing -> append before 1939 in order; else error)
X=sys.argv[1]; f=f'families/{X}.json'
d=json.load(open(f))
order=['1908','1913','1919','1922','1928','1939']
def key(m):
    s=m.split('/')[0].replace('korea-tokanfu-','')
    for i,o in enumerate(order):
        if s.startswith(o): return i
    return 9
for a in sys.argv[2:]:
    lab,mid=a.split('=',1)
    m='korea-tokanfu-1928/'+mid
    fam=[x for x in d['families'] if x['label']==lab]
    if fam:
        fam[0]['members'].append(m); fam[0]['members'].sort(key=key)
    else:
        print('new label',lab); d['families'].append({'label':lab,'members':[m]})
json.dump(d,open(f,'w'),ensure_ascii=False,indent=1)
json.load(open(f))
