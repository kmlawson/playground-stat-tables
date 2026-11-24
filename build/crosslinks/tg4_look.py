import sys,re
n=sys.argv[1]; ids=set(sys.argv[2:])
for l in open(f'listings/korea-tokei--{n}.txt'):
    p=[x.strip() for x in l.split('|')]
    if len(p)<8: continue
    if p[1] in ids:
        t=re.sub(r'\[EN: (Table \d+: )?','[',re.sub(r'^Table \d+\. ','',p[4]))
        print(p[0][-4:],p[1],t[:80],'||',p[6][:int(260)],'||',p[7][:60])
