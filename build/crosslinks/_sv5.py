import json,sys
for f in ["police-gaols-and-courts","public-works","education-orchestra-and-library"]:
    n="china-smc--"+f
    L={}
    for l in open(f"listings/{n}.txt"):
        p=[x.strip() for x in l.split("|")]
        if len(p)<5: continue
        L[p[0]+"/"+p[1]]=p
    J=json.load(open(f"families/{n}.json"))
    used=set(m for fa in J["families"] for m in fa["members"])
    print("=====",f,len(J["families"]))
    for i,fa in enumerate(J["families"]):
        ms=fa["members"]
        if any(m.startswith(("china-smc-1886","china-smc-1887","china-smc-1893","china-smc-1888")) for m in ms):
            print(i,fa["label"],"|",[m.replace("china-smc-","") for m in ms][:6])
    print("-- unused 1886/1887/1893 older")
    for k,p in L.items():
        if k not in used and k.split("/")[0] in("china-smc-1886","china-smc-1887","china-smc-1888","china-smc-1893"):
            print(k,p[2][:25],"|",p[4][:80])
