from tagA_write import w
M='military';V='militias-and-volunteer-forces'
w('b01',[
("government","local-government",1,"committee lists"),
("government","local-government",1,"sub-committee reps"),
("government","local-government",0,"committee meetings"),
(M,V,0,"corps strength"),(M,V,0,"reasons leaving"),(M,V,0,"efficiency shield"),(M,V,0,"parade attendance"),(M,V,0,"camp"),
(M,V,1,"officer roll"),(M,V,1,"commissions"),(M,V,1,"commissions"),(M,V,1,"resignations"),(M,V,1,"staff list"),
(M,V,0,"strength"),(M,V,1,"retired list"),
(M,"arms-and-arsenals "+V,0,"stores"),(M,"arms-and-arsenals "+V,0,"ammunition"),
(M,V,1,"inspection papers list"),(M,V,0,"parade state"),(M+" population","nationality-and-ethnicity "+V,0,"corps by nationality"),
("disasters","firefighting",1,"fire brigade officers"),("disasters","firefighting",1,"attendance cups"),
("disasters","firefighting",0,"equipment"),("disasters","firefighting",0,"appliances added"),
("disasters","fires firefighting",0,"call record"),("disasters","fires firefighting",0,"call summary"),
("crime-and-justice","police",0,"police strength"),("crime-and-justice","police offences-and-convictions",0,"offences by police"),
("crime-and-justice","police",0,"Sikh branch"),("crime-and-justice","police offences-and-convictions",0,"offences by Sikh police"),
("crime-and-justice","police",0,"watchmen"),("crime-and-justice","police",0,"Chinese branch"),
("crime-and-justice","police",0,"mounted branch"),("crime-and-justice","police",1,"animals presented"),
("crime-and-justice","police",0,"CID strength"),("crime-and-justice","police",0,"ID office staff"),
("crime-and-justice","offences-and-convictions police",0,"larcenies by station"),
("crime-and-justice","prisons",0,"gaol"),("crime-and-justice","prisons",0,"gaol population"),("crime-and-justice","prisons",0,"prisoners localities"),
])
