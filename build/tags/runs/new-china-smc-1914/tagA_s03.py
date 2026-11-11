from tagA_write import w
U="utilities";H="health";F="finance"
w('b03',[
(U+" "+H,"public-health",0,"refuse"),(H,"public-health",0,"sanitary work"),(H,"food-inspection veterinary-health",0,"slaughter rejections"),
(H+" agriculture","food-inspection livestock",0,"slaughter"),("trade","prices",0,"prices"),("trade","markets-and-exchanges",0,"markets"),
("crime-and-justice "+H,"offences-and-convictions food-inspection",0,"prosecutions"),(H,"",0,"cemeteries"),(H+" crime-and-justice","",0,"mortuary"),
(H,"medical-services",1,"signatories"),(H,"medical-services",0,"patients"),(H,"medical-services",0,"cases"),
(H+" "+F,"medical-services",0,"hospital accounts"),(H+" "+F,"medical-services",0,"balance sheet"),
("transportation","roads-and-bridges",0,"bridges"),("government","land-surveys",0,"survey work"),("government","land-surveys",0,"boundary stones"),
(F,"land-tax",0,"new lots taxed"),("government","land-surveys",0,"areas revised"),("transportation","roads-and-bridges land-surveys",0,"road lots"),
("government","land-surveys",0,"plans"),("transportation","roads-and-bridges",0,"road surfacing"),("transportation","roads-and-bridges",0,"road mileage"),
("transportation","roads-and-bridges",0,"footways"),(U,"",0,"plant"),(U+" "+H,"",0,"sweepings"),(U,"water-and-sewerage",0,"water use"),
(U+" disasters","water-and-sewerage firefighting",0,"hydrants"),(U,"water-and-sewerage",0,"mains"),("labour","employment-and-unemployment",0,"men employed"),
("welfare","nationality-and-ethnicity poor-relief",0,"casual ward"),("welfare","poor-relief",0,"casual ward stone"),(U,"rivers-and-waterways",0,"dredging"),
(U,"gas",0,"gas lamps"),(U,"electricity",0,"electric lamps"),(U+" crime-and-justice","electricity gas",0,"lamp fines"),
(U,"construction",0,"permits"),(U,"construction",0,"new buildings"),(U,"construction",0,"building work"),(U,"construction",0,"permits"),
])
