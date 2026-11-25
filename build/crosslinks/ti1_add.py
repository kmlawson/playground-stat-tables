import json
P='korea-tokanfu-1928/p'
def ins(fam, ids):
    ms=fam['members']; new=[P[:-1]+i if False else 'korea-tokanfu-1928/'+i for i in ids]
    for n in new: assert n not in ms
    pos=len(ms)
    for k,m in enumerate(ms):
        if m.startswith('korea-tokanfu-1939'): pos=k;break
    fam['members']=ms[:pos]+new+ms[pos:]
def run(name, byidx=None, bylabel=None, newfams=()):
    fn='families/%s.json'%name
    d=json.load(open(fn)); added=0
    for fam in d['families']:
        key=fam['label']
        if bylabel and key in bylabel:
            ins(fam,bylabel[key]); added+=len(bylabel[key])
    for lab,mem,note in newfams:
        f={'label':lab,'members':mem}
        if note:f['note']=note
        d['families'].append(f); added+=1  # counted below
    json.dump(d,open(fn,'w'),ensure_ascii=False,indent=1)
    json.load(open(fn))
    return added
# monopolies
print(run('korea-tokei--monopolies',bylabel={
 'Fresh ginseng cultivation, harvest and receipts':['p0411_1','p0411_2','p0411_3'],
 'Red ginseng and ginseng products manufactured':['p0412_1'],
 'Red ginseng sales':['p0412_2']},
 newfams=[('Ginseng products manufactured and sold',['korea-tokanfu-1919/p0313_1','korea-tokanfu-1928/p0413_1'],None)]))
# officials
print(run('korea-tokei--officials',bylabel={
 'Officials and salaries':['p0365_1','p0365_2'],
 'Local officials paid from local funds':['p0366_1','p0367_1','p0367_2'],
 'Township officials':['p0367_3'],
 'Yi Household Office staff and salaries':['p0369_1'],
 'Pensions and allowances':['p0369_2'],
 'Township clerks by number per township':['p0368_1'],
 'Village and ward heads by number of villages served':['p0368_2']}))
L={
'Central government revenue and expenditure':['p0370_1'],
'Central government revenue by item':['p0371_1'],
'Central government expenditure by item':['p0371_2'],
'Outstanding national debt':['p0409_1'],
'Railway supplies fund special account':['p0372_1'],
'Land tax by province':['p0373_1'],
'Income tax by province':['p0377_1'],
'Income tax payers by amount paid':['p0378_1'],
'Liquor tax by province and type':['p0379_1','p0379_2','p0380_1','p0380_2'],
'Imported liquor tax':['p0380_4','p0380_5','p0381_1'],
'Sugar consumption tax':['p0382_1'],
'Mining taxes':['p0384_1','p0384_2'],
'National tax receipts':['p0387_1'],
'Non-tax revenue receipts':['p0389_1'],
'Revenue stamp receipts':['p0388_3'],
'Direct tax burden by city and county':['p0392_1','p0393_1'],
'Provincial revenue and expenditure':['p0395_1'],
'Provincial expenditure by item and province':['p0396_1'],
'Provincial levies by province':['p0397_1'],
'Provincial tax collection':['p0398_1'],
'City revenue budget':['p0400_1'],
'City expenditure budget':['p0400_2'],
'Township revenue budget':['p0401_1'],
'Township expenditure budget':['p0402_1'],
'Average township burden':['p0403_2'],
'School association revenue and expenditure budget':['p0403_3'],
'City debt':['p0409_2'],
'School association debt':['p0410_1'],
'Special account of the Government-General, year-to-year comparison':['p0370_2'],
'Government-General continuing expenditures':['p0372_2'],
'Urban taxed land by province':['p0373_2'],
'Landowners by land tax paid':['p0376_1','p0376_2'],
'Post-station land income receipts':['p0388_2'],
'Distraint for unpaid national taxes':['p0389_2'],
'Tax collection expenses':['p0391_1'],
'Local fund revenue by item':['p0395_2'],
'Distraint for unpaid local fund levies':['p0399_1'],
'Township levy rates':['p0403_1'],
'Water association budgets':['p0404_1'],
'Public common school revenue budgets':['p0407_1'],
'Public common school expenditure budgets':['p0408_1'],
'Confucian school property revenue and expenditure':['p0408_2'],
'Water association debt':['p0410_2'],
}
d=json.load(open('families/korea-tokei--public-finance.json'))
labs={f['label'] for f in d['families']}
assert set(L)<=labs, set(L)-labs
print(run('korea-tokei--public-finance',bylabel=L), sum(len(v) for v in L.values()), len(L))
