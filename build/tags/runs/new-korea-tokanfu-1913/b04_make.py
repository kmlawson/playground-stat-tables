import json
b=json.load(open('batches/b04.json'))
M={
117:(["forestry"],["afforestation"],"seedlings distributed"),
118:(["forestry","education"],["afforestation"],"school forests area/trees"),
119:(["forestry"],["afforestation"],"nursery seedlings"),
120:(["forestry"],["timber"],"felling hauling rafting"),
121:(["forestry"],["timber"],"sawmilling"),
122:(["forestry"],["timber"],"purchased timber"),
123:(["forestry","trade"],["timber"],"timber sales"),
124:(["forestry"],["timber"],"timber receipts/disbursements"),
125:(["forestry"],["timber"],"timber stock"),
126:(["forestry","labour"],["wages","timber"],"workers and wages"),
127:(["geography","government"],["hunting"],"hunting licences"),
128:(["fisheries","population"],["fishing"],"fishing households"),
129:(["fisheries","population"],["fishing"],"fishing households"),
130:(["fisheries","population"],["fishing"],"fishing population"),
131:(["fisheries"],["fishing"],"fishing vessels"),
132:(["fisheries"],["fishing"],"fishing vessels"),
133:(["fisheries"],[],"processing/transport vessels"),
134:(["fisheries"],["fishing"],"fishing gear"),
135:(["fisheries","government"],["fishing-rights-and-licences"],"fishery applications"),
136:(["fisheries","government"],["fishing-rights-and-licences"],"fishery licences"),
137:(["fisheries"],["fishing"],"vessels crew catch"),
138:(["fisheries"],["fishing"],"catch by species"),
139:(["fisheries"],["fishing"],"catch by gear"),
140:(["fisheries","manufacturing"],["fish-and-fish-products"],"processed marine products"),
141:(["fisheries"],["whaling"],"whaling"),
142:(["fisheries","trade"],["markets-and-exchanges","fish-and-fish-products"],"fish markets"),
143:(["fisheries"],["fishing"],"fishing associations"),
144:(["fisheries"],["fishing"],"visiting fishermen by prefecture"),
145:(["manufacturing","mining"],["salt"],"state salt production"),
146:(["manufacturing","mining"],["salt"],"salt survey"),
147:(["trade"],["salt","imports"],"salt trade"),
148:(["mining","government"],["mining-rights-and-concessions"],"mining applications"),
149:(["mining","government"],["mining-rights-and-concessions"],"mining applications"),
150:(["mining","government"],["mining-rights-and-concessions"],"mining permits"),
151:(["mining"],["mining-rights-and-concessions"],"permitted mining areas"),
152:(["mining"],["mineral-production"],"working/idle mining areas"),
153:(["mining"],["mineral-production"],"working/idle areas by nationality"),
154:(["mining"],["mineral-production"],"mineral output"),
155:(["mining","labour"],["coal"],"Pyongyang mining office"),
156:(["trade"],["business-associations"],"chambers of commerce"),
}
out=[]
for r in b:
    t,g,w=M[int(r['table_no'])]
    out.append({"key":r['key'],"topics":t,"tags":g,"flags":[],"why":w})
json.dump(out,open('results/b04.json','w'),ensure_ascii=False,indent=1)
v=json.load(open('/Users/kml/shell/projects/yearbooks/japanyearbooks/stat-tables-site/build/tags/vocabulary.json'))
print(type(v),list(v)[:5] if isinstance(v,dict) else len(v),len(out),len(b))
