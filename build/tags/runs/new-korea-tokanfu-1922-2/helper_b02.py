import json
d=json.load(open('batches/b02.json'))
F=['fisheries'];M=['mining']
a={
'p0038_1':(['forestry'],['afforestation'],'private nursery seedlings'),
'p0038_2':(['forestry','education'],['afforestation','forest-area'],'school forest area planting'),
'p0039_1':(['forestry'],['timber'],'felling and sawing timber'),
'p0040_1':(['forestry'],['timber'],'timber rafting'),
'p0040_2':(['forestry','trade'],['timber'],'timber purchases and sales'),
'p0040_3':(['forestry','government'],['hunting'],'hunting licences'),
'p0042_1':(F,['fishing'],'fisheries summary'),
'p0043_1':(F,['fishing'],'fishery households'),
'p0044_1':(F,['fishing'],'fishery vessels'),
'p0045_1':(F,['fishing'],'fishing gear'),
'p0046_1':(F,['fishing-rights-and-licences'],'fishery applications licences'),
'p0047_1':(F,['fishing'],'boats out and catch'),
'p0048_1':(F,['fish-and-fish-products','fishing'],'catch by fish type'),
'p0049_1':(F,['aquaculture'],'fish and shellfish culture'),
'p0050_1':(F+['manufacturing'],['fish-and-fish-products'],'marine products manufactured'),
'p0050_2':(F,['whaling'],'whaling'),
'p0050_3':(F+['trade'],['markets-and-exchanges','fish-and-fish-products'],'fish markets'),
'p0051_1':(M+['manufacturing'],['salt'],'government salt manufacture'),
'p0051_2':(F,['fishing'],'Japanese fishing associations'),
'p0052_1':(['trade']+M,['salt'],'salt imports'),
'p0053_1':(M,['mineral-production','mining-rights-and-concessions'],'mining summary'),
'p0054_1':(M,['mining-rights-and-concessions'],'mining applications'),
'p0055_1':(M,['mining-rights-and-concessions'],'applications by mineral'),
'p0056_1':(M,['mining-rights-and-concessions'],'permits by mineral'),
'p0057_1':(M,['mining-rights-and-concessions'],'permitted claims area'),
'p0059_1':(M,['mining-rights-and-concessions'],'working and idle claims'),
'p0063_1':(M,['mining-rights-and-concessions','nationality-and-ethnicity'],'claims by nationality'),
'p0064_1':(M,['mineral-production'],'mineral output'),
'p0066_1':(M,['mineral-production','nationality-and-ethnicity'],'output by nationality'),
'p0066_2':(M,['mineral-production'],'output by mine'),
}
out=[]
for r in d:
  t,g,w=a[r['key'].split(':')[1]]
  out.append({'key':r['key'],'topics':t,'tags':g,'flags':[],'why':w})
json.dump(out,open('results/b02.json','w'),ensure_ascii=False,indent=1)
print(len(out),sum(1 for o in out if o['tags']))
