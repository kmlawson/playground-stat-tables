import json
A='korea-tokanfu-1919/';B='korea-tokanfu-1939/'
def run(name,pairs):
    fam=[]
    for lab,a,b in pairs:
        fam.append({"label":lab,"members":[A+x for x in a.split()]+[B+x for x in b.split()],"note":""})
    json.dump({"listing":name,"families":fam},open(f'families/{name}.json','w'),ensure_ascii=False,indent=1)
    n=sum(len(f['members']) for f in fam);print(name,len(fam),n)
run('korea-tokanfu--courts-and-registration',[
("Civil cases, first instance","p0216_2","p0207_1"),("Civil cases, second instance","p0217_1","p0207_2"),("Civil cases, third instance","p0217_2","p0207_3"),
("Civil suit amounts and values","p0217_3","p0208_2"),("Civil appeals (kokoku)","p0218_1","p0208_4"),("Settlement cases","p0218_2","p0209_1"),
("Payment-order cases","p0219_1","p0209_2"),("Provisional seizure and disposition","p0219_2","p0209_3"),("Compulsory execution cases","p0219_3","p0209_4"),
("Real-estate auction cases","p0219_4","p0210_2"),("Bankruptcy cases","p0220_1","p0210_3"),("Interdiction and disappearance declarations","p0220_2","p0210_4"),
("Non-contentious cases","p0220_3","p0210_5"),("Civil judicial assistance","p0220_4","p0210_6"),("Bailiff business cases","p0221_1","p0210_7"),
("Notarial cases","p0222_1","p0211_2"),("Fixed-date (certified date) cases","p0222_2","p0211_3"),("Real estate and ship registration","p0222_3","p0211_4"),
("Non-profit corporation registration","p0223_1","p0212_2"),("Commercial company registration","p0224_1","p0212_3"),("Trade name, minor, wife, agent registration","p0224_2","p0213_1"),
("Civil dispute conciliation","p0225_1","p0213_3"),("Prosecutor cases received","p0225_2","p0215_1"),("Prosecutor investigation cases","p0226_1","p0215_2"),
("Preliminary examination cases","p0226_3","p0217_1"),("Criminal cases, first instance","p0226_4","p0217_2"),("Criminal first instance, persons by judgment","p0227_1","p0219_2"),
("Criminal cases, second instance","p0229_1","p0218_1"),("Criminal second instance, judgments","p0229_2","p0220_1"),("Criminal cases, third instance","p0230_1","p0219_1"),
("Criminal third instance, judgments","p0230_2","p0221_1"),("Criminal appeals (kokoku)","p0230_3","p0222_1"),("Private prosecution cases","p0230_4","p0222_2"),
("Criminal defendants by detention period","p0231_1","p0223_1"),("Suspended sentences and revocations","p0231_2","p0223_2"),("Judicial assistance, criminal","p0234_1","p0224_1")])
run('korea-tokanfu--prisons',[
("Prison inmates","p0234_2","p0227_2"),("Convicts by sentence and term","p0235_1","p0229_1"),("Convict admissions and discharges","p0236_1","p0229_2"),
("New convicts by sentence and term","p0237_1","p0230_3"),("New convicts by number of offences","p0237_2","p0232_1"),("New convicts by age at entry","p0237_3","p0232_2"),
("New convicts by cause of crime","p0237_4","p0233_1"),("New convicts by birth and upbringing","p0238_1","p0234_1"),("New convicts by education","p0238_2","p0234_2"),
("Prison labour","p0239_1","p0235_2"),("Prisoners' illness","p0240_1","p0238_1"),("Discharged-prisoner aid","p0241_1","p0244_1")])
run('korea-tokanfu--commerce-and-finance',[
("Companies","p0110_1","p0115_1"),("Markets","p0115_1","p0115_2"),("Insurance","p0112_1","p0116_2 p0116_3"),("Currency in circulation estimate","p0120_2","p0117_2"),
("Bank of Chosen note issue","p0121_1","p0117_3"),("Financial institutions","p0120_1","p0118_1"),("Bank business overview","p0122_1","p0118_2"),
("Bank deposits by type","p0122_2","p0118_3"),("Bank deposits by month","p0122_3","p0119_1"),("Bank loans by type","p0123_1","p0119_3"),
("Bank loans by month","p0123_2","p0119_4"),("Bank deposits and loans by region","p0124_1","p0119_2 p0119_5"),("Bank exchange transactions","p0124_2","p0120_1"),
("Clearing-house exchanges","p0130_3","p0120_2"),("Financial associations business","p0130_1","p0121_2"),("Bank of Chosen average interest","p0131_1","p0123_1"),
("Chosen Industrial Bank average interest","p0132_1","p0123_2"),("Ordinary banks average interest","p0132_2","p0123_4"),("Financial association interest","p0132_4","p0123_6"),
("Moneylender interest","p0132_3","p0123_7")])
