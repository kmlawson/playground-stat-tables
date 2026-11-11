from tagA_write import w
PB="public-budgets";F="finance";CON=PB+" construction";RE=PB+" real-estate"
w('b13',[
("finance education",RE+" education-finance",0,"land edu"),(F,CON,0,"buildings"),("finance disasters",PB+" firefighting",0,"fire bldgs"),
("finance crime-and-justice",PB+" police",0,"police bldgs"),("finance health",CON,0,"health bldgs"),(F,CON,0,"PWD bldgs"),(F,CON,0,"parks bldgs"),
("finance education",CON+" education-finance",0,"school bldgs"),("finance transportation",PB+" roads-and-bridges",0,"roads"),(F,PB,0,"summary"),(F,PB,0,"sterling receipts"),(F,PB,0,"sterling payments"),
])
