#!/usr/bin/env python3
"""Validate and save Korea and Taiwan classifications; never invoke models or build pages."""
from collections import Counter
from copy import deepcopy
import classify_korea_taiwan as c
from run_china_sonnet import row_issues,now


def main():
 out=c.OUT;manifest=c.read(out/'manifest.json');rs=c.read(out/'records.json');v=c.read(out/'vocabulary.json')
 assert c.sha(out/'records.json')==manifest['records_sha256']
 assert c.sha(out/'vocabulary.json')==manifest['vocabulary_sha256']
 current,sources,books=c.load()
 assert sources==manifest['source_files']
 assert {w['key']:c.digest({'book':w['book'],'table':w['table']}) for w in current}==manifest['inputs']
 a=deepcopy(c.read(out/'candidates.json')['assignments']);audit=c.read(out/'candidate-audit.json');flags=c.read(out/'body-flag-proposals.json')
 flag_overrides=c.read(out/'flag-overrides.json')
 assert len(rs)==len(a)==6594 and set(a)=={w['key'] for w in rs}
 pilot=c.read(c.HERE/'pilot/assignments.json')['assignments']
 for w in rs:
  key=w['key']
  if audit[key]['method']=='authored-subject-rule':a[key]['flags']=flags[key]
  if key in flag_overrides:a[key]['flags']=flag_overrides[key]
  if not a[key]['tags'] and not a[key]['review_questions']:
   a[key]['review_questions']=['No precise approved detailed tag fits; retained for later user review.']
  if key in pilot:assert a[key]==pilot[key],key
  audit[key]['input_sha256']=manifest['inputs'][key]
  audit[key]['flags']=a[key]['flags']
  audit[key]['flag_method']='preserved-calibration' if key in pilot else 'reviewed-body-content-and-structure'
 result={'schema_version':1,'classifier':'assistant-direct-with-authored-rules','vocabulary_version':v['vocabulary_version'],
         'review_status':'draft-for-user-review','assignments':a}
 problems=row_issues(result,{'keys':[w['key'] for w in rs]},v)
 if problems:raise ValueError(problems)
 c.write(out/'assignments.korea-taiwan.json',result)
 brief=[]
 for w in rs:
  key=w['key'];brief.append({'key':key,'book':w['book'],'title':(w['table'].get('en') or {}).get('t') or w['table']['title'],**a[key]})
 for group in ['korea','taiwan']:
  subset={w['key']:a[w['key']] for w in rs if w['book']['collection']==group}
  c.write(out/f'assignments.{group}.json',{**result,'collection':group,'assignments':subset})
 c.write(out/'no-detailed-tags.json',{'count':sum(not r['tags'] for r in brief),'tables':[r for r in brief if not r['tags']]})
 c.write(out/'review-queue.json',{'count':sum(bool(r['review_questions']) for r in brief),'tables':[r for r in brief if r['review_questions']]})
 c.write(out/'provenance.json',{'schema_version':1,'tables':audit})
 (out/'rules.applied.tsv').write_bytes((c.HERE/'korea_taiwan_rules.tsv').read_bytes())
 collection_counts={g:sum(w['book']['collection']==g for w in rs) for g in ['korea','taiwan']}
 book_counts={g:sum(b['collection']==g for b in books) for g in ['korea','taiwan']}
 summaries={g:{'tables':collection_counts[g],'books':book_counts[g],
   'without_details':sum(w['book']['collection']==g and not a[w['key']]['tags'] for w in rs),
   'text_tables':sum(w['book']['collection']==g and bool(a[w['key']]['flags']) for w in rs)} for g in collection_counts}
 validation={'status':'complete','tables':len(a),'books':len(books),'collections':summaries,
   'vocabulary_version':v['vocabulary_version'],'vocabulary_counts':{k:len(v[k]) for k in ['topics','tags','flags']},
   'additional_llm_cli_calls':0,'preserved_calibration_tables':sum(k in pilot for k in a),
   'methods':dict(Counter(x['method'] for x in audit.values())),
   'without_detailed_tags':sum(not r['tags'] for r in a.values()),'text_tables':sum(bool(r['flags']) for r in a.values()),
   'checks':{'exact_key_coverage':True,'approved_ids_and_cardinalities':True,'all_39_source_hashes_unchanged':True,
             'all_input_fingerprints_match':True,'frozen_vocabulary_unchanged':True,'calibration_assignments_preserved_exactly':True},
   'semantic_checks':['Reviewed subject rule families and unmatched subjects using bilingual titles, all column labels and body profiles.',
      'Read full ambiguous and generic records, and corrected specificity and priority collisions.',
      'Inspected all complete body fields for quantitative measures versus identifiers; reviewed textual candidates and traditional-numeral exceptions.',
      'Checked explicit Indigenous subjects, colonial institutions, school finance, narcotic licensing and tram/light-rail boundaries.',
      'Compared all 62 exact-source calibration assignments and preserved their existing decisions.'],
   'issues':[],'validated_utc':now(),'source_files':sources,
   'implementation_sha256':{p.name:c.sha(p) for p in [c.HERE/'classify_korea_taiwan.py',c.HERE/'apply_korea_taiwan_rules.py',c.HERE/'inspect_korea_taiwan_flags.py',c.HERE/'finalize_korea_taiwan.py']},
   'output_sha256':{name:c.sha(out/name) for name in ['assignments.korea-taiwan.json','assignments.korea.json','assignments.taiwan.json','no-detailed-tags.json','review-queue.json','provenance.json','rules.applied.tsv','decisions.tsv','reviewed-overrides.json']}}
 c.write(out/'validation.json',validation)
 rows=[]
 for book in books:
  count=sum(w['book']['slug']==book['slug'] for w in rs)
  assert count==book['tables']
  rows.append(f"| {book['title']} | {count:,} |")
 report=f"""# Korea and Taiwan table classifications

Saved classifications for **{len(a):,} tables in {len(books)} volumes**.

| Collection | Volumes | Tables | Without detailed tags | Text tables |
|---|---:|---:|---:|---:|
| Korea | {book_counts['korea']} | {collection_counts['korea']:,} | {summaries['korea']['without_details']} | {summaries['korea']['text_tables']} |
| Taiwan | {book_counts['taiwan']} | {collection_counts['taiwan']:,} | {summaries['taiwan']['without_details']} | {summaries['taiwan']['text_tables']} |

## Files

- [Combined Korea and Taiwan assignments](assignments.korea-taiwan.json)
- [Korea assignments](assignments.korea.json) and [Taiwan assignments](assignments.taiwan.json)
- [Tables without detailed tags](no-detailed-tags.json)
- [Review questions](review-queue.json)
- [Per-table provenance](provenance.json) and [validation](validation.json)
- [Applied subject rules](rules.applied.tsv), [explicit decisions](decisions.tsv),
  [body-review overrides](reviewed-overrides.json) and [body flag review](body-flag-review.json)

## Method

The assistant performed a local, rule-assisted classification pass with **no LLM CLI
calls** and no external classification service. Explicitly authored subject rules
handle repeated table families; bilingual titles and English descriptions are used
with original columns, part labels and body profiles. Every complete JSON record was
parsed, and all body fields were inspected programmatically for quantities and identifiers.
Ambiguous headings, orphaned continuations, special accounts, directories and boundary
cases were reviewed in full as needed. This is a scalable subject-rule pass, not a
claim that every numerical cell was individually reread by the assistant.

The **62 existing calibration assignments** whose complete input fingerprints exactly
match these records are preserved verbatim. All remaining assignments retain the
applied rule or explicit record decision in provenance. These are draft classifications
for user evaluation. Structural validation does not establish perfect semantic accuracy.

The vocabulary is unchanged: **32 high-level topics and 327 detailed tags**, version
`{v['vocabulary_version']}`. Each record has 1–2 topics, 0–3 detailed tags and an independent
`text-tables` flag. **{validation['without_detailed_tags']} records** have no fitting or
sufficiently supported detail and are left for later review. Missing numerical bodies
remain statistical when their headings and context establish the intended quantities.

Topics describe the table subject; ordinary colonial-era demographic and productive
statistics do not automatically receive a colonial-rule tag. Indigenous-specific
statistics, formal colonial institutions and guard-line policing are treated separately.
Street trams remain distinct from conventional and light railways. Dedicated school
finance and licensed opium commerce follow the agreed classification boundaries.

## Validation and scope

Passed exact coverage and uniqueness for all **6,594 keys**, approved vocabulary IDs,
cardinality limits, all 39 original file hashes, all record fingerprints, frozen
vocabulary checks, and preservation of the 62 calibration assignments. No OCR or Git
operations were used. Original source data, existing China classifications, website
pages and Topics navigation were not changed.

The separate four-agent review of the 380 China tables without details is advisory;
its proposed vocabulary additions have not been incorporated into this run.

## Volumes

| Volume | Tables |
|---|---:|
{chr(10).join(rows)}
| **Total** | **6,594** |
"""
 (out/'REPORT.md').write_text(report)
 print(c.compact({k:validation[k] for k in ['status','tables','books','collections','preserved_calibration_tables','methods','without_detailed_tags','text_tables','issues']}))

if __name__=='__main__':main()
