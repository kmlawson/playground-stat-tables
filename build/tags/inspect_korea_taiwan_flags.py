#!/usr/bin/env python3
"""Inspect complete body fields for quantitative content; export review candidates."""
import re
import classify_korea_taiwan as c
ID=re.compile(r'^(?:no\.?|rank|grade|page|vol\.?|year|date|month|day|calendar year|fiscal year|年次|年度|年|月日|年月日|番号|番號|順位|爵|卷|巻|氏名|名稱|姓名|姓|名|就任|設立|創立|創業|成立|開業|建設年月|when built|tenure|telephone|tel\.?|電話)(?:$|[ /・,]+(?:line|district|道別|種類|年月|of office)$)',re.I)
MEASURE=re.compile(r'(?:count|quantity|amount|area|length|width|height|depth|tonnage|distance|cost|price|value|receipts|expenditure|capital|profit|balance|number of|no\. of|enrol|pupil|student|teacher|staff|worker|member|patient|population|total|percent|rate|ratio|age|score|record|points|speed|horsepower|latitude|longitude|數|数|額|量|員|率|價|面積|坪|粁|噸|斤|石|圓|圧|壓|溫|温|馬力|年齡|度數|得點|記錄|年限|金利|利息|東經|北緯|經度|緯度|degrees|里數)',re.I)
VALUE=re.compile(r'^[\s¥$£(（△▲+−—-]*[\d,]+(?:\.\d+)?[\s%％)）]*(?:[a-z.]+)?$',re.I)
QUANTITY=re.compile(r'\d[\d,.]*\s*(?:%|per cent|yen|tons?|kilos?|km\b|miles?|metres?|meters?|feet|students|pupils|persons|men|women|members|[圓円斤瓩石噸坪町里米粁人戶戸])',re.I)

def inspect():
 rs=c.read(c.OUT/'records.json');ps=c.read(c.OUT/'profiles.json');a=c.read(c.OUT/'candidates.json')['assignments'];audit=c.read(c.OUT/'candidate-audit.json');findings=[];flags={}
 for w,p in zip(rs,ps):
  body=w['table'].get('parts',[]);metric=[];values=[]
  for part in body:
   cols=part.get('columns',[])
   for j,col in enumerate(cols):
    if MEASURE.search(str(col)) and not ID.match(str(col)):metric.append(str(col))
   for row in part.get('rows',[]):
    for j,cell in enumerate(row):
     s=str(cell).strip();col=str(cols[j]) if j<len(cols) else ''
     if ID.match(col) or re.search('insignia|shoulder|sleeve',col,re.I):continue
     if VALUE.match(s) or QUANTITY.search(s):values.append(s)
  statistical=bool(metric or values)
  if set(a[w['key']]['tags']) & {'weather','recruitment-and-conscription'}:statistical=True
  if a[w['key']]['topics']==['sport'] and 'sports-records' in a[w['key']]['tags'] and 'Grade' not in p['T']:statistical=True
  if audit[w['key']]['method'] in ['explicit-record-decision','reviewed-body-override','preserved-reviewed-pilot']:flags[w['key']]=a[w['key']]['flags'];continue
  mode=[] if statistical else ['text-tables'];flags[w['key']]=mode
  if mode or (metric and not values):findings.append({'i':p['i'],'key':w['key'],'title':p['T'],'columns':list(dict.fromkeys(col for q in body for col in q.get('columns',[]))),'metric_columns':list(dict.fromkeys(metric)),'numeric_examples':values[:3],'proposed_flags':mode})
 c.write(c.OUT/'body-flag-proposals.json',flags);c.write(c.OUT/'body-flag-review.json',findings)
 print(c.compact({'text_proposed':sum(bool(v) for v in flags.values()),'review_candidates':len(findings)}))
 for f in findings:
  if f['proposed_flags']:print(f['i'],f['title'],'C:',','.join(f['columns'])[:160])
if __name__=='__main__':inspect()
