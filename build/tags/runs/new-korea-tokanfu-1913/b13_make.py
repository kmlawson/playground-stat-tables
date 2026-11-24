import json
d=json.load(open('batches/b13.json'))
F=['finance']
S={ # suffix: (topics,tags,why)
'p0385_1':(['welfare'],['poor-relief'],'relief cost sick travellers'),
'p0386_1':(['welfare'],[],'handling dead travellers cost'),
'p0386_2':(['welfare'],['charitable-institutions'],'Red Cross members'),
'p0387_1':(['welfare'],['charitable-institutions'],'Patriotic Women members'),
'p0387_2':(['welfare','disasters'],['disaster-relief'],'imperial relief grants, casualties'),
'p0388_1':(F+['government'],['public-budgets'],'special account revenue/expenditure'),
'p0388_2':(F+['government'],['public-budgets'],'multi-year budget comparison'),
'p0389_1':(F+['government'],['public-budgets'],'revenue budget'),
'p0389_2':(F+['government'],['public-budgets'],'expenditure budget'),
'p0390_1':(F+['transportation'],['public-budgets'],'railway supplies fund account'),
'p0390_2':(F+['forestry'],['public-budgets'],'forestry special account'),
'p0391_1':(F+['forestry'],['public-budgets'],'forestry profit-loss'),
'p0391_2':(F+['health'],['public-budgets'],'hospital special account'),
'p0391_3':(F+['health'],['public-budgets'],'hospital funds account'),
'p0391_4':(F+['government'],['public-budgets'],'continuing expenditures'),
'p0391_5':(F+['agriculture'],['land-tax'],'kyol and tax amount'),
'p0392_1':(F+['agriculture'],['land-tax'],'taxed urban land'),
'p0392_2':(F+['agriculture'],['land-tax'],'wasteland by kyol'),
'p0393_1':(F+['agriculture'],['land-tax'],'crop failure land tax'),
'p0394_1':(['agriculture','finance'],['land-tenure'],'landowners by holding'),
'p0394_2':(['finance','agriculture'],['land-tax'],'landowners by tax paid'),
'p0394_3':(['agriculture','finance'],['land-registration'],'land parcel changes'),
'p0394_4':(F,['head-tax'],'household tax'),
'p0395_1':(F,['taxation'],'house tax'),
'p0395_2':(F,['taxation'],'house tax reductions'),
'p0396_1':(F+['manufacturing'],['taxation','alcohol'],'liquor tax'),
'p0397_1':(F+['manufacturing'],['taxation','alcohol'],'liquor tax'),
'p0398_1':(F+['manufacturing'],['taxation','tobacco'],'tobacco tax'),
'p0398_2':(F+['mining'],['taxation','mining-rights-and-concessions'],'mining area tax'),
'p0399_1':(F+['mining'],['taxation','mineral-production'],'mining output tax'),
'p0399_2':(F+['mining'],['taxation'],'placer mining tax'),
'p0400_1':(F+['mining'],['salt-tax','salt'],'salt tax and output'),
'p0400_2':(F+['transportation'],['taxation','shipping'],'vessel tax'),
'p0400_3':(F+['agriculture'],['taxation','ginseng'],'ginseng tax'),
'p0401_1':(F+['fisheries'],['taxation','fishing-rights-and-licences'],'fishery tax'),
'p0401_2':(F+['fisheries'],['taxation','fishing-rights-and-licences'],'licensed fisheries tax'),
'p0401_3':(F+['fisheries'],['taxation','fishing-rights-and-licences'],'permitted fisheries tax'),
'p0402_1':(F+['fisheries'],['taxation','fishing-rights-and-licences'],'notified fisheries tax'),
'p0402_2':(F+['agriculture'],['public-property','land-tenure'],'post-station land leases'),
'p0403_1':(F+['agriculture'],['public-property','land-tenure'],'post-station land leases by category'),
}
out=[]
for r in d:
    t,g,w=S[r['key'].split(':')[1]]
    out.append({'key':r['key'],'topics':t[:2],'tags':g,'flags':[],'why':w})
v=json.load(open('../../vocabulary.json'))
ids={x['id'] for x in v['tags']}|{x['id'] for x in v['topics']}
for o in out:
    for i in o['topics']+o['tags']: assert i in ids,i
assert len(out)==len(d)
json.dump(out,open('results/b13.json','w'),ensure_ascii=False,indent=1)
print(len(out),sum(1 for o in out if o['tags']))
