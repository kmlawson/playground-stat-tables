from tagA_write import w
U="utilities";F="finance";RB="roads-and-bridges"
w('b04',[
(U,"construction",0,"stone despatched"),(U,"construction",0,"monthly stone"),("manufacturing","cement-and-bricks",0,"concreteware"),
("government","public-property",0,"municipal properties"),(F+" transportation",RB,0,"land and road cost"),(F+" transportation",RB,0,"cost by road"),
(F+" government","real-estate",0,"claim"),(F+" government","real-estate",0,"compensation"),(F+" government","real-estate",0,"compensation"),
("transportation "+F,RB+" real-estate",0,"improvements"),(F+" transportation","real-estate "+RB,0,"compensation lots"),
(F+" transportation","real-estate "+RB,0,"agri land purchases"),(F+" government","real-estate",0,"land commission award"),(F+" government","real-estate",0,"award"),
("government","",1,"commissioners"),(F,"real-estate",0,"settlement"),(F+" government","real-estate",0,"award"),("government","",1,"commissioners"),
(F,"real-estate",0,"rent claim"),(F,"real-estate",0,"claim"),(F,"real-estate",0,"claim"),("transportation "+F,"real-estate "+RB,0,"improvements"),
("government","",1,"commission meetings"),("government","",1,"commission meetings"),
("culture","recreation-and-amusements",0,"recreation ground users"),("forestry "+U,"afforestation",0,"road trees"),("forestry","afforestation",0,"nurseries"),
("forestry","afforestation",0,"nursery land"),("agriculture culture","horticulture",0,"flowering plants"),("culture","",0,"turf"),("forestry","afforestation",0,"parks planting"),
(U+" "+F,"electricity",0,"works costs"),(U+" "+F,"electricity",0,"works costs"),(U,"electricity",0,"mains"),(U,"electricity",0,"street lamps"),(U,"electricity",0,"street lamps"),
(U,"electricity",0,"horse power"),(U,"electricity",0,"units sold"),(U,"electricity",0,"units at works"),(U+" "+F,"electricity",0,"profit"),
])
