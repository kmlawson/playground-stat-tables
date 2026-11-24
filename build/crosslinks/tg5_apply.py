import json
T='korea-tokanfu-'
def m(s):
    return [T+x if not x.startswith('korea') else x for x in s]
def apply(name, add, new):
    p=f'families/{name}.json'
    d=json.load(open(p,encoding='utf-8'))
    used={x for f in d['families'] for x in f['members']}
    n=0
    for lab,ms in add.items():
        f=[f for f in d['families'] if f['label']==lab][0]
        ms=[x for x in ms]
        assert not (set(ms)&used)
        f['members']=ms+f['members']; used|=set(ms); n+=len(ms)
    for fam in new:
        ms=fam['members']; assert not (set(ms)&used) and len({x.split('/')[0] for x in ms})>=2
        used|=set(ms); n+=len(ms); d['families'].append(fam)
    json.dump(d,open(p,'w',encoding='utf-8'),ensure_ascii=False,indent=1)
    json.load(open(p,encoding='utf-8'))
    print(name,len(d['families']),n)
a='korea-tokanfu-1913/'; b='korea-tokanfu-1919/'; c='korea-tokanfu-1939/'
def F(l,ms,note=None):
    r={'label':l,'members':ms}
    if note:r['note']=note
    return r
def A(*ids):return [a+i for i in ids]
apply('korea-tokei--fisheries',{
 'Fishery households and population':A('p0081_1'),
 'Fishery vessels':A('p0083_1'),
 'Fishing gear':A('p0085_1'),
 'Fishing boats and catch':A('p0086_2'),
 'Catch by species':A('p0086_3'),
 'Marine products by type':A('p0088_1'),
 'Fish markets':A('p0090_2'),
 'Fishery applications and licences':A('p0085_2','p0086_1'),
},[
 F('Whaling',A('p0090_1')+[b+'p0097_2']),
 F('Fishing associations from Japan',A('p0091_1')+[b+'p0097_4']),
 F('State salt production',A('p0092_2')+[b+'p0098_1']),
 F('Salt imports and shipments',A('p0093_2')+[b+'p0098_2']),
])
apply('korea-tokei--forestry',{
 'Forest area':A('p0075_1'),
 'Commemorative tree planting':A('p0076_3'),
 'Tree nurseries':A('p0077_1','p0077_2','p0077_3'),
 'State afforestation':A('p0076_1'),
 'Local and private afforestation':A('p0076_2'),
 'Forestry station timber purchases and sales':A('p0079_4','p0079_5'),
},[
 F('Seedling and seed distribution',A('p0077_4','p0077_5','p0078_1')+[b+'p0088_1'],'1913 splits by funding source.'),
 F('Private nursery seedlings',A('p0079_1')+[b+'p0089_1']),
 F('School forests',A('p0078_2')+[b+'p0090_1']),
 F('Forestry station felling, rafting and sawing',A('p0079_2','p0079_3')+[b+'p0090_2',b+'p0090_3',c+'p0050_1']),
 F('Hunting licences',A('p0080_3')+[b+'p0091_2']),
])
apply('korea-tokei--mining-and-industry',{
 'Mining applications':A('p0094_1'),
 'Permitted mining areas by mineral':A('p0095_1'),
 'Factories':A('p0099_2'),
},[
 F('Working and idle mining areas',A('p0095_2')+[b+'p0103_1']),
 F('Working and idle mining areas by nationality',A('p0096_1')+[b+'p0105_1']),
 F('Mineral output',A('p0096_2')+[b+'p0106_1']),
 F('Pyongyang Mining Office',A('p0097_1')+[b+'p0109_1']),
 F('Companies with head office in Korea',A('p0098_1')+[b+'p0110_1']),
 F('Markets',A('p0100_2')+[b+'p0115_1']),
 F('Weights and measures sellers and repairers',A('p0101_2')+[b+'p0117_1']),
 F('Weights and measures sales',A('p0101_3')+[b+'p0117_2']),
 F('Government-General Printing Office',A('p0102_2')+[b+'p0119_3']),
])
apply('korea-tokei--agriculture',{
 'Cultivated land area':A('p0062_1'),
 'Rice acreage and yield':A('p0062_2'),
 'Barley and wheat acreage and yield':A('p0063_1'),
 'Pulses acreage and yield':A('p0064_1'),
 'Miscellaneous grains':A('p0064_2'),
 'Industrial crops':A('p0065_1'),
 'Vegetables':A('p0066_1'),
 'Domestic silkworms and mulberry fields':A('p0067_2'),
 'Tussah silkworms':A('p0068_1'),
 'Cooperative silkworm rearing':A('p0068_3'),
 'Silkworm egg production':A('p0068_4'),
 'Mulberry seedling production':A('p0069_1'),
 'Breeding bulls by age':A('p0069_2','p0069_3'),
 'Cattle births and deaths':A('p0070_3'),
 'Slaughterhouses':A('p0071_2'),
 'Oriental Development Company business':A('p0073_2'),
 'Oriental Development Company settlers and allotted land':A('p0074_5'),
},[
 F('Fruit trees',A('p0066_2')+[b+'p0076_1',c+'p0035_1']),
 F('Green manure crops',A('p0067_1')+[b+'p0076_2']),
 F('Livestock numbers',A('p0070_2')+[b+'p0080_2']),
 F('Milk production',A('p0070_4')+[c+'p0039_2']),
 F('State wasteland leases',A('p0072_4')+[b+'p0082_2']),
 F('State wasteland leases by purpose',A('p0073_1')+[b+'p0083_2']),
])
