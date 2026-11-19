# usage: ks16_add.py X  'id=famidx' ...   | 'id=new:Label' (new family needs also 'id2' via +)  
import sys,json
n=sys.argv[1];fn=f'families/japan-keishicho--{n}.json'
d=json.load(open(fn));F=d['families'];P='japan-keishicho-'
def order(m): return int(m.split('/')[0].replace(P,''))
cnt=0
for a in sys.argv[2:]:
    i,t=a.split('=',1);m=P+'1938/'+i
    if t.startswith('new:'):
        lab,*others=t[4:].split('+')
        F.append({'label':lab,'members':sorted([m]+[P+o for o in others],key=order),'note':''});cnt+=1;continue
    f=F[int(t)]
    assert m not in f['members']
    f['members'].append(m);f['members'].sort(key=order);cnt+=1
json.dump(d,open(fn,'w'),ensure_ascii=False,indent=1)
json.load(open(fn));print(n,len(F),cnt)
