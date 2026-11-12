import json
d=json.load(open('batches/b01.json'))
out=[]
for r in d:
    t=r['title']; k=r['key']
    flags=[]; topics=['education']
    if '尋常小學校第六學年' in t: tags=['primary-education','secondary-education','schools-and-pupils']; why='upper elementary girls and secondary applicants'
    elif '設立者別' in t: tags=['secondary-education','schools-and-pupils']; why='school counts by founder'
    elif '學校名稱' in t: tags=['secondary-education','schools-and-pupils']; flags=['text-tables']; why='list of schools, founders, principals'
    elif '教員' in t: tags=['teachers','secondary-education']; why='teachers by qualification'
    elif '卒業' in t: tags=['schools-and-pupils','secondary-education']; why='graduates by destination'
    elif '退學' in t: tags=['schools-and-pupils','secondary-education']; why='mid-course leavers by year'
    elif '入學' in t: tags=['schools-and-pupils','secondary-education']; why='applicants and admissions'
    else: tags=['schools-and-pupils','secondary-education']; why='schools, capacity, classes, pupils'
    out.append(dict(key=k,topics=topics,tags=tags,flags=flags,why=why))
assert [o['key'] for o in out]==[r['key'] for r in d]
json.dump(out,open('results/b01.json','w'),ensure_ascii=False,indent=1)
print(len(out))
