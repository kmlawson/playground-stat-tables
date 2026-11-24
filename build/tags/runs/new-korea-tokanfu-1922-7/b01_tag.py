import json
d=json.load(open('batches/b01.json'));out=[]
for r in d:
    t=r['title'];n=r['en']['t']
    topics=['education'];tags=[];why=''
    if '資產' in t:
        tags=['public-property'] if '私立' not in t else []
        topics=['education','finance'] if tags else ['education']
        why='school land/buildings and value'
    elif '經費' in t:
        tags=['education-finance'];topics=['education','finance'];why='school income and expenses'
    elif '敎員資格' in t:
        tags=['teachers'];why='teacher qualifications, salaries'
    elif '學齡兒童' in t:
        tags=['primary-education','nationality-and-ethnicity'];why='Japanese school-age children enrolment'
    elif '學校及生徒概數' in t or '概數' in t:
        tags=['schools-and-pupils'];why='summary of schools and pupils by type'
    elif '一覽' in t:
        tags=['schools-and-pupils'];why='schools/pupils by type'
    else:
        tags=['schools-and-pupils']; why='school status, classes, teachers, pupils'
    if '小學校' in t or '普通學校' in t and '高等' not in t:
        tags=[x for x in tags if x!='primary-education']+['primary-education']
    if '高等普通' in t or '中學校' in t or '高等女學校' in t:
        tags.append('secondary-education')
    if '實業' in t: tags.append('vocational-education')
    if '專門學校' in t: tags.append('higher-education')
    if '出席' in t or '入學者' in t or '退學' in t: why='pupil flows/attendance'
    seen=[];[seen.append(x) for x in tags if x not in seen]
    out.append(dict(key=r['key'],topics=topics,tags=seen[:3],flags=[],why=why))
json.dump(out,open('results/b01.json','w'),ensure_ascii=False,indent=1)
print(len(out),sum(1 for o in out if o['tags']))
for o in out[:6]+out[-4:]:print(o['key'],o['tags'])
