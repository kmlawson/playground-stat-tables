import json
H=['health','population'];D=['diseases','births-and-deaths'];F=['finance'];RB=['utilities','transportation']
def r(tp,tg,why,fl=[]):return (tp,tg,fl,why)
s=[r(H,D,'deaths by cause'),r(H,D,'deaths by cause'),r(H,D,'child deaths'),r(H,D,'native deaths'),
r(F,['public-debt'],'sinking fund'),r(F,['public-budgets'],'accounts'),r(F,['public-budgets'],'budget'),r(F,['taxation','public-budgets'],'licence receipts'),r(F,['public-budgets'],'overspending')]
s+=[r(F,['taxation','real-estate'],'municipal rate')]*6
s+=[r(F,['taxation','real-estate'],'rate summary'),r(F,['taxation','real-estate'],'assessment reductions'),r(F,['taxation','real-estate'],'assessment increases'),r(F,['taxation','land-registration'],'land lots assessed'),
r(['communications'],['postal-services'],'post office'),
r(['utilities'],['construction'],'concrete mix'),r(RB,['construction','roads-and-bridges'],'bridge tenders'),r(['utilities'],['river-conservancy'],'dredging cost'),r(['utilities'],['river-conservancy'],'dredging cost'),
r(['finance','culture'],['recreation-and-amusements','public-budgets'],'recreation ground accounts'),
r(['population'],['births-and-deaths'],'burials by quarter'),
r(['utilities'],['water-and-sewerage'],'brick drains'),r(['utilities'],['water-and-sewerage'],'pipe drains'),
r(['transportation'],['roads-and-bridges'],'road works'),r(['transportation'],['roads-and-bridges'],'roads widened'),r(['transportation'],['roads-and-bridges'],'road extensions'),
r(['government','finance'],[],'allowance payments in a case'),r(['government','finance'],[],'payments in a case'),
r(['utilities'],['water-and-sewerage'],'water used'),r(['utilities'],['river-conservancy'],'bunding expenditure'),r(['transportation'],['roads-and-bridges'],'proposed roads'),
r(['education','finance'],['education-finance'],'school accounts'),r(['culture'],['arts-and-music'],'band services'),r(['culture'],['arts-and-music'],'orchestra services'),r(['culture'],['arts-and-music'],'band repertoire')]
json.dump(s,open('/dev/stdout','w'))
