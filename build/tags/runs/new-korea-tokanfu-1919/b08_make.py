import json
d=json.load(open('batches/b08.json'))
J=['crime-and-justice']
m={
278:(['trade','crime-and-justice'],['companies'],'company registrations'),
279:(['trade','crime-and-justice'],['companies'],'trade-name/manager registrations'),
280:(J,['civil-litigation','courts'],'civil conciliation'),
281:(J,['courts','offences-and-convictions'],'prosecutor cases'),
282:(J,['courts','offences-and-convictions'],'prosecutor investigations'),
283:(J,['courts','offences-and-convictions'],'non-prosecution'),
284:(J,['courts'],'preliminary examinations'),
285:(J,['courts','offences-and-convictions'],'first instance criminal'),
286:(J,['offences-and-convictions','courts'],'defendants by offence'),
287:(J,['courts','offences-and-convictions'],'second instance'),
288:(J,['courts','offences-and-convictions'],'second instance results'),
289:(J,['courts','offences-and-convictions'],'third instance'),
290:(J,['courts','offences-and-convictions'],'third instance results'),
291:(J,['courts'],'criminal appeals'),
292:(J,['courts'],'private suits in prosecutions'),
293:(J,['courts','prisons'],'defendant detention'),
294:(J,['courts','offences-and-convictions'],'suspended sentences'),
295:(J,['courts','offences-and-convictions'],'fines execution'),
296:(J,['prisons','offences-and-convictions'],'penalty execution'),
297:(J,['courts'],'judicial assistance'),
298:(J,['prisons'],'prisoners held'),
299:(J,['prisons','offences-and-convictions'],'convicts by offence'),
300:(J,['prisons','offences-and-convictions'],'sentence and term'),
301:(J,['prisons'],'admissions/releases'),
302:(J,['prisons','offences-and-convictions'],'new convicts by sentence'),
303:(J,['prisons','offences-and-convictions'],'recidivism'),
304:(J,['prisons','age-and-sex'],'convicts by age'),
305:(J,['prisons','offences-and-convictions'],'motive'),
306:(J,['prisons'],'birth/upbringing'),
307:(J,['prisons'],'convict education'),
308:(J,['prisons'],'birthplace by province'),
309:(J,['prisons','offences-and-convictions'],'offence by month'),
310:(J,['prison-labour','prisons'],'prison labour'),
311:(['crime-and-justice','health'],['prisons','diseases'],'prisoner illness'),
312:(['crime-and-justice','welfare'],['prisoner-aftercare'],'released prisoner aid'),
313:(['education'],['schools-and-pupils','primary-education'],'schools for Japanese'),
314:(['education'],['schools-and-pupils','primary-education'],'school-age children'),
315:(['education'],['primary-education','teachers','schools-and-pupils'],'elementary classes teachers pupils'),
316:(['education'],['primary-education','schools-and-pupils'],'admissions graduates'),
317:(['education'],['primary-education','schools-and-pupils'],'dropouts deaths'),
}
out=[]
for r in d:
    t,g,w=m[int(r['table_no'])]
    if not g[0]=='companies' and len(t)==1 and t==J: pass
    out.append({'key':r['key'],'topics':t if isinstance(t,list) else J,'tags':g,'flags':[],'why':w})
json.dump(out,open('results/b08.json','w'),ensure_ascii=False,indent=1)
v=json.load(open('../../vocabulary.json'))
ids={x['id'] if isinstance(x,dict) else x for x in (v['tags'] if isinstance(v['tags'],list) else v['tags'].keys())}
tp=v['topics']; tp={x['id'] if isinstance(x,dict) else x for x in (tp if isinstance(tp,list) else tp.keys())}
print(len(out),[o for o in out if set(o['tags'])-ids or set(o['topics'])-tp])
