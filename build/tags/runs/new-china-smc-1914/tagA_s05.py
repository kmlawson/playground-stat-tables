from tagA_write import w
UF="utilities finance";E="electricity";ED="education";SP="schools-and-pupils";SR="sports-records"
w('b05',[
(UF,E,0,"profit pct"),(UF,E,0,"depreciation"),(UF,E,0,"sales profit"),(UF,E,0,"profit pct"),(UF,E,0,"stores"),(UF,E,0,"debtors"),(UF,E,0,"capex"),(UF,E,0,"funds"),
(UF,E,0,"revenue account"),(UF,E,0,"net revenue"),(UF,E,0,"balance sheet"),(UF,E+" public-budgets",0,"estimate"),(UF,E+" public-budgets",0,"pay estimate"),
(UF,E,0,"capex estimate"),("utilities",E,0,"comparative growth"),
(UF,"water-and-sewerage",0,"sewer estimate"),(UF,"water-and-sewerage",0,"sewer estimate"),(UF,"land-reclamation",0,"filling estimate"),(UF,"land-reclamation",0,"sand transport"),
(UF,"water-and-sewerage land-reclamation",0,"drain and fill"),(UF,"land-reclamation",0,"comparative estimates"),(UF,"water-and-sewerage land-reclamation roads-and-bridges",0,"drain fill road"),
("transportation","road-transport",0,"railless car fares"),("transportation","road-transport",0,"cars"),("transportation","road-transport",0,"cars"),
(ED,SP,0,"withdrawals"),(ED,SP,0,"attendance"),(ED,SP,0,"attendance"),(ED,SP,0,"admissions"),(ED,SP,0,"admissions"),
(ED+" health","schools-and-pupils diseases",0,"sickness"),(ED,"education-finance",0,"bursaries"),(ED,"secondary-education",1,"exam results"),(ED,"secondary-education",0,"exam entries"),
("sport "+ED,SR,0,"cricket"),("sport "+ED,SR,0,"cricket match"),("sport "+ED,SR,0,"football"),
(ED,"school-curricula",0,"form timetable"),(ED,"school-curricula",0,"form timetable"),(ED,"school-curricula",0,"form timetable"),
])
