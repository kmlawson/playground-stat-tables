import json
b=json.load(open('batches/b10.json'))
J=['crime-and-justice']
m={
352:(J,['civil-litigation','courts'],'payment order cases'),
353:(J,['civil-litigation','courts'],'provisional seizure cases'),
354:(J,['civil-litigation','courts'],'compulsory execution cases'),
355:(J+['finance'],['civil-litigation'],'executions: claims, costs'),
356:(J+['finance'],['civil-litigation'],'executions by claim amount'),
357:(J+['finance'],['civil-litigation'],'claims in distribution'),
358:(J,['civil-litigation','courts'],'real estate auction cases'),
359:(J+['finance'],['civil-litigation','courts'],'bankruptcy cases'),
360:(J,['civil-litigation','courts'],'interdiction cases'),
361:(J,['civil-litigation','courts'],'non-contentious cases'),
362:(J,['civil-litigation','courts'],'civil assistance cases'),
363:(J,['courts'],'notarial cases, fees'),
364:(J,['courts'],'certified-date cases'),
365:(J+['agriculture'],['real-estate','courts'],'real estate registration'),
366:(J+['agriculture'],['real-estate','courts'],'registration by type'),
367:(J+['economy'],['courts'],'non-profit corporation registration'),
368:(J+['economy'],['companies','courts'],'company registration'),
369:(J+['economy'],['courts'],'trade-name registration'),
370:(J,['courts','offences-and-convictions'],'prosecutor cases received'),
371:(J,['courts','offences-and-convictions'],'prosecutor dispositions'),
372:(J,['courts','offences-and-convictions'],'preliminary examinations'),
373:(J,['offences-and-convictions','courts'],'first-instance criminal cases'),
374:(J,['offences-and-convictions','nationality-and-ethnicity'],'offences by nationality'),
375:(J,['offences-and-convictions','nationality-and-ethnicity'],'judgments by offence, race'),
376:(J,['offences-and-convictions','courts'],'second-instance criminal'),
377:(J,['offences-and-convictions','courts'],'second-instance results'),
378:(J,['offences-and-convictions','courts'],'third-instance criminal'),
379:(J,['offences-and-convictions','courts'],'third-instance results'),
380:(J,['offences-and-convictions','nationality-and-ethnicity'],'new criminal cases by nationality'),
381:(J,['courts','offences-and-convictions'],'criminal appeals'),
382:(J,['civil-litigation','courts'],'civil claims attached to prosecutions'),
383:(J,['offences-and-convictions','courts'],'defendant detention periods'),
384:(J,['offences-and-convictions','courts'],'suspended sentences'),
385:(J+['finance'],['offences-and-convictions','courts'],'fines execution'),
386:(J,['offences-and-convictions','courts'],'corporal sentence execution'),
387:(J,['courts'],'judicial assistance cases'),
388:(J,['prisons'],'prison staff'),
389:(J,['prisons'],'prisoners held'),
390:(J,['prisons','offences-and-convictions'],'convicts by offence'),
391:(J,['prisons','offences-and-convictions'],'convicts by sentence'),
}
out=[]
for r in b:
    t,g,w=m[int(r['table_no'])]
    out.append({'key':r['key'],'topics':t,'tags':g,'flags':[],'why':w})
json.dump(out,open('results/b10.json','w'),ensure_ascii=False,indent=1)
print(len(out))
