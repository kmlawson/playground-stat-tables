import json
def go(f,add):
    p='families/china-smc--%s.json'%f
    d=json.load(open(p)); n=0
    for lab,ms in add.items():
        fam=[x for x in d['families'] if x['label']==lab]; assert len(fam)==1,lab
        fam=fam[0]
        new=['china-smc-1881/'+m for m in ms]
        assert not set(new)&set(fam['members'])
        fam['members']=new+fam['members']; n+=len(new)
    json.dump(d,open(p,'w'),ensure_ascii=False,indent=1)
    json.load(open(p)); print(f,n)
go('volunteer-corps-and-fire-brigade',{
 'Artillery equipment: guns and harness':['p0018_1'],
 'Ammunition stock and issues':['p0020_1'],
 'Fire Brigade statement of receipts and expenditure':['p0146_1'],
 'Fire Brigade estimate':['p0148_1'],
 'Members of the Fire Commission (estimate signatories)':['p0148_2']})
go('treasurer-s-report-and-revenue',{
 'Foreign general municipal rate summary':['p0026_1','p0027_1','p0028_1','p0029_1'],
 'Chinese general municipal rate summary':['p0026_2','p0027_2','p0028_2','p0029_2'],
 'New foreign houses assessed':['p0030_1'],
 'Foreign houses: assessments reduced':['p0031_1'],
 'Lots of land assessed during the year':['p0032_1'],
 'Local Post Office correspondence':['p0036_1'],
 'Accounts summary: receipts, disbursements, balance':['p0022_1'],
 'Expenditure in excess of appropriations':['p0023_1']})
