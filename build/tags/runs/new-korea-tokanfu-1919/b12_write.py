import json
d=json.load(open('batches/b12.json'))
G=['government','finance']; F=['finance','government']
pb='public-budgets'; lg='local-government'
A={
437:(F,[pb,lg,'taxation'],'local expense revenue by levy'),
438:(F,[pb,lg],'local expense spending'),
439:(F,['taxation',lg,'land-tax'],'levies by province'),
440:(F,['taxation',lg],'levy assessed vs collected'),
441:(F,['taxation',lg],'arrears disposal'),
442:(F,[pb],'imperial bounty allotment'),
443:(F,[pb,lg],'city revenue'),444:(F,[pb,lg],'city expenditure'),
445:(F,[pb,lg],'township revenue'),446:(F,[pb,lg],'township expenditure'),
447:(F,['taxation',lg],'township levy rates'),448:(F,['taxation',lg],'township burden'),
449:(['finance','education'],['education-finance',pb,lg],'school association budgets'),
450:(['finance','agriculture'],['irrigation',pb],'irrigation association budgets'),
451:(['finance','education'],['education-finance','primary-education',pb],'common school revenue'),
452:(['finance','education'],['education-finance','primary-education',pb],'common school expenditure'),
453:(['education','finance'],['traditional-schools',pb],'hyanggyo property budgets'),
454:(['finance'],['public-debt'],'national debt'),
455:(F,['public-debt',lg],'city debt'),
456:(['finance','education'],['public-debt','education-finance'],'school association debt'),
457:(['finance','agriculture'],['public-debt','irrigation'],'irrigation association debt'),
458:(['agriculture','economy'],['ginseng','state-monopolies'],'ginseng cultivation'),
459:(['agriculture','economy'],['ginseng','state-monopolies'],'ginseng harvest'),
460:(['agriculture','economy'],['ginseng','state-monopolies'],'ginseng receipts'),
461:(['manufacturing','economy'],['ginseng','state-monopolies'],'red ginseng production'),
462:(['trade','economy'],['ginseng','state-monopolies'],'red ginseng sales'),
463:(['manufacturing','trade'],['ginseng','state-monopolies'],'ginseng products'),
464:(['trade'],['ginseng','exports','imports'],'ginseng trade'),
465:(['government','labour'],['government-offices','wages'],'official salaries'),
466:(['government','labour'],['government-offices','wages','nationality-and-ethnicity'],'salaries by office and nationality'),
467:(['government','labour'],['government-offices','wages',lg],'locally paid staff'),
468:(['government'],[lg,'government-offices'],'township officials'),
469:(['government'],[lg,'government-offices'],'township clerks'),
470:(['government'],[lg,'government-offices'],'ward heads'),
471:(['government'],['imperial-household','government-offices','wages'],'Yi household staff'),
472:(['government','finance'],['insurance-and-pensions','government-offices'],'pensions'),
}
out=[]
for r in d:
    t,g,w=A[int(r['table_no'])]
    out.append({'key':r['key'],'topics':t,'tags':g,'flags':[],'why':w})
json.dump(out,open('results/b12.json','w'),ensure_ascii=False,indent=1)
v=json.load(open('../../vocabulary.json'))
s=json.dumps(v)
bad=[x for o in out for x in o['topics']+o['tags'] if '"%s"'%x not in s]
print(len(out),bad)
