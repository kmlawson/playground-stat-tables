import sys
for l in open(sys.argv[1]):
    p=l.rstrip('\n').split(' | ')
    if len(p)>=7 and p[0].startswith('korea'):
        print(p[0][-2:],p[1],p[4].split(' [EN')[0][:70],'|',p[6][:80])
    elif l.startswith('##'): print(l.strip())
