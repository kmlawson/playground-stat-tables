#!/usr/bin/env python3
"""Local, auditable classification aids for Korea and Taiwan. No model calls."""
import argparse, ast, hashlib, json, re, unicodedata
from collections import Counter, defaultdict
from pathlib import Path
from prepare_pilot import collection, digest
from run_china_sonnet import row_issues
HERE=Path(__file__).resolve().parent
SITE=HERE.parent.parent
OUT=HERE/'runs/korea-taiwan-direct-2026-10-26'
VOCAB=HERE/'runs/china-sonnet-2026-10-26/vocabulary.json'

def read(p):return json.loads(p.read_text())
def write(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def compact(x):return json.dumps(x,ensure_ascii=False,separators=(',',':'))
def load():
 bs=next(n.value for n in ast.parse((SITE/'build/build_site.py').read_text()).body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='BOOKS' for t in n.targets))
 records=[];sources={};books=[]
 for n in bs.elts:
  f={k.value:v for k,v in zip(n.keys,n.values) if isinstance(k,ast.Constant)};slug=ast.literal_eval(f['slug']);group=collection(slug,f)
  if group not in ('korea','taiwan'):continue
  path=SITE/'data'/f'{slug}.json';tables=read(path);sources[str(path.relative_to(SITE))]=sha(path)
  book={'slug':slug,'title':ast.literal_eval(f['title']),'collection':group};books.append({**book,'tables':len(tables)})
  records.extend({'key':slug+':'+t['id'],'book':book,'table':t} for t in tables)
 return records,sources,books

def norm(title):
 s=unicodedata.normalize('NFKC',title).lower();s=re.sub(r'\d[\d.,]*','#',s)
 return re.sub(r'[^\w#]+',' ',s).strip()
def prepare():
 if OUT.exists():raise ValueError('Already prepared')
 OUT.mkdir(parents=True);rs,sources,books=load();assert len(rs)==6594
 write(OUT/'records.json',rs);write(OUT/'vocabulary.json',read(VOCAB))
 groups={};profiles=[]
 for i,w in enumerate(rs):
  t=w['table'];en=t.get('en') or {};title=en.get('t') or t['title'];key=norm(title)
  if key not in groups:groups[key]={'g':len(groups),'keys':[],'indices':[],'title':title}
  groups[key]['keys'].append(w['key']);groups[key]['indices'].append(i)
  parts=[]
  for p in t.get('parts',[]):
   rows=p.get('rows',[]);example=next((r for r in rows if sum(bool(x) for x in r)>1), rows[0] if rows else [])
   parts.append({'label':p.get('label'),'columns':p.get('columns',[]),'n':len(rows),'example':example})
  profiles.append({'i':i,'g':groups[key]['g'],'key':w['key'],'T':title,'J':t['title'],'D':en.get('d'),'chapter':t.get('chapter'),'P':parts,'caption':t.get('caption_extra'),'context':t.get('context'),'footnotes':t.get('footnotes')})
 write(OUT/'profiles.json',profiles);write(OUT/'groups.json',list(groups.values()))
 write(OUT/'manifest.json',{'schema_version':1,'classifier':'assistant-direct-with-audited-rules','tables':len(rs),'books':books,'source_files':sources,'vocabulary_version':read(VOCAB)['vocabulary_version'],'records_sha256':sha(OUT/'records.json'),'vocabulary_sha256':sha(OUT/'vocabulary.json'),'inputs':{w['key']:digest({'book':w['book'],'table':w['table']}) for w in rs}})
 (OUT/'decisions.tsv').write_text('# indices|topics|tags|s or t|rationale\n')
 print(compact({'tables':len(rs),'books':len(books),'groups':len(groups)}))
def show(start,count,lean=False):
 ps=read(OUT/'profiles.json')[start:start+count]
 for p in ps:
  if lean:
   print(compact({'i':p['i'],'T':p['T'],'J':p['J'],'C':list(dict.fromkeys(c for q in p['P'] for c in q['columns'])),'R':[[q['label'],q['n'],q['example']] for q in p['P']]}))
  else:print(compact(p))
def full(i):print(compact(read(OUT/'records.json')[i]))
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('action',choices=['prepare','show','lean','full']);ap.add_argument('--start',type=int,default=0);ap.add_argument('--count',type=int,default=30);a=ap.parse_args()
 {'prepare':prepare,'show':lambda:show(a.start,a.count),'lean':lambda:show(a.start,a.count,True),'full':lambda:full(a.start)}[a.action]()
