"""Merge the 1919 statistical annual into the existing korea-tokei series (1908, 1939), reusing the 1919-1939 families
made for the short-lived korea-tokanfu series (TF1-TF5, 2026-11-24). Run once."""
import json,glob,os,re
A,B,C='korea-tokanfu-1908','korea-tokanfu-1919','korea-tokanfu-1939'
order={A:0,B:1,C:2}
TF2K={'land':'land-and-climate','population':'population','shrines-and-education':'education','religion-and-social-work':'social-affairs',
 'police':'police','prisons':'prisons','courts-and-registration':'justice','commerce-and-finance':'banking-and-commerce',
 'foreign-trade':'foreign-trade','railways':'railways','communications':'communications','public-finance':'public-finance',
 'officials-and-pensions':'officials'}
K={f[len('families/korea-tokei--'):-5]: json.load(open(f)) for f in glob.glob('families/korea-tokei--*.json')}
where={}
for t,d in K.items():
    for i,fam in enumerate(d['families']):
        for mm in fam['members']: where[mm]=(t,i)
added=newf=0; log=[]
for f in sorted(glob.glob('families/korea-tokanfu--*.json')):
    tf=f[len('families/korea-tokanfu--'):-5]; d=json.load(open(f)); kt=TF2K.get(tf,tf)
    if kt not in K: K[kt]={'listing':'korea-tokei--'+kt,'families':[]}
    for fam in d['families']:
        m19=[x for x in fam['members'] if x.startswith(B+'/')]; m39=[x for x in fam['members'] if x.startswith(C+'/')]
        hit=[where[x] for x in m39 if x in where]
        if hit:
            t,i=hit[0]; tgt=K[t]['families'][i]
            for x in m19:
                if x not in where: tgt['members'].append(x); where[x]=(t,i); added+=1
            if len(set(hit))>1: log.append(f'{fam["label"]}: 1939 members in {len(set(hit))} korea-tokei families; 1919 added to the first')
        else:
            mem=[x for x in fam['members'] if x not in where]
            if len({x.split('/')[0] for x in mem})>=2:
                K[kt]['families'].append({'label':fam['label'],'members':mem,**({'note':fam['note']} if fam.get('note') else {})})
                for x in mem: where[x]=(kt,len(K[kt]['families'])-1)
                newf+=1; added+=sum(1 for x in mem if x.startswith(B))
for t,d in K.items():
    for fam in d['families']: fam['members'].sort(key=lambda x:order.get(x.split('/')[0],9))
    json.dump(d,open(f'families/korea-tokei--{t}.json','w'),ensure_ascii=False,indent=1)
print('1919 tables placed',added,'new families',newf); print('\n'.join(log))
