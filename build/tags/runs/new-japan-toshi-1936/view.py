import json,sys
d=json.load(open(sys.argv[1]))
for i,r in enumerate(d):
    print(f"## [{i}] {r['key']} | {r['title']} | {r['en']['t']} | {r['en']['d']} | ch: {r.get('chapter')} | cap: {r.get('caption_extra')}")
    for p in r['parts']:
        cols=' / '.join(p.get('columns') or [])
        rl=p.get('row_labels') or []
        print(f"  part {p.get('label')}: cols[{cols[:400]}] rows={p.get('rows')} labels[{' ; '.join(rl[:10])[:250]}]")
    for f in (r.get('footnotes') or [])[:3]:
        print("  fn:", f[:160])
