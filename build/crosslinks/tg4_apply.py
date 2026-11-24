import json
P='korea-tokanfu-'
ORD={'1908':0,'1913':1,'1919':2,'1939':3}
def m(s):  # '1913/p0363_2' -> slug/id
    return P+s
def ed(x): return ORD[x.split('/')[0][len(P):]]
def run(name, adds, news):
    fn=f'families/korea-tokei--{name}.json'
    d=json.load(open(fn,encoding='utf-8'))
    allm={x for f in d['families'] for x in f['members']}
    byl={f['label']:f for f in d['families']}
    cnt=0
    for lab,new in adds:
        f=byl[lab]
        for n in new:
            n=m(n); assert n not in allm,n
            allm.add(n)
            f['members'].append(n); cnt+=1
        f['members']=sorted(f['members'],key=ed)  # stable
    for lab,mem,note in news:
        mem=[m(x) for x in mem]
        for x in mem: assert x not in allm,x
        allm.update(mem); cnt+=sum(1 for x in mem if x.startswith(P+'1913'))
        d['families'].append({'label':lab,'members':sorted(mem,key=ed),'note':note})
    json.dump(d,open(fn,'w',encoding='utf-8'),ensure_ascii=False,indent=1)
    json.load(open(fn,encoding='utf-8'))
    print(name,len(d['families']),'families; 1913 added:',cnt)

run('social-affairs',[
 ('Buddhist temples and Korean temples/monks',['1913/p0381_1']),
 ('Relief Institute staff',['1913/p0381_3']),
 ('Relief Institute nursery pupils',['1913/p0381_4']),
 ('Relief of sick and dead travellers',['1913/p0382_2']),
 ('Red Cross members',['1913/p0386_2']),
 ("Patriotic Women's Association members",['1913/p0387_1']),
 ('Imperial relief grants',['1913/p0387_2']),
],[
 ('Relief Institute blind and deaf-mute department',['1913/p0382_1','1919/p0264_1'],''),
 ('Sick and dead travellers by disease',['1913/p0384_1','1919/p0266_1'],''),
])

run('education',[
 ('Japanese school-age children',['1913/p0363_2']),
 ('Japanese elementary schools: status',['1913/p0364_2']),
 ('Japanese elementary schools: pupil movements',['1913/p0365_1','1913/p0366_1']),
 ('Japanese elementary schools: attendance',['1913/p0366_2']),
 ('Japanese elementary schools: assets',['1913/p0369_1']),
 ("Japanese elementary schools: teachers' qualifications and pay",['1913/p0369_2']),
 ('Korean elementary schools: status',['1913/p0372_2']),
 ('Korean elementary schools: pupil movements',['1913/p0372_3','1913/p0372_4']),
 ('Korean elementary schools: attendance',['1913/p0373_1']),
 ('Korean elementary schools: assets',['1913/p0374_1']),
 ("Korean elementary schools: teachers' qualifications and pay",['1913/p0374_2']),
 ('Middle schools: status',['1913/p0370_1']),
 ('Middle schools: assets',['1913/p0370_2']),
 ("Girls' high schools: status",['1913/p0370_3']),
 ("Girls' high schools: assets",['1913/p0371_1']),
 ('Vocational schools: status',['1913/p0376_1']),
 ('Vocational schools: assets',['1913/p0376_2']),
 ('Private miscellaneous schools by province',['1913/p0378_3']),
 ('Village schools (sodang)',['1913/p0378_4']),
 ('Libraries',['1913/p0379_4']),
],[
 ('Educational institutions for Japanese',['1913/p0363_1','1919/p0242_1'],''),
 ('Japanese elementary schools: expenditure',['1913/p0368_2','1919/p0246_1'],''),
 ('Vocational training schools for Japanese: status',['1913/p0371_2','1919/p0249_1','1919/p0249_2'],'1919 splits commercial and simplified vocational training schools into two tables.'),
 ('Vocational training schools for Japanese: assets',['1913/p0371_3','1919/p0249_3'],''),
 ('Private miscellaneous schools for Japanese',['1913/p0371_4','1919/p0249_5'],''),
 ('Educational institutions for Koreans',['1913/p0372_1','1919/p0250_1'],''),
 ('Simple vocational schools',['1913/p0377_1','1919/p0257_1'],''),
 ('Government students in Japan',['1913/p0379_2','1919/p0259_3'],''),
 ('Textbooks distributed',['1913/p0379_3','1919/p0260_2'],''),
])

run('banking-and-commerce',[
 ('Bank deposits by type',['1913/p0133_1']),
 ('Bank loans by type',['1913/p0133_3']),
 ('Ordinary banks, general business',['1913/p0132_2']),
 ("Moneylenders' interest rates",['1913/p0142_3']),
 ('Companies',['1913/p0098_1']),
 ('Markets',['1913/p0100_2']),
 ('Financial institutions',['1913/p0132_1']),
 ('Bank deposits by month',['1913/p0133_2']),
 ('Bank loans by month',['1913/p0134_1']),
 ('Bank deposits and loans by region',['1913/p0134_2']),
 ('Clearing-house exchanges',['1913/p0141_2']),
 ('Financial associations business',['1913/p0140_5']),
 ('Bank of Chosen average interest',['1913/p0141_3']),
 ('Ordinary banks average interest',['1913/p0142_1','1913/p0142_2']),
],[
 ('Bank of Chosen: general business',['1913/p0134_3','1919/p0125_1'],''),
 ('Bank of Chosen: deposits',['1913/p0135_1','1919/p0125_2'],''),
 ('Bank of Chosen: borrowings',['1913/p0135_2','1919/p0125_3'],''),
 ('Bank of Chosen: loans',['1913/p0135_3','1919/p0125_4'],''),
 ('Bank of Chosen: funds placed with other banks',['1913/p0135_4','1919/p0126_2'],''),
 ('Bank of Chosen: exchange receipts and payments',['1913/p0136_1','1919/p0126_5'],''),
 ('Agricultural and industrial banks: general business',['1908/p0080_1','1913/p0136_2','1919/p0127_5'],''),
 ('Ordinary banks: general business by year',['1913/p0139_1','1919/p0128_1'],''),
 ('Ordinary banks: deposits',['1913/p0139_2','1919/p0128_2'],''),
 ('Ordinary banks: borrowings',['1913/p0140_1','1919/p0129_1'],''),
 ('Ordinary banks: loans',['1913/p0140_2','1919/p0129_2'],''),
 ('Ordinary banks: funds placed with other banks',['1913/p0140_3','1919/p0129_4'],''),
 ('Ordinary banks: exchange receipts and payments',['1913/p0140_4','1919/p0129_5'],''),
 ('Factories',['1913/p0099_2','1919/p0118_1'],''),
 ('Weights and measures: sellers and sales',['1913/p0101_2','1913/p0101_3','1919/p0117_1','1919/p0117_2','1939/p0117_1'],'Earlier editions split sellers and sales into two tables; 1939 combines them.'),
 ('Government-General Printing Office',['1913/p0102_2','1919/p0119_3'],''),
])
