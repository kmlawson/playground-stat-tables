import json
d=json.load(open('batches/b11.json'))
v=json.load(open('../../vocabulary.json'))
ids={t['id'] for t in v['tags']}; tp={t['id'] for t in v['topics']}
CJ='crime-and-justice'
m={
392:([CJ],['prisons'],'inmates by prison, nationality, sex'),
393:([CJ],['prisons'],'convict admissions/releases'),
394:([CJ],['offences-and-convictions','prisons'],'new convicts by offence, sentence'),
395:([CJ],['offences-and-convictions','prisons'],'offence by prison'),
396:([CJ],['offences-and-convictions','prisons'],'sentence term by prison'),
397:([CJ],['offences-and-convictions','prisons'],'prior convictions by offence'),
398:([CJ],['offences-and-convictions','prisons'],'prior convictions by prison'),
399:([CJ,'population'],['offences-and-convictions','age-and-sex'],'age at admission by offence'),
400:([CJ,'population'],['prisons','age-and-sex'],'age at admission by prison'),
401:([CJ],['prisons'],'defendants in custody movements'),
402:([CJ],['prisons'],'labour house detainees'),
403:([CJ],['prisons'],'children accompanying inmates'),
404:([CJ,'labour'],['prison-labour'],'prison work'),
405:([CJ,'labour'],['prison-labour'],'prison work income/expenditure'),
406:([CJ,'labour'],['prison-labour'],'work bonuses on release'),
407:([CJ,'labour'],['prison-labour'],'work bonuses by prison'),
408:([CJ,'health'],['prisons','diseases'],'sick prisoners by disease'),
409:([CJ,'health'],['prisons','diseases'],'sick prisoners by prison'),
410:([CJ,'health'],['prisons','diseases'],'illness to death interval'),
411:([CJ,'health'],['prisons','diseases'],'illness to death by prison'),
412:([CJ,'health'],['prisons','births-and-deaths'],'prisoner deaths by month'),
413:([CJ],['prisons'],'prison discipline'),
414:([CJ],['prisons'],'punished prisoners by prison'),
415:([CJ],['prisoner-aftercare'],'protection on release'),
416:([CJ],['prisoner-aftercare'],'protection on release by prison'),
417:([CJ],['corporal-punishment'],'flogging'),
418:([CJ],['corporal-punishment'],'flogging by prison'),
419:(['education','colonial-rule'],['schools-and-pupils'],'schools for Japanese'),
420:(['education','population'],['schools-and-pupils'],'school-age children'),
421:(['education'],['primary-education','schools-and-pupils'],'elementary schools'),
422:(['education'],['primary-education','teachers','schools-and-pupils'],'teachers and pupils'),
423:(['education'],['primary-education','schools-and-pupils'],'entrants and graduates'),
424:(['education'],['primary-education','schools-and-pupils'],'dropouts and deaths'),
425:(['education'],['primary-education','schools-and-pupils'],'attendance'),
426:(['education'],['primary-education','schools-and-pupils'],'pupils by year'),
427:(['education','population'],['primary-education','schools-and-pupils'],'pupils by home prefecture'),
428:(['education'],['primary-education','education-finance'],'tuition'),
429:(['education','finance'],['primary-education','education-finance'],'school expenditure'),
430:(['education','finance'],['primary-education','education-finance'],'school assets'),
431:(['education'],['primary-education','teachers'],'teachers by qualification, salary'),
}
out=[]
for r in d:
    a=m[int(r['table_no'])]
    assert set(a[0])<=tp and set(a[1])<=ids,a
    out.append({"key":r['key'],"topics":a[0],"tags":a[1],"flags":[],"why":a[2]})
json.dump(out,open('results/b11.json','w'),ensure_ascii=False,indent=1)
print(len(out))
