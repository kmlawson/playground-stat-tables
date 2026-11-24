import json
b=json.load(open('batches/b09.json'))
P,S,H,V,T,TT,F,SP='primary-education','secondary-education','higher-education','vocational-education','teachers','teacher-training','education-finance','schools-and-pupils'
m={318:([P,SP],'attendance'),319:([P,F],'school accounts'),320:([P],'school property'),321:([P,T],'teacher pay'),
322:([S,SP,TT],'middle schools + teacher training'),323:([S],'property'),324:([S,SP],'girls high schools'),325:([S],'property'),
326:([V,SP],'commercial schools'),327:([V,SP],'simplified vocational'),328:([V],'property'),329:([H,SP],'colleges'),330:([SP],'misc schools'),
331:([SP,P,S],'Korean school inventory'),332:([P,SP,T],'state common'),333:([P,SP,T],'public common'),334:([P,SP],'admissions graduates'),
335:([P,SP],'dropouts deaths'),336:([P,SP],'attendance'),337:([P],'property'),338:([P,T],'teacher pay'),339:([P,SP,T],'private common'),
340:([S,SP],'higher common'),341:([S],'property'),342:([S,SP],'girls'),343:([S],'property'),344:([S,SP],'private higher common'),345:([S,SP],'private girls'),
346:([TT,SP],'teacher training'),347:([V,SP,T],'vocational'),348:([V],'property'),349:([V,SP],'simplified vocational'),
350:([V,SP],'Keijo training school'),351:([V],'property'),352:([H,SP],'medical college'),353:([H],'property'),354:([H,V],'technical college'),355:([H],'property'),356:([H,V],'agri college'),357:([H],'property')}
out=[]
for r in b:
    n=int(r['table_no']); tg,w=m[n]
    tp=['education']
    if n==319: tp=['education','finance']
    out.append({'key':r['key'],'topics':tp,'tags':tg[:3],'flags':[],'why':w})
json.dump(out,open('results/b09.json','w'),ensure_ascii=False,indent=1)
v=json.load(open('/Users/kml/shell/projects/yearbooks/japanyearbooks/stat-tables-site/build/tags/vocabulary.json'))
ids={t['id'] for t in v['tags']}|{t['id'] for t in v['topics']}
print(len(out),all(r['key']==x['key'] for r,x in zip(b,out)),[i for o in out for i in o['topics']+o['tags'] if i not in ids])
