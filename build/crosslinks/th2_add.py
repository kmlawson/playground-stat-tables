import json
S='korea-tokanfu-1922-2/'
A={"Farm households":["p0009_1"],"Cultivated land area":["p0008_1"],"Rice acreage and yield":["p0010_1"],"Barley and wheat acreage and yield":["p0011_1"],"Pulses acreage and yield":["p0012_1"],"Miscellaneous grains":["p0013_1"],"Industrial crops":["p0014_1"],"Vegetables":["p0016_1"],"Fruit trees":["p0017_1"],"Green manure crops":["p0017_2"],"Domestic silkworms and mulberry fields":["p0018_1"],"Tussah silkworms":["p0019_1"],"Cooperative silkworm rearing":["p0019_3"],"Silkworm egg production":["p0020_1"],"Mulberry seedling production":["p0020_2"],"Breeding bulls by age":["p0021_1"],"Cattle births and deaths":["p0023_2"],"Slaughterhouses":["p0024_1"],"Livestock products":["p0025_1"],"Oriental Development Company business":["p0026_3"],"Oriental Development Company settlers and allotted land":["p0026_4"],"Livestock numbers":["p0023_1"],"State wasteland leases":["p0025_2"],"State wasteland leases by purpose":["p0026_2"]}
F={"Forest area":["p0030_1"],"Protection forests":["p0030_2"],"Commemorative tree planting":["p0033_2"],"Tree nurseries":["p0034_1"],"State afforestation":["p0033_1"],"Local and private afforestation":["p0033_3"],"Forestry station timber purchases and sales":["p0040_2"],"Seedling and seed distribution":["p0036_1"],"Private nursery seedlings":["p0038_1"],"School forests":["p0038_2"],"Forestry station felling, rafting and sawing":["p0039_1","p0040_1"],"Hunting licences":["p0040_3"]}
W={"Fishery households and population":["p0043_1"],"Fishery vessels":["p0044_1"],"Fishing gear":["p0045_1"],"Fishing boats and catch":["p0047_1"],"Catch by species":["p0048_1"],"Aquaculture":["p0049_1"],"Marine products by type":["p0050_1"],"Fish markets":["p0050_3"],"Fishery applications and licences":["p0046_1"],"Whaling":["p0050_2"],"Fishing associations from Japan":["p0051_2"],"State salt production":["p0051_1"],"Salt imports and shipments":["p0052_1"]}
def ed(m):
    return 1922.5 if '1922' in m else int(m.split('-')[2].split('/')[0])
for n,M in (('agriculture',A),('forestry',F),('fisheries',W)):
    p=f'families/korea-tokei--{n}.json'; d=json.load(open(p)); fam=0;added=0
    for f in d['families']:
        if f['label'] in M and not any('1922' in m for m in f['members']):
            f['members']+= [S+i for i in M[f['label']]]
            f['members']=sorted(f['members'],key=ed); added+=len(M[f['label']])
        fam+=any('1922' in m for m in f['members'])
    json.dump(d,open(p,'w'),ensure_ascii=False,indent=1)
    json.load(open(p)); print(n,len(d['families']),fam,added)
