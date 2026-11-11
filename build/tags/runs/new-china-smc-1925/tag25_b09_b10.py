import json
V=json.load(open('../../vocabulary.json'))
T={t['id'] for t in V['topics']}; G={t['id'] for t in V['tags']}
E=(['utilities'],['electricity'])
EF=(['finance','utilities'],['electricity','public-budgets'])
PB=(['finance'],['public-budgets'])
m={}
for k in 'p0367_1 p0367_2 p0368_1 p0369_1 p0371_1 p0371_2 p0371_3 p0371_4 p0372_1 p0372_2 p0372_3 p0373_1 p0374_1 p0375_1 p0376_1 p0380_1'.split(): m[k]=E
for k in 'p0381_1 p0381_2 p0382_1 p0386_1 p0386_2 p0386_3 p0387_1 p0388_1 p0389_1 p0391_1 p0391_2 p0391_3 p0393_1 p0394_1 p0395_1'.split(): m[k]=EF
m['p0393_1']=(['finance','utilities'],['electricity','public-debt'])
m['p0393_2']=(['finance','utilities'],['public-debt','electricity'])
m['p0391_4']=(['finance','utilities'],['public-debt','electricity'])
m['p0391_5']=EF
m['p0368_1']=m['p0369_1']=(['utilities'],['electricity'])
for k in 'p0398_1 p0398_2 p0398_3 p0399_2 p0400_2 p0402_1 p0402_2 p0404_2 p0409_3 p0411_1 p0418_3 p0418_4'.split(): m[k]=PB
m['p0399_1']=(['finance'],['public-budgets','police'])
m['p0400_1']=(['finance'],['public-budgets','riots-and-civil-unrest'])
m['p0403_1']=(['finance'],['public-debt','securities-and-investment'])
m['p0403_2']=m['p0403_3']=(['finance'],['public-debt'])
m['p0403_4']=m['p0404_1']=(['finance'],['public-debt','securities-and-investment'])
m['p0405_1']=(['finance'],['taxation','real-estate'])
m['p0405_2']=(['finance'],['taxation','public-budgets'])
m['p0406_1']=PB
m['p0406_2']=m['p0406_3']=(['finance'],['taxation','real-estate'])
m['p0407_1']=(['finance','transportation'],['ports','public-budgets'])
m['p0407_2']=(['transportation','finance'],['road-transport','taxation'])
m['p0407_3']=(['transportation'],['road-transport'])
m['p0408_1']=m['p0414_1']=m['p0415_1']=m['p0417_6']=(['finance'],['taxation','public-budgets'])
m['p0408_2']=(['finance','transportation'],['road-transport','taxation'])
m['p0409_1']=(['finance'],['markets-and-exchanges','public-budgets'])
m['p0409_2']=(['finance','population'],['population-totals','public-budgets'])
m['p0412_1']=m['p0413_1']=(['finance'],['taxation','real-estate'])
m['p0417_1']=(['finance'],['taxation','land-tax'])
m['p0417_2']=m['p0417_3']=(['finance'],['taxation','public-budgets'])
m['p0417_4']=(['finance'],['taxation','advertising'])
m['p0417_5']=(['finance','transportation'],['ports','public-budgets'])
m['p0418_1']=(['finance'],['public-property','markets-and-exchanges'])
m['p0418_2']=(['finance'],['public-property','securities-and-investment'])
m['p0419_1']=m['p0419_2']=(['finance','military'],['public-budgets','militias-and-volunteer-forces'])
m['p0420_1']=(['finance','disasters'],['public-budgets','firefighting'])
for b in ['b09','b10']:
    d=json.load(open(f'batches/{b}.json')); out=[]
    for r in d:
        t,g=m[r['key'].split(':')[1]]
        assert set(t)<=T and set(g)<=G
        out.append({'key':r['key'],'topics':t,'tags':g,'flags':[],'why':r['title'][:60]})
    json.dump(out,open(f'results/{b}.json','w'),ensure_ascii=False,indent=1)
    print(b,len(out),sum(1 for o in out if o['tags']))
