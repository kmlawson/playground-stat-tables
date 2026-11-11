import json
V=json.load(open('../../vocabulary.json'))
TOP={t['id'] for t in V['topics']}; TAG={t['id'] for t in V['tags']}
# (keywords all-in title lower, topics, tags, why); first match wins
R=[
(['rent of municipal properties and leased'],['finance'],['public-property','public-budgets'],'rent of premises'),
(['special permit fees'],['finance','health'],['taxation','food-inspection'],'slaughter permit fees'),
(['police medical'],['finance','health'],['public-budgets','medical-services'],'police medical'),
(['interest, brokerage'],['finance'],['public-debt','public-budgets'],'loan interest'),
(['redemption of debentures'],['finance'],['public-debt','public-budgets'],'debenture redemption'),
(['extraordinary expenditure — ','drainage','sewerage'],['finance','utilities'],['public-budgets','water-and-sewerage'],'capital drainage'),
(['landing stages'],['finance','transportation'],['public-budgets','ports'],'landing stages'),
(['extraordinary expenditure — land'],['finance'],['public-budgets','real-estate'],'land purchase'),
(['appropriations by school'],['education','finance'],['education-finance','schools-and-pupils'],'school appropriations'),
(['licence fees','motor'],['finance','transportation'],['taxation','road-transport'],'motor vehicle licence fees'),
(['licence fees','boats'],['finance','transportation'],['taxation','shipping'],'boat/carriage licence fees'),
(['licence fees','eating'],['finance'],['taxation'],'licence fees food trade'),
(['rates, taxes','licence fees'],['finance'],['taxation'],'licence fees'),
(['ammunition'],['finance','military'],['taxation','arms-and-arsenals'],'arms licence fees'),
(['bullet proof'],['finance','military'],['taxation','arms-and-arsenals'],'vest licence fees'),
(['police fees'],['finance','crime-and-justice'],['taxation','police'],'police fees'),
(['slaughterhouse','storage'],['finance','health'],['taxation','food-inspection'],'slaughterhouse fees'),
(['slaughterhouse'],['finance','health'],['taxation','food-inspection'],'slaughterhouse fees'),
(['lairage'],['finance','agriculture'],['taxation','livestock'],'lairage fees'),
(['special permit fees','export fees'],['finance','agriculture'],['taxation','livestock'],'livestock fees'),
(['export fees'],['finance','agriculture'],['taxation','livestock'],'livestock export fees'),
(['water supply'],['finance','utilities'],['taxation','water-and-sewerage'],'hide/entrail cleaning fees'),
(['market fees'],['finance','trade'],['taxation','markets-and-exchanges'],'market fees'),
(['permit fees','building'],['finance','manufacturing'],['taxation','construction'],'building permit fees'),
(['water closet'],['finance','health'],['taxation','water-and-sewerage'],'installation fees'),
(['ordinary income','land tax'],['finance'],['land-tax','public-budgets'],'land tax income'),
(['ordinary income','rates'],['finance'],['taxation','public-budgets'],'municipal rates income'),
(['wharfage'],['finance','transportation'],['taxation','ports'],'wharfage dues'),
(['ordinary income','licence'],['finance'],['taxation','public-budgets'],'licence income'),
(['ordinary income','rent'],['finance'],['public-property','public-budgets'],'rent income'),
(['public and municipal undertakings'],['finance','utilities'],['public-budgets'],'utility revenue'),
(['ordinary income'],['finance'],['public-budgets'],'income'),
(['volunteer corps','rent'],['finance','military'],['public-budgets'],'rent'),
(['volunteer'],['finance','military'],['public-budgets','militias-and-volunteer-forces'],'volunteer corps budget'),
(['fire brigade','rent'],['finance','disasters'],['public-budgets','firefighting'],'rent'),
(['fire brigade'],['finance','disasters'],['public-budgets','firefighting'],'fire brigade budget'),
(['gaols'],['finance','crime-and-justice'],['public-budgets','prisons'],'gaol budget'),
(['police'],['finance','crime-and-justice'],['public-budgets','police'],'police budget'),
(['plague'],['finance','health'],['public-budgets','epidemics'],'plague prevention'),
(['mosquito'],['finance','health'],['public-budgets','malaria'],'mosquito work'),
(['police medical'],['finance','health'],['public-budgets','medical-services'],'police medical'),
(['tuberculosis'],['finance','health'],['public-budgets','diseases'],'TB hospital'),
(['isolation'],['finance','health'],['public-budgets','epidemics'],'isolation hospital'),
(['hospitals','nursing','clinic','ambulance','health office'],['finance','health'],['public-budgets','medical-services'],'health budget'),
(['cemeteries'],['finance','health'],['public-budgets','public-health'],'cemeteries'),
(['swimming'],['finance','culture'],['public-budgets','recreation-and-amusements'],'baths'),
(['health department'],['finance','health'],['public-budgets','medical-services'],'health budget'),
(['house refuse'],['finance','utilities'],['public-budgets','water-and-sewerage'],'refuse'),
(['drainage and sewerage','drainage','sewerage'],['finance','utilities'],['public-budgets','water-and-sewerage'],'drainage'),
(['creeks'],['finance','geography'],['public-budgets','rivers-and-waterways'],'creeks'),
(['roads'],['finance','transportation'],['public-budgets','roads-and-bridges'],'roads'),
(['lighting'],['finance','utilities'],['public-budgets','electricity'],'lighting'),
(['parks'],['finance','culture'],['public-budgets','recreation-and-amusements'],'parks'),
(['public works department','buildings'],['finance'],['public-budgets','construction'],'building upkeep'),
(['orchestra'],['finance','culture'],['public-budgets','arts-and-music'],'orchestra'),
(['library'],['finance','education'],['public-budgets','libraries'],'library'),
(['grants in aid','educational'],['education','finance'],['education-finance','charitable-institutions'],'education grants'),
(['educational'],['education','finance'],['education-finance','schools-and-pupils'],'school budget'),
(['grants in aid'],['finance','welfare'],['public-budgets','charitable-institutions'],'grants'),
(['pensions'],['finance'],['insurance-and-pensions','public-budgets'],'pensions'),
(['rent of municipal'],['finance'],['public-property','public-budgets'],'rents'),
(['emergency measures'],['finance','military'],['public-budgets'],'defence works'),
(['buildings','extraordinary'],['finance'],['public-budgets','construction'],'capital buildings'),
(['loans'],['finance'],['public-debt','public-budgets'],'loans'),
]
def tag(r):
    t=r['title'].lower()
    for kw,tp,tg,w in R:
        if kw[0] in t if len(kw)==1 else (kw[0] in t and any(k in t for k in kw[1:])) :
            return tp,tg,w
    return ['finance'],['public-budgets'],'municipal budget'
for n in ('b18','b19','b20','b21'):
    b=json.load(open(f'batches/{n}.json')); out=[]
    for r in b:
        tp,tg,w=tag(r)
        assert set(tp)<=TOP and set(tg)<=TAG,(tp,tg)
        out.append({'key':r['key'],'topics':tp,'tags':tg,'flags':[],'why':w})
    json.dump(out,open(f'results/{n}.json','w'),ensure_ascii=False,indent=1)
    print(n,len(out),len(b))
    for r,o in zip(b,out): print('  ',r['title'][10:80],'->',o['tags'])
