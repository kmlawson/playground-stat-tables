import json
d=json.load(open('batches/b15.json'))
M={552:(['education','finance'],['education-finance','primary-education'],'school budgets'),
553:(['education','finance'],['education-finance','primary-education'],'school budgets'),
554:(['education','finance'],['traditional-schools','education-finance'],'hyanggyo property'),
555:(['finance'],['public-debt'],'debt list'),556:(['finance'],['public-debt'],'debt comparison'),
557:(['finance','colonial-rule'],['public-debt'],'settler association debts'),
558:(['finance','education'],['public-debt','education-finance'],'school association debts'),
559:(['finance','agriculture'],['public-debt','irrigation'],'water association debts'),
560:(['finance'],['currency'],'currency circulation'),561:(['finance'],['currency','banking'],'note issue reserves'),
562:(['finance'],['currency','banking'],'note issue monthly'),563:(['finance'],['currency','banking'],'note denominations'),
564:(['finance'],['currency','banking'],'note reserves'),
565:(['agriculture','finance'],['ginseng','state-monopolies'],'ginseng cultivation'),
566:(['agriculture','finance'],['ginseng','state-monopolies'],'ginseng harvest'),
567:(['agriculture','finance'],['ginseng','state-monopolies'],'ginseng harvest grades'),
568:(['manufacturing','finance'],['ginseng','state-monopolies'],'red ginseng production'),
569:(['finance','trade'],['ginseng','state-monopolies'],'red ginseng sales'),
570:(['trade','finance'],['ginseng','exports','imports'],'ginseng trade'),
571:(['government'],['government-offices'],'staff salaries'),572:(['government'],['government-offices'],'staff by office'),
573:(['government'],['government-offices','local-government'],'provincial staff'),
574:(['government'],['government-offices','local-government'],'non-state staff'),
575:(['government'],['government-offices'],'officials on leave'),
576:(['government'],['local-government'],'township staff'),577:(['government'],['local-government'],'township clerks'),
578:(['government'],['local-government'],'village heads'),
579:(['government'],['imperial-household','government-offices'],'Yi household office'),
580:(['government','finance'],['insurance-and-pensions','honours-and-ranks'],'pensions')}
r=[]
for x in d:
  t,g,w=M[int(x['table_no'])]
  r.append(dict(key=x['key'],topics=t,tags=g,flags=[],why=w))
json.dump(r,open('results/b15.json','w'),ensure_ascii=False,indent=1)
print(len(r),len(d))
