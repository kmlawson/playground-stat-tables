import json
O={'p0024_1':(['sport','military'],['sports-records'],[]),
'p0128_1':(['finance','culture'],['recreation-and-amusements'],[]),
'p0192_1':(['finance','culture'],['arts-and-music'],[]),
'p0193_1':(['finance','culture'],['arts-and-music'],[]),
'p0194_1':(['government','disasters'],['firefighting'],['text-tables']),
'p0194_2':(['government','disasters'],['firefighting'],['text-tables']),
'p0194_3':(['government','disasters'],['firefighting'],['text-tables']),
'p0200_2':(['government','disasters'],['firefighting'],['text-tables'])}
for b in range(1,8):
    f=f'results/b{b:02d}.json';d=json.load(open(f))
    for x in d:
        k=x['key'].split(':')[1]
        if k in O: x['topics'],x['tags'],x['flags']=O[k]
    json.dump(d,open(f,'w'),ensure_ascii=False,indent=1)
