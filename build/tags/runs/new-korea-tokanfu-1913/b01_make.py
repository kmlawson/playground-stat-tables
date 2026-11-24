import json
d=json.load(open('batches/b01.json'))
G=["geography"]
m={
1:(["geography"],["land-area"],"extreme points, area"),
2:(["government","geography"],["administrative-divisions","route-distances"],"provincial divisions, route length"),
3:(["government","geography"],["administrative-divisions"],"jurisdiction areas of provinces"),
4:(["agriculture","finance"],["land-tax","arable-land"],"taxable land area"),
5:(["agriculture","finance"],["land-tax","land-tenure"],"kyol grades and converted area"),
6:(["agriculture"],["arable-land","land-area"],"average converted area paddy/dry"),
7:(["finance","geography"],["land-tax","land-area"],"taxed urban land"),
8:(["government","geography"],["public-property","land-area"],"post-station land"),
9:(["economy","agriculture"],["prices","real-estate"],"land sale prices"),
10:(["economy","agriculture"],["prices","real-estate"],"land rental prices"),
11:(["crime-and-justice","economy"],["land-registration","real-estate"],"real estate certification cases"),
12:(["crime-and-justice","economy"],["land-registration","real-estate"],"certification by type"),
}
W=lambda t:(["geography"],t,"")
out=[]
for i,r in enumerate(d):
    k=r['key']; n=int(k.split(':p')[1][:4]); s=k[-1]
    T=r['en']['t']
    if n<=22:
        idx=[x for x in range(len(d))][i]+1
        t,g,w=m[idx]
    elif n==23 and s in '12':
        t,g,w=(["geography","transportation"],["weather","navigation-aids"] if s=='2' else ["weather"],"station locations")
        if s=='2': g=["storms-and-typhoons","navigation-aids"]; t=["geography","transportation"]
        else: t=["geography","science-and-technology"]
    elif n<=27:
        t,g,w=["geography"],["weather"],"climate elements 1913"
    else:
        t,g,w=["population"],[],""
        if n==28 and s=='1': g=["population-totals","households"];w="households and population"
        elif n==28: g=["age-and-sex"];w="sex ratio"
        elif n==29 and s=='1': g=["nationality-and-ethnicity"];w="nationality ratio"
        elif n==29 and s=='2': g=["population-totals","land-area"];w="density"
        elif n==29 and s=='3': g=["population-totals","overseas-communities"];w="Japanese residents growth"
        elif n==29: g=["age-and-sex","overseas-communities"];w="Japanese by age"
        elif n==30: g=["age-and-sex","overseas-communities"];w="Japanese by age and birth year"
        elif n in(31,32): g=["occupations","overseas-communities"];w="Japanese by occupation"
        elif n==33: g=["migration","overseas-communities"];w="Japanese by home prefecture"
        else: t=["population","colonial-rule"];g=["local-government","overseas-communities"];w="settlers' associations"
    out.append({"key":k,"topics":t,"tags":g,"flags":[],"why":w})
json.dump(out,open('results/b01.json','w'),ensure_ascii=False,indent=1)
v=json.load(open('../../vocabulary.json'));ids={x['id'] for x in v['tags']}|{x['id'] for x in v['topics']}
assert len(out)==len(d) and all(a['key']==b['key'] for a,b in zip(out,d))
print([x for o in out for x in o['topics']+o['tags'] if x not in ids], sum(1 for o in out if o['tags']))
