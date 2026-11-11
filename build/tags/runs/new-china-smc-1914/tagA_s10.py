from tagA_write import w
F="finance";PB="public-budgets";FM="finance military";FD="finance disasters";V=" militias-and-volunteer-forces"
TP="taxation public-budgets"
w('b10',[
(F+" mining","",0,"quarry accounts"),(F+" mining","",0,"quarry balance"),
(F+" crime-and-justice","prison-labour",0,"convict labour"),(F+" crime-and-justice","prison-labour",0,"convict balance"),
(F+" manufacturing","cement-and-bricks",0,"concreteware"),(F+" manufacturing","cement-and-bricks",0,"concreteware balance"),
(F+" manufacturing","",0,"workshop"),(F+" manufacturing","",0,"workshop balance"),(F,"",0,"adjustment account"),
(F+" crime-and-justice","police",0,"police fund"),(F+" religion","religious-institutions",0,"gurdwara fund"),
(F+" government","public-property real-estate",0,"land schedule"),(F+" government","public-property",0,"buildings schedule"),(F+" government","public-property",0,"stores schedule"),
(F,PB,0,"summary"),(F+" trade","taxation tariffs",0,"wharfage rates"),(F,"taxation",0,"licence fees"),
(F+" health","taxation food-inspection",0,"slaughter fees"),(F+" health","taxation food-inspection",0,"permit fees"),(F+" health","taxation food-inspection",0,"export fees"),
("utilities "+F,"water-and-sewerage",0,"water fees"),(F+" trade","markets-and-exchanges taxation",0,"market fees"),(F,"taxation construction",0,"permit fees"),
(F,"land-tax "+PB,0,"land tax"),(F,TP,0,"rate"),(F,TP,0,"rate"),(F,TP,0,"advert rate"),(F,TP,0,"wharfage"),(F,TP,0,"licences"),
(F,PB+" public-property",0,"rents"),(F,PB,0,"undertakings"),
(FM,PB+V,0,"pay"),(FM,PB+V,0,"pay"),(FM,PB+V,0,"items"),(FM,PB+V,0,"stores"),(FM,PB+V,0,"credit"),
(FD,PB+" firefighting",0,"fire pay"),(FD,PB+" firefighting",0,"stud"),(FD,PB+" firefighting",0,"items"),(FD,PB+" firefighting",0,"stores"),
])
