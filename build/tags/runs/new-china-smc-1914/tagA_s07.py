from tagA_write import w
F="finance";PB="public-budgets";FM="finance military";FD="finance disasters";FC="finance crime-and-justice"
w('b07',[
(F,"taxation real-estate",0,"houses assessments"),(F,"taxation",0,"wharfage dues"),(F,"taxation",0,"licence excess"),
("transportation","road-transport",0,"motor vehicles"),("transportation "+F,"road-transport taxation",0,"vehicle licences"),
("trade","markets-and-exchanges",0,"market takings"),("transportation","road-transport",0,"ricsha tickets"),
(F,"taxation",0,"Chinese rate"),(F,"taxation real-estate",0,"Chinese houses assessments"),(F,"taxation",0,"licence fees"),(F,"taxation",0,"licence revenue"),
(F,"land-tax "+PB,0,"land tax income"),(F,"taxation "+PB,0,"municipal rate"),(F,"taxation "+PB,0,"wharfage"),(F,"taxation "+PB,0,"licence fees"),
(F,PB+" public-property",0,"rents"),(F,PB,0,"undertakings revenue"),
(FM,PB+" militias-and-volunteer-forces",0,"volunteer pay"),(FM,PB+" militias-and-volunteer-forces",0,"volunteer exp"),
(FM,PB+" militias-and-volunteer-forces",0,"stores"),(FM,PB+" militias-and-volunteer-forces",0,"credit"),
(FD,PB+" firefighting",0,"fire pay"),(FD,PB+" firefighting",0,"stud"),(FD,PB+" firefighting",0,"fire exp"),(FD,PB+" firefighting",0,"stores"),
(FC,PB+" police",0,"police pay"),(FC,PB+" police",0,"Sikh pay"),(FC,PB+" police",0,"Chinese pay"),(FC,PB+" police",0,"medical"),(FC,PB+" police",0,"ponies"),
(FC,PB+" police",0,"light"),(FC,PB+" police",0,"general"),(FC,PB+" prisons",0,"prisoners expenses"),(FC,PB+" police",0,"maintenance"),
(FC,PB+" courts",0,"mixed court"),(FC,PB+" police",0,"stores"),(FC,PB+" police",0,"credit"),(FC,PB+" police",0,"general"),(FC,PB+" police",0,"receipts deducted"),
(F+" health",PB,0,"health office"),
])
