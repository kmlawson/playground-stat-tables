#!/usr/bin/env python3
"""Generate auditable candidates from explicitly authored subject rules and decisions."""
import argparse,re
from collections import Counter
import classify_korea_taiwan as c
from run_china_sonnet import row_issues
RULES=c.HERE/'korea_taiwan_rules.tsv'

def priority(rule):
 id_,rx,topics,tags,reason=rule
 if id_ in ['public-debt-specific','judicial-stamps','veterinary-epidemics','mission-schools','professional-schools','traditional-village-school','special-schools','primary-national-schools','national-language-school','reformatory','child-rearing','relief-institute','disaster-relief','work-relief-erosion','heritage-treasures','prison-work-accounts','nav-rivers','charity-organisations','company-directory','indigenous-population','population-occupation2']:return 3
 if id_ in ['school-associations','opium-licences','mixed-narcotics','fertilizer-use','sport-participants','news-agency','indigenous-school','population-work','farmhouseholds','lawyers']:return 2
 if id_ in ['units','units-jp','calendar','chronology','land-survey','property-certification','real-estate-certification','land-registration']:return 1
 if id_ in ['public-budgets','public-officials','local-government','construction','total-area','special-accounts']:return 90
 if id_ in ['press-censorship','school-finance','medical-training','prison-labour','veterinary','anti-epizootic','monopoly-finance']:return 4
 if 'finance' in topics and id_ not in ['companies','public-buildings']:return 5
 if id_ in ['fishing2']:return 50
 if id_ in ['narcotics','opium','morphine','elections','honours']:return 10
 if id_ in ['markets','companies','incorporations','manufacturing','forestry-management','population']:return 70
 if topics[0] in ['trade']:return 20
 if topics[0] in ['crime-and-justice','religion','health','education','communications','transportation','military']:return 25
 if topics[0] in ['geography','population','government','welfare','labour','economy','disasters']:return 30
 return 40

def enrich(row,p,w):
 """Explicit subordinate subjects supported by body structure, not incidental prose."""
 title=p['T'];t=w['table'];cols=' '.join(str(x) for q in t.get('parts',[]) for x in q.get('columns',[]))
 labels=' '.join(str(q.get('label') or '') for q in t.get('parts',[]))
 add=[]
 if row['topics']==['population']:
  if re.search('population.{0,45}occupation|households.{0,45}occupation',title,re.I):row['tags']=['occupations']
  if re.search('households|dwellings|houses',title,re.I) and 'households' not in row['tags']:add.append('households')
  if re.search('age|sex|male|female|男|女',cols,re.I):add.append('age-and-sex')
 if row['topics'][0]=='education' and re.search('teachers|faculty|教員|敎員',title+' '+cols,re.I):add.append('teachers')
 if re.search('by occupation',title,re.I) and 'occupations' not in row['tags']:add.append('occupations')
 people=bool(set(row['topics']) & {'population','education','labour','crime-and-justice','religion','health','government','indigenous-peoples'})
 people=people or bool(re.search('depositors|savings|subscribers|farm households|farmers',title,re.I))
 if people and re.search('Japanese|Koreans?|Taiwanese|內地人|内地人|朝鮮人|本島人|外國人|外国人',cols+' '+labels,re.I):
  groups=re.findall('Japanese|Koreans?|Taiwanese|內地人|内地人|朝鮮人|本島人|外國人|外国人',cols+' '+labels,re.I)
  if len(set(x.lower() for x in groups))>=2:add.append('nationality-and-ethnicity')
 if row['topics']==['narcotics'] and re.search('cultivation|poppy',title,re.I):row['topics'].append('agriculture')
 if 'trams' in row['tags'] and re.search('light rail',title,re.I):add.append('railways')
 if row['topics']==['religion'] and re.search('adherents|believers|converts|信徒',title+' '+cols,re.I):
  add.insert(0,'religious-affiliation')
 if row['topics']==['government'] and re.search('government.general',title,re.I):
  row['topics'].append('colonial-rule');add.insert(0,'colonial-administration')
 for tag in add:
  if tag not in row['tags'] and len(row['tags'])<3:row['tags'].append(tag)
 if row['topics']==['agriculture','manufacturing'] and re.search('consumption|consumed',title,re.I):
  row['topics']=['agriculture'];row['tags']=['farm-inputs']
 return row

def build():
 rs=c.read(c.OUT/'records.json');ps=c.read(c.OUT/'profiles.json');vocab=c.read(c.OUT/'vocabulary.json');rules=[]
 for line in RULES.read_text().splitlines():
  if not line or line.startswith('#'):continue
  id_,rest=line.split('|',1);pattern,topics,tags,reason=rest.rsplit('|',3)
  rules.append((id_,re.compile(pattern,re.I),topics.split(','),tags.split(',') if tags else [],reason))
 rules.sort(key=priority)
 manual={}
 for line in (c.OUT/'decisions.tsv').read_text().splitlines():
  if not line or line.startswith('#'):continue
  spans,topics,tags,mode,reason=line.split('|',4)
  for span in spans.split(','):
   bounds=list(map(int,span.split('-')))
   for i in range(bounds[0],bounds[-1]+1):
    if i in manual:raise ValueError('Duplicate authored index '+str(i))
    manual[i]={'topics':topics.split(','),'tags':tags.split(',') if tags else [],'flags':['text-tables'] if mode=='t' else [],'rationale':reason,'review_questions':[] if tags else ['No precise approved detailed tag fits; retained for later user review.']}
 assignments={};audit={};unmatched=[]
 for p,w in zip(ps,rs):
  i=p['i'];key=w['key'];title=p['T']+' '+p['J']
  if i in manual:
   assignments[key]=manual[i];audit[key]={'method':'explicit-record-decision','index':i};continue
  for id_,rx,topics,tags,reason in rules:
   if rx.search(title):
    assignments[key]={'topics':list(topics),'tags':list(tags),'flags':[],'rationale':reason,'review_questions':[]}
    assignments[key]=enrich(assignments[key],p,w)
    audit[key]={'method':'authored-subject-rule','rule':id_,'index':i};break
  else:unmatched.append(i)
 overrides_path=c.OUT/'reviewed-overrides.json'
 if overrides_path.exists():
  for position,row in c.read(overrides_path).items():
   i=int(position);key=rs[i]['key'];assignments[key]=row
   audit[key]={'method':'reviewed-body-override','index':i}
 pilot=c.read(c.HERE/'pilot/assignments.json')
 pilot_inputs={x['key']:x for x in c.read(c.HERE/'pilot/manifest.json')['tables']}
 for i,w in enumerate(rs):
  key=w['key']
  if key in pilot['assignments']:
   if c.digest({'book':w['book'],'table':w['table']})!=pilot_inputs[key]['input_sha256']:raise ValueError('Pilot source changed '+key)
   assignments[key]=pilot['assignments'][key]
   audit[key]={'method':'preserved-reviewed-pilot','index':i,'pilot_id':pilot['pilot_id']}
 result={'schema_version':1,'vocabulary_version':vocab['vocabulary_version'],'review_status':'candidates-requiring-cohort-review','assignments':assignments}
 issues=row_issues(result,{'keys':list(assignments)},vocab)
 if issues:raise ValueError(issues)
 c.write(c.OUT/'candidates.json',result);c.write(c.OUT/'candidate-audit.json',audit);c.write(c.OUT/'unmatched.json',unmatched)
 print(c.compact({'candidates':len(assignments),'unmatched':len(unmatched),'manual':len(manual),'rules':dict(Counter(v.get('rule','manual') for v in audit.values()))}))

def unmatched(start,count):
 ps=c.read(c.OUT/'profiles.json');ids=c.read(c.OUT/'unmatched.json')[start:start+count]
 for i in ids:
  p=ps[i]; print(c.compact({'i':i,'T':p['T'],'J':p['J'],'C':list(dict.fromkeys(x for q in p['P'] for x in q['columns'])),'R':[[q['label'],q['n'],q['example']] for q in p['P']]}))
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('action',choices=['build','unmatched']);ap.add_argument('--start',type=int,default=0);ap.add_argument('--count',type=int,default=30);a=ap.parse_args();build() if a.action=='build' else unmatched(a.start,a.count)
