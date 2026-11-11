from tagA_write import w
CJ="crime-and-justice";H="health";HP="health population"
w('b02',[
(CJ,"police",0,"traffic staff"),("transportation "+CJ,"transport-accidents",0,"accidents"),("transportation","trams",0,"tram passengers"),
("transportation","road-transport",0,"motor cars"),(CJ,"courts police",0,"mixed court staff"),(CJ,"offences-and-convictions courts",0,"persons charged"),
(CJ,"courts",0,"petitions"),(CJ,"civil-litigation courts nationality-and-ethnicity",0,"civil cases"),
(CJ,"police offences-and-convictions",0,"police action"),(CJ,"offences-and-convictions police",0,"arrests"),
(CJ,"offences-and-convictions police",0,"apprehended"),(CJ,"offences-and-convictions courts",0,"mixed court"),
(CJ,"courts offences-and-convictions",0,"sentences"),(CJ,"offences-and-convictions",0,"arrests 1905-14"),
(CJ,"prisons police",0,"cells"),(CJ,"police arms-and-arsenals",0,"arms issued"),
("geography population","land-area population-totals",0,"summary"),("geography","weather",0,"meteorology"),
(HP,"births-and-deaths diseases",0,"deaths by cause"),(HP,"births-and-deaths diseases",0,"child deaths"),(HP,"births-and-deaths diseases",0,"foreign deaths"),
("population health","births-and-deaths nationality-and-ethnicity",0,"deaths by nationality"),("population health","births-and-deaths age-and-sex",0,"deaths by age"),
(HP,"births-and-deaths",0,"death rate"),(HP,"births-and-deaths diseases",0,"Chinese deaths"),
(H,"diseases epidemics",0,"notifications"),(H,"diseases epidemics",0,"infectious deaths"),(H,"vaccination",0,"vaccinations"),
(H,"epidemics diseases",0,"rats plague"),(H,"epidemics public-health",0,"plague prevention"),(H,"veterinary-health public-health",0,"rabies kennels"),
(H,"diseases public-health",0,"lab diagnosis"),(H,"food-inspection",0,"milk water"),(H,"food-inspection",0,"milk adulteration"),
("utilities health","water-and-sewerage public-health",0,"water analysis"),(H,"diseases medical-services",0,"isolation hospital"),(H,"medical-services",0,"nursing home"),
(H,"medical-services diseases",0,"police hospital"),(H+" "+CJ,"medical-services diseases",0,"gaol hospital"),("utilities health","public-health",0,"refuse disposal"),
])
