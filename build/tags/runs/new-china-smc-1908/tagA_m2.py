import json,re,sys
sys.path.insert(0,'.')
from tagA_common import *
rules=[ # (regex on title+chapter, topics, tags, text, why) first match wins
("Donors of Seeds","government","",1,"list of donors"),
("^Municipal Properties","government","public-property land-area",0,"properties with areas"),
("Roads: Land and Construction","transportation finance","roads-and-bridges real-estate",0,"road land/construction cost"),
("Soochow Road|Agricultural Land Purchased|Native-Owned Country Land|Amended Calculation","transportation finance","roads-and-bridges real-estate",0,"land bought for roads"),
("Amounts Annually Receivable|Amounts Annually Payable","finance","public-property",1,"annual rents/payments by party"),
("Lots within Settlement Limits|French Registered Lots","government","land-registration",1,"lot numbers list"),
("Public Lighting: Reduced","utilities","electricity",0,"lighting charges"),
("Load Factor|Units Sold|Increase over 1907|Comparative Table","utilities","electricity",0,"electricity output/load"),
("Tenders for","utilities","electricity",1,"switchboard tenders"),
("Analysis of Costs","utilities finance","electricity",0,"electricity costs"),
("Electricity Department","finance utilities","electricity",0,"electricity accounts"),
("Estimate for 1908","finance utilities","electricity public-budgets",0,"electricity estimate"),
("Houses Licensed for Closing","narcotics","opium-licensing",0,"opium houses closing"),
("Charges in Other Cities","communications","telephone",0,"telephone charges"),
("Schedule of Charges","communications","telephone",0,"telephone charges"),
("Semaphore","communications transportation","navigation-aids",0,"semaphore account"),
("Committee of the Public School","education","schools-and-pupils",1,"school committee"),
("Evening Classes","education","school-curricula",1,"class subjects list"),
("Attendance of Pupils|New Pupils","education","schools-and-pupils",0,"pupils"),
("Cambridge","education","secondary-education",0,"exam results"),
("Pay Scale|Extra Pay|Period of Service|Deferred Pay","government crime-and-justice","wages police",0,"pay scales"),
("Personnel of the Municipal","government","government-offices",1,"staff roster"),
("Pingchiao Quarry","finance mining","mineral-production companies",0,"quarry account"),
("Convict Labour","finance crime-and-justice","prison-labour",0,"convict labour account"),
("Concreteware","finance manufacturing","cement-and-bricks",0,"concreteware works account"),
("Police Recreation|Gurdwara","finance","",0,"fund account"),
("^Land$","finance","public-property land-area",0,"municipal land value"),
("^Buildings$|Stock and Stores$","finance","public-property",0,"municipal property value"),
("Balance Sheet","finance","public-budgets",0,"balance sheet"),
("Wharfage Dues$","trade finance","tariffs",0,"wharfage rates"),
("Licence Fees$","finance","taxation",0,"licence fee schedule"),
("Slaughter-house|Special Permit|Export Fees|Water Supply|Market Fees|Permit Fees","finance","taxation",0,"fee schedule"),
("Volunteer Corps — Strength","military finance","militias-and-volunteer-forces",0,"corps strength and cost"),
("Redemption of Debentures","finance","public-debt",0,"debenture redemption"),
("Sterling","finance","public-budgets foreign-loans",0,"sterling accounts"),
("Rent of Municipal","finance","public-property",0,"rent of municipal property"),
("Rates, Taxes","finance","taxation public-budgets",0,"rates comparison"),
("Summary of Estimated","finance","public-budgets",0,"budget summary"),
("Comparative Statement of Expenditure","finance","public-budgets",0,"expenditure comparison"),
("Land Tax|General Municipal Rate","finance","taxation land-tax",0,"rate income"),
("Statement Totals|Totals","finance","public-budgets",0,"budget totals"),
("Extraordinary Receipts|Extraordinary Income","finance","public-budgets",0,"extraordinary income"),
("Extraordinary Payments|Extraordinary Expenditure","finance","public-budgets",0,"extraordinary expenditure"),
("Ordinary Income|Ordinary Receipts|Financial Statement.*Ordinary R","finance","public-budgets",0,"ordinary income"),
]
dept=[("Police","crime-and-justice finance","police public-budgets"),("Health|Hospitals|Cemeter","health finance","public-health public-budgets"),
("Public Works|Public Work","finance","public-budgets construction"),("Secretariat","government finance","government-offices public-budgets"),
("Volunteer","military finance","militias-and-volunteer-forces public-budgets"),("Fire Brigade","disasters finance","firefighting public-budgets"),
("Educational|Education","education finance","education-finance public-budgets"),("Interest|Redemption","finance","public-debt public-budgets"),
("Public Band","culture finance","arts-and-music public-budgets")]
def classify(r):
    s=r['title']+' | '+(r['chapter'] or '')
    for pat,t,g,f,w in rules:
        if re.search(pat,r['title']) : return (t,g,f,w)
    if re.search('Ordinary Payments|Ordinary Expenditure|Financial Statement',s):
        for pat,t,g in dept:
            if re.search(pat,r['title']): return (t,g,0,"expenditure by department")
        return ("finance","public-budgets",0,"municipal expenditure")
    return None
def build(b):
    M={}
    for r in json.load(open(f'{HERE}/batches/{b}.json')):
        c=classify(r)
        s=r['key'].split(':')[1]
        if c is None: print('UNMATCHED',s,r['title']); continue
        M[s]=c
    return M
