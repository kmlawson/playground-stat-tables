from tagA_write import w
F="finance";PB="public-budgets";FE="finance education";EP="education-finance public-budgets";FG="finance government";FT="finance transportation"
w('b09',[
(FE,EP,0,"stores"),(FE,EP,0,"grants in aid to schools"),(FE,PB+" libraries",0,"library"),
(FG,PB,0,"treasurer office"),(FG,PB,0,"compradore"),(FG,PB,0,"stores"),(FG,PB,0,"secretariat pay"),(FG,PB,0,"secretariat"),(FG,PB,0,"tax office pay"),(FG,PB,0,"tax office"),(FG,PB,0,"stores"),
(FG,PB,0,"general charges"),("finance welfare",PB+" charitable-institutions",0,"grants in aid"),(FG,PB,0,"central offices"),(F,PB,0,"rents"),(F,PB,0,"police premises"),
(F,PB,0,"health premises"),(F,PB,0,"PWD premises"),(F,PB,0,"other items"),(F,"public-debt "+PB,0,"interest"),(F,"public-debt",0,"redemption"),
(F,PB+" public-debt",0,"extraordinary income"),(FT,PB+" roads-and-bridges",0,"bridges"),(F+" utilities",PB+" construction",0,"buildings"),
(F+" utilities",PB+" water-and-sewerage",0,"drainage"),(FT,PB+" ports",0,"landing stages"),(F,PB+" real-estate",0,"land"),(F,PB+" construction",0,"buildings"),
(F,PB+" construction",0,"buildings"),(F,PB+" construction",0,"buildings"),(F,PB+" construction",0,"buildings"),(F,PB+" construction",0,"buildings"),(F,PB+" construction",0,"buildings"),
(FT,PB+" roads-and-bridges",0,"roads"),(F,PB,0,"summary"),(F,PB,0,"sterling receipts"),(F,PB,0,"sterling payments"),
(F,"public-debt public-property",0,"balance liabilities"),(F,"public-property",0,"balance assets"),(F,PB,0,"comparative expenditure"),
])
