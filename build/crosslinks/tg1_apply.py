import json
S13='korea-tokanfu-1913/'; S19='korea-tokanfu-1919/'; S39='korea-tokanfu-1939/'; S08='korea-tokanfu-1908/'
def load(n): return json.load(open(f'families/korea-tokei--{n}.json'))
def save(n,d): json.dump(d,open(f'families/korea-tokei--{n}.json','w'),ensure_ascii=False,indent=1); json.load(open(f'families/korea-tokei--{n}.json'))
def add(d,first,new,note=None):
    for f in d['families']:
        if first in f['members']:
            ms=f['members']
            # insert before the first 1919 member, after 1908 members
            i=next((k for k,m in enumerate(ms) if m.startswith(S19) or m.startswith(S39)),len(ms))
            f['members']=ms[:i]+[S13+x for x in new]+ms[i:]
            if note: f['note']=(f.get('note','')+' '+note).strip()
            return
    raise KeyError(first)
# monopolies
d=load('monopolies')
add(d,S19+'p0311_1',['p0430_1','p0430_2','p0431_1'],'1913 also splits the table in three.')
add(d,S19+'p0312_2',['p0432_1'])
add(d,S19+'p0312_3',['p0432_2'])
add(d,S19+'p0313_2',['p0432_3'])
save('monopolies',d)
# officials
d=load('officials')
add(d,S19+'p0314_1',['p0433_1','p0433_2'],'1913 also prints the table in two parts.')
add(d,S19+'p0320_1',['p0439_1'])
add(d,S19+'p0321_1',['p0441_2'])
add(d,S19+'p0322_2',['p0442_2'])
add(d,S19+'p0323_1',['p0442_3'])
d['families'].append({"label":"Township clerks by number per township","members":[S13+'p0441_3',S19+'p0321_2']})
d['families'].append({"label":"Village and ward heads by number of villages served","members":[S13+'p0442_1',S19+'p0322_1'],"note":"1913 village heads (洞里長) versus 1919 ward heads (區長)."})
save('officials',d)
# public finance
d=load('public-finance')
A=lambda f,n,note=None: add(d,f,n,note)
A(S19+'p0269_1',['p0388_1'])
A(S19+'p0271_1',['p0389_1'])
A(S19+'p0271_2',['p0389_2'])
A(S19+'p0309_2',['p0427_2'])
A(S19+'p0272_1',['p0390_1'])
A(S19+'p0275_2',['p0391_5'],'1913 gives kyol and tax by province.')
A(S19+'p0281_3',['p0396_1','p0397_1'],'1913 prints brewed and distilled/compounded liquor in two tables.')
A(S19+'p0286_1',['p0398_2','p0399_1'])
A(S19+'p0293_1',['p0406_3'])
A(S19+'p0295_2',['p0413_1'])
A(S19+'p0295_1',['p0412_2'])
A(S19+'p0297_2',['p0416_2'],'1913 is one table by province.')
A(S19+'p0299_1',['p0417_1'])
A(S19+'p0300_1',['p0418_1'])
A(S19+'p0300_2',['p0418_2'])
A(S19+'p0301_1',['p0419_1'])
A(S19+'p0303_1',['p0422_2'])
A(S19+'p0303_2',['p0423_1'])
A(S19+'p0304_1',['p0420_4'])
A(S19+'p0305_1',['p0421_1'])
A(S19+'p0306_1',['p0421_3'])
A(S19+'p0306_2',['p0425_2'])
A(S19+'p0310_1',['p0428_1'])
new=[
("Special account of the Government-General, year-to-year comparison",[S13+'p0388_2',S19+'p0269_2']),
("Forestry special account",[S13+'p0390_2',S19+'p0272_2']),
("Forestry special account, profit accounts",[S13+'p0391_1',S19+'p0273_1']),
("Hospital and relief institute special account",[S13+'p0391_2',S19+'p0273_2']),
("Hospital and relief institute funds special account",[S13+'p0391_3',S19+'p0274_1']),
("Government-General continuing expenditures",[S13+'p0391_4',S19+'p0274_2']),
("Urban taxed land by province",[S13+'p0392_1',S19+'p0276_1']),
("Land with total crop failure",[S13+'p0393_1',S19+'p0278_3']),
("Landowners by land tax paid",[S13+'p0394_2',S19+'p0279_1',S19+'p0279_2',S39+'p0251_2'],"1919 splits the table into land-tax and urban-land-tax areas."),
("Salt tax",[S13+'p0400_1',S19+'p0287_3']),
("Vessel tax",[S13+'p0400_2',S19+'p0287_4']),
("Ginseng tax",[S13+'p0400_3',S19+'p0288_1']),
("Fishery tax",[S13+'p0401_1',S19+'p0288_2']),
("Post-station land income receipts",[S13+'p0412_1',S19+'p0294_3']),
("Distraint for unpaid national taxes",[S13+'p0414_1',S19+'p0296_1']),
("Tax collection expenses",[S13+'p0415_2',S19+'p0297_1']),
("Local fund revenue by item",[S13+'p0417_2',S19+'p0299_2']),
("Distraint for unpaid local fund levies",[S13+'p0419_2',S19+'p0302_1']),
("Imperial bounty distribution",[S13+'p0420_1',S19+'p0302_2']),
("Township levy rates",[S13+'p0421_2',S19+'p0305_2']),
("Water association budgets",[S13+'p0425_3',S19+'p0307_1']),
("Public common school revenue budgets",[S13+'p0425_4',S19+'p0307_2']),
("Public common school expenditure budgets",[S13+'p0426_1',S19+'p0308_1']),
("Confucian school property revenue and expenditure",[S13+'p0427_1',S19+'p0309_1']),
("Water association debt",[S13+'p0428_2',S19+'p0310_2']),
("Settlers' associations revenue and expenditure",[S08+'p0129_1',S13+'p0425_1']),
]
for x in new:
    e={"label":x[0],"members":x[1]}
    if len(x)>2: e['note']=x[2]
    d['families'].append(e)
save('public-finance',d)
allm=[m for f in d['families'] for m in f['members']]
assert len(allm)==len(set(allm))
