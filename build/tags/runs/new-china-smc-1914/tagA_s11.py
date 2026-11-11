from tagA_write import w
PB="public-budgets";FC="finance crime-and-justice";FH="finance health";FU="finance utilities"
P=PB+" police";MS=PB+" medical-services"
w('b11',[
(FC,P,0,"foreign pay"),(FC,P,0,"Sikh pay"),(FC,P,0,"Chinese pay"),(FC,P,0,"general"),(FC,P,0,"medical"),(FC,P,0,"ponies"),(FC,PB+" prisons",0,"prisoners"),
(FC,P,0,"police cont"),(FC,P,0,"stores"),
(FH,PB,0,"health office"),(FH,PB+" epidemics",0,"plague"),(FH,PB+" public-health",0,"mosquito"),(FH,PB,0,"less receipts"),
(FH,MS,0,"nursing home"),(FH,MS,0,"isolation"),(FH,MS,0,"isolation Chinese"),(FH,MS,0,"police hosp"),(FH,MS,0,"police hosp"),(FH,MS,0,"sanatorium"),(FH,MS,0,"nursing staff"),
(FH,PB,0,"cemeteries"),(FH,PB,0,"bath"),(FH,MS,0,"medical attendance, grants"),(FH,PB,0,"stores"),
(FU,PB,0,"PWD general"),(FU,PB,0,"buildings"),(FU,PB,0,"police bldgs"),(FU,PB,0,"health bldgs"),(FU,PB,0,"PWD bldgs"),(FU,PB,0,"school bldgs"),
(FU,PB+" rivers-and-waterways",0,"creeks"),(FU,PB+" water-and-sewerage",0,"drainage"),("finance transportation",PB+" roads-and-bridges",0,"roads"),
("finance transportation",PB+" roads-and-bridges",0,"road maintenance"),(FU,PB,0,"cleansing"),(FU,PB+" electricity gas",0,"lighting"),(FU,PB,0,"parks"),(FU,PB,0,"stores"),
("finance culture",PB+" arts-and-music",0,"band pay"),("finance culture",PB+" arts-and-music",0,"band stores"),
])
