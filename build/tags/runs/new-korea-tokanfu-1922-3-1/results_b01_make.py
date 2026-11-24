import json
d=json.load(open('batches/b01.json'))
v={x['id'] for x in json.load(open('../../vocabulary.json'))['tags']} if False else None
K='korea-tokanfu-1922-3-1:'
m={
'p0005_1':(["economy","finance"],["companies"],"companies by type, capital"),
'p0005_2':(["manufacturing"],["industrial-output","nationality-and-ethnicity"],"factories by owner nationality"),
'p0007_1':(["economy","finance"],["companies","nationality-and-ethnicity"],"companies by type, founder nationality"),
'p0010_1':(["finance"],["insurance-and-pensions"],"life and damage insurance"),
'p0016_1':(["trade"],["markets-and-exchanges","domestic-trade"],"markets and turnover"),
'p0018_1':(["trade","manufacturing"],["tobacco"],"tobacco retail consumption"),
'p0018_2':(["science-and-technology","trade"],["measurement-and-units"],"weights/measures sellers"),
'p0019_1':(["science-and-technology","trade"],["measurement-and-units"],"weights/measures sales"),
'p0019_2':(["manufacturing"],["industrial-output"],"factories, capital, workers, power"),
'p0025_1':(["manufacturing"],["industrial-output"],"value of industrial products by province"),
'p0027_1':(["utilities"],["electricity","companies"],"electric utilities, capacity"),
'p0028_1':(["education","manufacturing"],["vocational-education","textiles"],"local industrial training institutes"),
'p0028_2':(["economy","labour"],["prices","wages"],"average prices and wages"),
'p0031_1':(["economy","trade"],["prices","rice"],"unhulled rice prices"),
'p0033_1':(["economy","trade"],["prices","rice"],"brown rice prices"),
'p0035_1':(["economy","trade"],["prices","rice"],"polished rice prices"),
'p0037_1':(["economy","trade"],["prices","soybeans"],"soybean prices"),
'p0040_1':(["economy","trade"],["prices","barley"],"barley prices"),
'p0042_1':(["economy","trade"],["prices","wheat"],"wheat prices"),
'p0044_1':(["economy","trade"],["prices"],"commodity prices by town"),
'p0046_1':(["labour"],["wages"],"wages by trade and town"),
}
out=[]
for r in d:
    t,g,w=m[r['key'].split(':')[1]]
    out.append({"key":r['key'],"topics":t,"tags":g,"flags":[],"why":w})
json.dump(out,open('results/b01.json','w'),ensure_ascii=False,indent=1)
print(len(out))
