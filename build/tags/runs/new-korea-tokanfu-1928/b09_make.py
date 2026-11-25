import json
d=json.load(open('batches/b09.json'))
C='crime-and-justice'
m={
278:([C],['courts','offences-and-convictions'],'detention periods by court'),
280:([C],['offences-and-convictions'],'suspended sentences by offence'),
281:([C],['offences-and-convictions','courts'],'suspended sentences by court'),
284:([C],['courts'],'judicial assistance cases'),
285:([C],['juvenile-justice','offences-and-convictions'],'under-18 investigations'),
286:([C],['juvenile-justice','courts'],'under-18 by court'),
287:([C],['juvenile-justice','offences-and-convictions'],'under-18 first instance'),
289:([C],['juvenile-justice','courts'],'under-18 by court'),
290:([C],['prisons'],'prison staff'),
291:([C],['prisons'],'inmates at year-end'),
292:([C],['prisons'],'convicts by prison'),
293:([C],['prisons','offences-and-convictions'],'convicts by sentence'),
294:([C],['prisons'],'inmate days'),
295:([C],['prisons'],'admissions/discharges'),
297:([C],['prisons'],'defendant admissions'),
299:([C],['prisons'],'workhouse detainees'),
300:([C],['prisons'],'accompanying children'),
304:([C],['prisons','offences-and-convictions'],'by repeat offences'),
305:([C,'population'],['prisons','age-and-sex'],'convicts by age'),
308:([C],['prisons','offences-and-convictions'],'motive'),
312:([C,'education'],['prisons'],'convicts by education'),
313:([C],['prisons','offences-and-convictions'],'place of offence'),
314:([C],['prisons'],'birthplace'),
316:([C],['prisons','offences-and-convictions'],'month of offence'),
317:([C],['prison-labour'],'prison labour'),
321:([C],['prison-labour'],'days not employed'),
322:([C],['prison-labour'],'labour revenue'),
323:([C],['prison-labour'],'labour accounts'),
324:([C],['prison-labour','prisons'],'labour bonuses'),
327:([C,'health'],['prisons','diseases'],'sick prisoners'),
329:([C],['prisons','offences-and-convictions'],'discipline'),
330:([C],['prisoner-aftercare'],'aid on release'),
}
out=[]
for r in d:
    k=r['key'];n=int(k.split(':p')[1][:4]);t=r['title']
    if t=='罹病者病類別': x=([C,'health'],['diseases','prisons'],'sick by illness')
    elif t=='罹病者刑務所別': x=([C,'health'],['prisons','diseases'],'sick by prison')
    elif t=='病者經過期間別': x=([C,'health'],['prisons','diseases'],'illness timing')
    elif t=='死亡人員月別': x=([C,'health'],['prisons'],'deaths by month')
    elif t=='釋放時作業賞與金給與人員': x=([C],['prison-labour','prisons'],'release bonuses')
    elif t=='賞遇人員': x=([C],['prisons'],'rewards')
    elif t=='徵收金成績種類別': x=([C],['offences-and-convictions'],'fines collected')
    elif t=='徵收金成績裁判所別': x=([C],['courts','offences-and-convictions'],'fines by court')
    elif t=='作業收支種類別' or t=='作業收支刑務所別': x=([C],['prison-labour'],'labour accounts')
    elif t=='新受刑者敎育別': x=([C,'education'],['prisons'],'convicts by education')
    elif t=='新受刑者出生及生育別': x=([C],['prisons'],'birth legitimacy')
    elif t=='新受刑者出生地別(朝鮮人)': x=([C],['prisons'],'birthplace')
    elif n==300 and t=='新受刑者刑名刑期別': x=([C],['prisons','offences-and-convictions'],'new convicts by sentence')
    elif n==300: x=([C],['prisons'],'accompanying children')
    elif n==308 and t.startswith('新受刑者犯由'): x=m[308]
    else: x=m[n]
    out.append(dict(key=k,topics=x[0],tags=x[1],flags=[],why=x[2]))
json.dump(out,open('results/b09.json','w'),ensure_ascii=False,indent=1)
print(len(out),sum(1 for o in out if o['tags']))
