import json
d=json.load(open('batches/b11.json'))
F=["finance"]
def m(n):
    return {398:("taxation","land-tax"),399:("taxation","land-tax")}.get(n)
out=[]
for r in d:
    n=int(r['table_no']) if r.get('table_no') else None
    t=r['title']; tp=["finance"]; tg=["taxation"]; w=r['en']['t']
    if t.startswith('納稅義務者'): tg=["land-tax","taxation"]
    elif '所得稅' in t: tg=["taxation"]
    elif '酒' in t: tg=["taxation","alcohol"]
    elif '煙草' in t: tg=["taxation","tobacco"]
    elif '砂糖' in t: tg=["taxation","sugar"]
    elif t in('鑛區稅','特許鑛稅'): tg=["taxation","mining-rights-and-concessions"]; tp=["finance","mining"]
    elif t=='鑛產稅': tg=["taxation","mineral-production"]; tp=["finance","mining"]
    elif '鹽' in t: tg=["salt-tax"]
    elif '船稅' in t: tg=["taxation","shipping"]
    elif '人參' in t: tg=["taxation","ginseng"]
    elif '漁業' in t: tg=["taxation","fishing-rights-and-licences"]; tp=["finance","fisheries"]
    elif '戰時利得' in t: tg=["taxation"]
    elif '驛屯' in t: tg=["public-property","public-budgets"]
    elif t=='國稅收納額' or '歲入豫算' in t or t=='收入印紙收納額' or '稅外' in t: tg=["public-budgets","taxation"]
    elif '滯納' in t: tg=["taxation"]
    elif '犯則' in t: tg=["offences-and-convictions","taxation"]; tp=["finance","crime-and-justice"]
    elif '徵稅費' in t: tg=["taxation","public-budgets"]
    elif '直接稅負擔' in t: tg=["taxation","local-government"]
    elif '地方費' in t: tg=["public-budgets","local-government"]; tp=["finance","government"]
    out.append({"key":r['key'],"topics":tp,"tags":tg,"flags":[],"why":w[:60]})
json.dump(out,open('results/b11.json','w'),ensure_ascii=False,indent=1)
v=json.load(open('../../vocabulary.json'))
s=json.dumps(v)
ids={x for o in out for x in o['tags']}
print(len(out),[i for i in ids if '"%s"'%i not in s])
