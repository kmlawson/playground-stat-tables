from tagA_write import w
PB="public-budgets";FE="finance education";EP="education-finance public-budgets";FG="finance government";F="finance"
FT="finance transportation";FU="finance utilities";CON=PB+" construction";RE=PB+" real-estate"
w('b12',[
(FE,PB+" libraries",0,"library pay"),
(FE,EP,0,"x"),(FE,EP,0,"x"),(FE,EP,0,"x"),(FE,EP,0,"x"),(FE,EP,0,"x"),(FE,EP,0,"x"),(FE,EP,0,"x"),(FE,EP,0,"x"),(FE,EP,0,"x"),(FE,EP,0,"x"),(FE,EP,0,"x"),(FE,EP,0,"x"),(FE,EP,0,"grants to schools"),
(FG,PB,0,"treasurer"),(FG,PB,0,"compradore"),(FG,PB,0,"stores"),(FG,PB,0,"secretariat"),(FG,PB,0,"tax office"),(FG,PB,0,"stores"),(FG,PB,0,"general charges"),
("finance welfare",PB+" charitable-institutions",0,"grants in aid"),
(F,PB+" public-property",0,"rents"),(F,PB+" public-property",0,"rents"),(F,PB+" public-property",0,"rents"),(F,PB+" public-property",0,"rents"),(F,PB+" public-property",0,"rents"),
(F,PB+" public-property",0,"rents"),(F,PB+" public-property",0,"rents"),(F,PB+" public-property",0,"rents"),
(F,"public-debt "+PB,0,"interest"),(F,"public-debt",0,"redemption"),(F,PB,0,"surplus"),(F,PB,0,"deficit"),
(FT,PB+" roads-and-bridges",0,"bridges"),(FU,CON,0,"bundings"),(FU,PB+" water-and-sewerage",0,"drainage"),(F,RE,0,"land fire"),(F,RE,0,"land health"),(F,RE,0,"land parks"),
])
