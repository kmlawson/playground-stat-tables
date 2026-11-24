import json,re
P='korea-tokanfu-'
def ed(m):
    s=m.split('/')[0].replace(P,'')
    return int(s[:4])
def sortm(ms): return sorted(ms,key=lambda m:(ed(m),ms.index(m)))
def fam_add(name,adds,new):
    fn=f'families/korea-tokei--{name}.json'
    d=json.load(open(fn,encoding='utf-8'))
    listing=set()
    for l in open(f'listings/korea-tokei--{name}.txt',encoding='utf-8'):
        p=[x.strip() for x in l.split('|')]
        if len(p)>4: listing.add(p[0]+'/'+p[1])
    used={m for f in d['families'] for m in f['members']}
    n=0
    def chk(ms):
        for m in ms:
            assert m in listing,m
            assert m not in used,m
            used.add(m)
    for i,ms in adds.items():
        ms=[P+'1922-7/'+m for m in ms]; chk(ms)
        f=d['families'][i]; f['members']=sortm(f['members']+ms); n+=len(ms)
    for label,ms in new:
        ms=[(m if m.startswith(P) else P+'1922-7/'+m) for m in ms]
        chk(ms); d['families'].append({'label':label,'members':sortm(ms),'note':''}); n+=1
    json.dump(d,open(fn,'w',encoding='utf-8'),ensure_ascii=False,indent=1)
    json.load(open(fn,encoding='utf-8'))
    print(name,len(d['families']),n)
fam_add('education',{
1:['p0010_2'],2:['p0011_1'],3:['p0013_1','p0014_1'],4:['p0015_1'],22:['p0015_2'],5:['p0016_1'],6:['p0016_2'],
7:['p0017_2'],8:['p0018_1','p0019_1'],9:['p0020_1'],11:['p0021_1'],10:['p0021_2'],
12:['p0024_1'],13:['p0024_2'],14:['p0026_2'],15:['p0027_1'],
16:['p0028_2','p0029_2','p0032_1'],17:['p0029_1','p0031_1'],
18:['p0037_1'],19:['p0038_1'],20:['p0039_1'],28:['p0039_2'],29:['p0040_1'],0:['p0043_1']},
[('State common schools: classes, teachers and pupils',['korea-tokanfu-1919/p0250_2','p0017_1']),
('Private common schools',['korea-tokanfu-1919/p0253_1','p0022_1']),
('State higher common schools: status',['korea-tokanfu-1919/p0254_1','p0024_3']),
('State higher common schools: assets',['korea-tokanfu-1919/p0254_2','p0024_4']),
('Private higher common schools',['korea-tokanfu-1919/p0255_3','p0026_1']),
('State girls\' higher common schools: status',['korea-tokanfu-1919/p0255_1','p0027_2']),
('State girls\' higher common schools: assets',['korea-tokanfu-1919/p0255_2','p0027_3']),
('Private girls\' higher common schools',['korea-tokanfu-1919/p0255_4','p0028_1']),
('Vocational continuation schools',['p0032_2','korea-tokanfu-1939/p0171_2','korea-tokanfu-1939/p0172_1','korea-tokanfu-1939/p0172_2']),
('Keijo Medical College: status',['korea-tokanfu-1919/p0258_1','p0033_3']),
('Keijo Medical College: property',['korea-tokanfu-1919/p0258_2','p0033_4']),
('Keijo technical college: status',['korea-tokanfu-1919/p0258_3','p0034_1']),
('Keijo technical college: property',['korea-tokanfu-1919/p0258_4','p0034_2']),
('Suwon agriculture and forestry college: status',['korea-tokanfu-1919/p0258_5','p0034_3']),
('Suwon agriculture and forestry college: property',['korea-tokanfu-1919/p0258_6','p0034_4']),
('State normal schools: status',['p0036_1'.replace('p0036_1','p0035_6'),'korea-tokanfu-1939/p0174_3']),
('State normal schools: property',['p0036_2','korea-tokanfu-1939/p0174_4']),
])
fam_add('social-affairs',{10:['p0050_1'],11:['p0050_2'],12:['p0051_2'],9:['p0051_1'],13:['p0053_1'],0:['p0055_1'],1:['p0055_2'],6:['p0056_1'],8:['p0056_2'],7:['p0057_1'],5:['p0057_2'],2:['p0043_2'],3:['p0044_1'],4:['p0046_1']},[])
fam_add('officials',{0:['p0060_1','p0060_2'],1:['p0067_1'],2:['p0069_1'],5:['p0069_2'],6:['p0070_1'],3:['p0070_2'],4:['p0071_1']},[])
