import json,sys
# usage: ks17_add.py listing 'p0060_1=0,p0060_2=1,...'  (id = family index)
n=sys.argv[1]; fn=f'families/japan-keishicho--{n}.json'
d=json.load(open(fn)); order=['1925','1935','1937','1938','1939','1940','1942']
key=lambda m:order.index(m.split('/')[0].split('-')[-1])
c=0
for pair in sys.argv[2].split(','):
    i,f=pair.split('='); m='japan-keishicho-1938/'+i
    fam=d['families'][int(f)]
    assert m not in fam['members']
    fam['members'].append(m); fam['members'].sort(key=key); c+=1
json.dump(d,open(fn,'w'),ensure_ascii=False,indent=1)
json.load(open(fn)); print(n,len(d['families']),c)
