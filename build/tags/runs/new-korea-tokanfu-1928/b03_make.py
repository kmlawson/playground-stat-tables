import json
d=json.load(open('batches/b03.json'))
M={
'81':(['government','fisheries'],['hunting'],'hunting licences'),
'82':(['fisheries','population'],['fishing','nationality-and-ethnicity'],'fishery households by nationality'),
'83':(['fisheries'],['fishing'],'fishing gear'),
'84':(['fisheries'],['fishing'],'fishery vessels'),
'85':(['fisheries','government'],['fishing-rights-and-licences'],'fishery applications/licences'),
'86':(['fisheries'],['fishing'],'boats and catch'),
'87':(['fisheries'],['fishing','fish-and-fish-products'],'catch by species'),
'88':(['fisheries'],['aquaculture'],'aquaculture'),
'89':(['fisheries','manufacturing'],['fish-and-fish-products','food-processing'],'marine products manufactured'),
'90':(['fisheries'],['whaling'],'whaling'),
'91':(['trade','fisheries'],['markets-and-exchanges','fish-and-fish-products'],'fish markets'),
'92':(['fisheries'],['fishing','business-associations'],'migratory fishing groups'),
'93':(['mining','manufacturing'],['salt'],'government salt works'),
'94':(['trade'],['salt','intra-imperial-trade','imports'],'salt imports'),
'95':(['mining'],['mining-rights-and-concessions'],'mining applications'),
'96':(['mining'],['mining-rights-and-concessions','nationality-and-ethnicity'],'applications by mineral'),
'97':(['mining'],['mining-rights-and-concessions','nationality-and-ethnicity'],'permits by mineral'),
'98':(['mining'],['mining-rights-and-concessions'],'permitted area by mineral, province'),
'99':(['mining'],['mining-rights-and-concessions','nationality-and-ethnicity'],'permitted area by holder'),
'100':(['mining'],['mining-rights-and-concessions'],'working/idle claims'),
'101':(['mining'],['mining-rights-and-concessions','nationality-and-ethnicity'],'working/idle by holder'),
'102':(['mining'],['mineral-production'],'mineral output'),
'103':(['mining'],['mineral-production','nationality-and-ethnicity'],'output by nationality'),
'104':(['mining'],['mineral-production'],'output by mine'),
'105':(['finance','economy'],['companies','nationality-and-ethnicity'],'companies by capital'),
'106':(['finance'],['insurance-and-pensions'],'insurance'),
'107':(['trade'],['markets-and-exchanges','domestic-trade'],'markets'),
'108':(['manufacturing','trade'],['tobacco'],'tobacco consumption'),
'109':(['science-and-technology','trade'],['measurement-and-units'],'weights/measures dealers'),
'110':(['science-and-technology','trade'],['measurement-and-units'],'measuring instrument dealers'),
'111':(['science-and-technology','trade'],['measurement-and-units'],'weights/measures sales'),
'112':(['science-and-technology','trade'],['measurement-and-units'],'measuring instrument sales'),
'113':(['manufacturing'],['industrial-output'],'factories'),
'114':(['manufacturing'],['industrial-output'],'industrial output by province'),
'115':(['utilities'],['electricity','companies'],'electric utilities'),
'116':(['education','manufacturing'],['vocational-education','cottage-industries'],'industrial training institutes'),
'117':(['trade','agriculture'],['prices','rice'],'unhulled rice prices'),
'118':(['trade','agriculture'],['prices','rice'],'brown rice prices'),
'119':(['trade','agriculture'],['prices','rice'],'polished rice prices'),
'120':(['trade','agriculture'],['prices','soybeans'],'soybean prices'),
}
out=[]
for r in d:
    t,g,w=M[r['table_no']]
    out.append({'key':r['key'],'topics':t,'tags':g,'flags':['text-tables'] if r['table_no'] in('116',) and False else [],'why':w})
v=json.load(open('../../vocabulary.json'))
ids={x['id'] for x in v['tags']}|{x['id'] for x in v['topics']}
for o in out:
    for x in o['topics']+o['tags']: assert x in ids,x
assert [o['key'] for o in out]==[r['key'] for r in d]
json.dump(out,open('results/b03.json','w'),ensure_ascii=False,indent=1)
print(len(out))
