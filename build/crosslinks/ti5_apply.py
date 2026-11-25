import json
ED=['1913','1919','1922-1','1922-2','1922-3-1','1922-3-2','1928','1939']
def ek(m):
    s=m.split('/')[0].replace('korea-tokanfu-','')
    return ED.index(s) if s in ED else (len(ED)-1 if False else 99)
P='korea-tokanfu-'
def q(x): return P+x
def run(L,add,new):
    fn=f'families/{L}.json'
    d=json.load(open(fn,encoding='utf8'))
    used={m for f in d['families'] for m in f['members']}
    for i,ms in add.items():
        f=d['families'][i]
        for m in ms:
            m=q(m); assert m not in used; used.add(m)
            # insert before first member of a later edition
            e=ek(m); pos=len(f['members'])
            for j,x in enumerate(f['members']):
                if ek(x)>e: pos=j;break
            f['members'].insert(pos,m)
    for lab,ms,*note in new:
        ms=[q(m) for m in ms]
        for m in ms: assert m not in used; used.add(m)
        ms.sort(key=ek)
        f={'label':lab,'members':ms}
        if note: f['note']=note[0]
        d['families'].append(f)
    json.dump(d,open(fn,'w',encoding='utf8'),ensure_ascii=False,indent=1)
    json.load(open(fn,encoding='utf8'))

run('korea-tokei--agriculture',
 {0:['1928/p0055_2'],1:['1928/p0055_1'],2:['1928/p0055_3'],3:['1928/p0056_1'],4:['1928/p0057_1'],5:['1928/p0057_2'],
  6:['1928/p0058_1'],7:['1928/p0059_1'],8:['1928/p0060_2'],9:['1928/p0061_1'],10:['1928/p0061_3'],11:['1928/p0061_4'],
  12:['1928/p0062_1'],13:['1928/p0062_2'],14:['1928/p0063_2'],15:['1928/p0063_3'],16:['1928/p0064_1'],
  17:['1928/p0065_2'],18:['1928/p0065_3'],19:['1928/p0059_2'],20:['1928/p0060_1'],21:['1928/p0063_1'],23:['1928/p0065_1']},
 [('Agricultural training institutes',['1919/p0078_1','1922-2/p0019_2','1928/p0061_2']),
  ('Breeding bull servicing',['1919/p0079_2','1922-2/p0021_2','1928/p0062_3']),
  ('Dairy cattle by breed',['1919/p0080_1','1922-2/p0022_1']),
  ('State unreclaimed land granted and sold',['1919/p0083_1','1922-2/p0026_1'])])
run('korea-tokei--forestry',
 {0:['1928/p0066_1'],1:['1928/p0066_2'],2:['1928/p0071_1'],3:['1928/p0072_2'],4:['1928/p0068_1'],5:['1928/p0072_1'],
  6:['1928/p0074_1'],8:['1928/p0073_1'],10:['1928/p0073_2'],11:['1928/p0074_2']},
 [('State forest leases and sales',['1919/p0085_1','1922-2/p0031_1','1928/p0066_3','1939/p0049_1']),
  ('State forest land grants',['1919/p0085_2','1922-2/p0032_1','1928/p0067_1','1939/p0049_2']),
  ('Disposal of state forest products',['1919/p0086_1','1922-2/p0032_2','1928/p0067_2','1939/p0049_3']),
  ('Forest product output',['1928/p0069_1','1939/p0047_3']),
  ('Forest damage',['1928/p0070_1','1939/p0048_3'])])
run('korea-tokei--fisheries',
 {0:['1928/p0074_3'],1:['1928/p0076_1'],2:['1928/p0075_1'],3:['1928/p0078_1'],4:['1928/p0078_2'],5:['1928/p0079_1'],
  6:['1928/p0080_1'],7:['1928/p0082_2'],8:['1928/p0077_1'],9:['1928/p0082_1'],10:['1928/p0082_3'],
  11:['1928/p0083_1'],12:['1928/p0083_2']},[])
run('korea-tokei--mining-and-industry',
 {0:['1928/p0083_3','1928/p0084_1'],1:['1928/p0085_1'],2:['1928/p0087_1'],3:['1928/p0105_1'],4:['1928/p0112_1'],
  5:['1928/p0088_1'],6:['1928/p0093_1'],7:['1928/p0093_2'],9:['1928/p0098_1'],10:['1928/p0102_2'],
  11:['1928/p0104_1'],12:['1928/p0104_3'],14:['1928/p0095_1'],15:['1928/p0096_1'],16:['1928/p0102_1'],
  17:['1928/p0103_1'],18:['1928/p0119_1'],19:['1928/p0120_1']},
 [('Permitted mining claims by nationality',['1919/p0102_1','1928/p0087_2'])])
