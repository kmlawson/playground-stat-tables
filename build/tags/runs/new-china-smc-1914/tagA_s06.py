from tagA_write import w
ED="education";SP="schools-and-pupils";F="finance";CW="child-welfare";EF="education-finance"
w('b06',[
(ED,"school-curricula",0,"form IV"),(ED,"school-curricula",0,"form V"),(ED,"school-curricula",0,"form VI"),(ED,"secondary-education",1,"exam results"),(ED,"secondary-education",0,"entries"),
(ED,"",1,"committee"),(F+" "+ED,"securities-and-investment",0,"trust schedule"),(ED,"nationality-and-ethnicity "+SP,0,"nationalities"),(ED,SP,0,"attendance"),(ED,SP,0,"withdrawals"),
(ED+" religion","religious-affiliation "+SP,0,"religions"),(ED,"school-boarding",1,"menus"),(ED,SP+" age-and-sex",0,"ages"),(ED+" health","school-boarding diseases",0,"sickness"),
(ED+" health","teachers",0,"staff sickness"),(ED,"teachers",1,"staff"),(ED,"teachers",1,"staff"),(ED,"teachers "+SP,0,"pupils per teacher"),(ED,EF,0,"fees"),
(ED+" welfare",EF+" "+CW,0,"orphanage accounts"),("welfare "+ED,CW+" nationality-and-ethnicity",0,"children numbers"),("welfare "+ED,CW,0,"orphanage pupils"),
("welfare "+ED,CW+" "+EF,0,"orphanage accounts"),("welfare "+ED,CW+" "+EF,0,"institution accounts"),(ED,EF,0,"reduced fees"),(ED,"",1,"committee members"),
("transportation "+F,"navigation-aids",0,"semaphore accounts"),("government","government-offices",1,"staff roster"),
(F,"public-budgets",0,"surplus"),(F,"public-budgets",0,"statement"),(F,"public-budgets",0,"departments over/under"),
(F+" crime-and-justice","public-budgets police",0,"police pay"),(F+" "+ED,EF+" public-budgets",0,"education cost"),(F,"public-budgets",0,"general charges"),
(F,"public-budgets",0,"extraordinary"),(F,"public-budgets",0,"unbudgeted"),(F,"public-budgets",0,"works profits"),(F,"public-budgets",0,"totals"),
(F,"public-budgets taxation",0,"revenue vs budget"),(F,"land-tax",0,"land tax"),
])
