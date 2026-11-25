import json
d=json.load(open('batches/b08.json'))
J=["crime-and-justice"]
CL,C,O=["civil-litigation"],["courts"],["offences-and-convictions"]
m={}
def s(ids,t,g,w,top=J):
    for i in ids: m['korea-tokanfu-1928:'+i]=(top,t,w)
s(['p0232_1','p0233_1','p0234_1','p0234_2','p0235_1','p0235_2','p0235_3','p0235_4','p0236_1'],CL+C,0,'civil enforcement/insolvency cases')
s(['p0236_2','p0236_3','p0277_1'],C,0,'court business')
s(['p0237_1','p0239_1','p0239_2'],CL+C,0,'bailiff executions')
s(['p0239_3'],C,0,'bailiff income')
s(['p0241_1','p0242_1','p0242_2'],C,0,'notarial/certified-date business',J+['government'])
s(['p0243_1'],["land-registration"],0,'real estate/ship registration')
s(['p0249_1'],[],0,'non-profit corporation registration',J+['economy'])
s(['p0250_1','p0253_1'],["companies"],0,'commercial registration',J+['trade'])
s(['p0254_1'],CL,0,'marital property registration')
s(['p0254_2'],["mediation-and-arbitration","civil-litigation"],0,'civil mediation')
s(['p0254_3'],[],0,'deposit cases',J+['finance'])
s(['p0255_1','p0256_1','p0264_1','p0271_1','p0273_1'],C+O,0,'prosecution/court cases')
s(['p0258_1','p0264_2','p0267_1','p0269_1','p0272_1','p0273_2','p0275_1'],O+C,0,'criminal cases/judgments')
s(['p0274_1'],O+["nationality-and-ethnicity"],0,'criminal cases by nationality')
s(['p0277_2'],CL+C,0,'private prosecution')
out=[]
for r in d:
    top,t,w=m[r['key']]
    out.append(dict(key=r['key'],topics=top,tags=t,flags=[],why=w))
json.dump(out,open('results/b08.json','w'),ensure_ascii=False,indent=1)
print(len(out),sum(1 for o in out if o['tags']))
