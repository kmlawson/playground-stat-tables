import json
A={"police-gaols-and-courts":{102:"p0052_1",82:"p0053_1",95:"p0054_1",99:"p0055_1",100:"p0057_1",101:"p0059_1",94:"p0061_1",81:"p0062_1",104:"p0063_1"},
"public-works":{119:"p0119_1",116:"p0125_1",118:"p0129_1",111:"p0132_2",112:"p0132_3",120:"p0133_2"},
"education-orchestra-and-library":{107:"p0184_1",105:"p0197_1",106:"p0198_1"}}
N={"public-works":[("Roads metalled",["china-smc-1885/p0131_1","china-smc-1886/p0140_2","china-smc-1888/p0126_2"]),
("Roads bricked and sanded",["china-smc-1885/p0132_1","china-smc-1886/p0139_2","china-smc-1893/p0205_2"]),
("Roads widened",["china-smc-1885/p0133_1","china-smc-1887/p0145_1"])]}
for f,d in A.items():
    p=f"families/china-smc--{f}.json";J=json.load(open(p))
    for i,t in d.items(): J["families"][i]["members"].insert(0,"china-smc-1885/"+t)
    for lab,m in N.get(f,[]): J["families"].append({"label":lab,"members":m,"note":""})
    json.dump(J,open(p,"w"),ensure_ascii=False,indent=1)
    json.load(open(p))
