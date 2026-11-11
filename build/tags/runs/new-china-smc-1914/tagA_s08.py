from tagA_write import w
FH="finance health";PB="public-budgets";FU="finance utilities";FE="finance education";EP="education-finance public-budgets"
MS=PB+" medical-services"
w('b08',[
(FH,PB+" epidemics",0,"plague"),(FH,PB+" public-health",0,"mosquito"),(FH,PB,0,"receipts"),
(FH,MS,0,"nursing home"),(FH,MS,0,"isolation"),(FH,MS,0,"isolation chinese"),(FH,MS,0,"police hospital"),(FH,MS,0,"police hospital"),(FH,MS,0,"sanatorium"),
(FH,PB,0,"cemeteries"),(FH,PB,0,"bath"),(FH,PB+" medical-services",0,"medical attendance"),(FH,PB,0,"stores"),
(FU,PB,0,"PWD general"),(FU,PB,0,"buildings"),(FU,PB,0,"police buildings"),(FU,PB,0,"health buildings"),(FU,PB,0,"PWD buildings"),(FU,PB,0,"school buildings"),
(FU,PB+" rivers-and-waterways",0,"creeks"),(FU,PB+" water-and-sewerage",0,"drainage"),("finance transportation",PB+" roads-and-bridges",0,"roads"),
(FU,PB,0,"cleansing"),(FU,PB+" electricity gas",0,"lighting"),(FU,PB,0,"parks"),(FU,PB,0,"stores"),(FU,PB,0,"credit"),
("finance culture",PB+" arts-and-music",0,"band"),("finance culture",PB+" arts-and-music",0,"band stores"),
(FE,EP,0,"boys school"),(FE,EP,0,"stores"),(FE,EP,0,"girls school"),(FE,EP,0,"stores"),(FE,EP,0,"Hanbury boys"),(FE,EP,0,"Hanbury girls"),
(FE,EP,0,"Hanbury fees"),(FE,EP,0,"stores"),(FE,EP,0,"Chinese school"),(FE,EP,0,"stores"),(FE,EP,0,"Kadoorie school"),
])
