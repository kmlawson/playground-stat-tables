import json,sys
n=sys.argv[1];kws=sys.argv[2:]
f=json.load(open(f'families/{n}.json'))
inf={m:i for i,fa in enumerate(f['families']) for m in fa['members']}
for l in open(f'listings/{n}.txt'):
    p=l.split(' | ')
    if len(p)<7 or not p[0].startswith('japan-keishicho'):continue
    if any(k in p[4] for k in kws): print(p[0][-4:],p[1],inf.get(p[0]+'/'+p[1]),p[4][:100],'||',p[6][:110])
