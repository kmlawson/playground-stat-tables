import json,sys
base='/Users/kml/shell/projects/yearbooks/japanyearbooks/stat-tables-site/build/tags/'
voc=json.load(open(base+'vocabulary.json'))
T={x['id'] for x in voc['topics']};G={x['id'] for x in voc['tags']}
S={}
S['b01']="""
government|local-government|t|committee membership
government|local-government|t|sub-committee reps
government|local-government||meetings per committee
military|army||corps strength by unit
military|army recruitment-and-conscription||joining/leaving
military|recruitment-and-conscription army||reasons leaving
military|army||efficiency return
military|army||efficiency shield points
military|army||musketry return
military|army||musketry points
military|army|t|engineers field work list
military|army honours-and-ranks|t|officer roll
military|army honours-and-ranks|t|promotions
military|army honours-and-ranks|t|commissions renewed
military|army honours-and-ranks|t|commissions issued
military|army honours-and-ranks|t|resignations
military|military-casualties|t|deaths list
military|army|t|strength details roster
military|army||total strength
military|army|t|retired list
military|arms-and-arsenals army||arms and stores on charge
disasters|firefighting|t|fire brigade staff
disasters|firefighting|t|volunteer firemen roster
disasters|firefighting|t|officer changes
disasters|firefighting|t|cup winners
disasters|firefighting honours-and-ranks|t|medals
disasters|firefighting honours-and-ranks|t|medals
disasters|firefighting honours-and-ranks|t|bars
disasters|firefighting|t|cup winners
disasters|firefighting fires||calls by source
disasters|firefighting||motor appliances
disasters|fires firefighting||calls since 1908
disasters|fires firefighting||monthly fires return
disasters|fires||fires by trade and origin
crime-and-justice|police||police authorised strength
crime-and-justice military|police military-casualties|t|police killed in war
crime-and-justice|police honours-and-ranks|t|police honours
crime-and-justice|police||police offences
crime-and-justice|police||Sikh branch strength
crime-and-justice|police||Sikh offences
"""
S['b02']="""
crime-and-justice|police||watchmen supervision
crime-and-justice|police||Chinese branch strength
crime-and-justice|police||CID strength
crime-and-justice|police||fingerprint records
crime-and-justice|police offences-and-convictions||stolen property reports
crime-and-justice transportation|police road-transport||chauffeur permits
transportation crime-and-justice|transport-accidents road-transport||accidents by cause
crime-and-justice|police||mounted branch
crime-and-justice|police|t|animals presented
crime-and-justice|prisons||gaol numbers
crime-and-justice|prisons juvenile-justice||reformatory numbers
crime-and-justice|prisons||prisoners passing through
crime-and-justice|prisons||gaol custody
crime-and-justice|prisons||prisoner localities
crime-and-justice|courts||court sessions
crime-and-justice government|courts government-offices||mixed court staff
crime-and-justice|offences-and-convictions||offence variations
crime-and-justice|offences-and-convictions||handed to Chinese authorities
crime-and-justice|civil-litigation nationality-and-ethnicity||civil cases by nationality
crime-and-justice|civil-litigation courts||foreign civil cases
crime-and-justice|civil-litigation courts||Chinese civil cases
crime-and-justice|courts||security bonds
crime-and-justice|police offences-and-convictions||police action return
crime-and-justice|offences-and-convictions police||arrests not charged
crime-and-justice|offences-and-convictions police||foreigners charged
crime-and-justice|offences-and-convictions courts||mixed court offences
crime-and-justice|courts offences-and-convictions||mixed court sentences
crime-and-justice|offences-and-convictions||arrests 1908-1917
crime-and-justice|prisons||cell prisoners
crime-and-justice|police arms-and-arsenals||arms and equipment
geography population|land-area population-totals||statistical summary
geography|weather||meteorology
health population|births-and-deaths diseases||deaths by cause
health population|births-and-deaths diseases||child deaths by cause
health population|births-and-deaths diseases||total deaths by cause
population health|births-and-deaths nationality-and-ethnicity||deaths by nationality
population health|births-and-deaths age-and-sex||deaths by age
population health|births-and-deaths||death rate
health population|births-and-deaths diseases||Chinese deaths
health|diseases epidemics||notified infectious diseases
"""
S['b03']="""
health|diseases epidemics births-and-deaths||disease deaths 20 yrs
health|vaccination||vaccinations
health|diseases epidemics||scarlet fever
health|diseases epidemics||plague rats
health|diseases epidemics||plague annual
health|public-health epidemics||plague prevention
health|veterinary-health public-health||kennels
health|diseases public-health||lab diagnosis
health|food-inspection||milk samples
health|food-inspection||milk adulteration
health utilities|water-and-sewerage public-health||water analysis
health utilities|water-and-sewerage public-health||water bacteria
health|diseases medical-services||isolation hospital
health|medical-services||nursing home
health|medical-services diseases||police hospitals
health utilities|public-health||refuse disposal
health utilities|public-health||refuse disposal
health|public-health||sanitary work
health|food-inspection veterinary-health||slaughterhouse rejections
health agriculture|food-inspection livestock||slaughterhouse returns
economy trade|prices cost-of-living||prices
trade|markets-and-exchanges||markets
crime-and-justice health|offences-and-convictions food-inspection||prosecutions
health|religious-institutions||cemeteries
health crime-and-justice|births-and-deaths||mortuary
health finance|medical-services construction||hospital tenders
health finance|medical-services construction||hospital cost estimate
health|medical-services||ward beds
health finance|medical-services||hospital finance estimate
health finance|medical-services||hospital finance
health finance|medical-services||hospital finance
health finance|medical-services||hospital finance
health|medical-services||patients treated
health finance|medical-services||working account
finance health|medical-services||balance sheet
crime-and-justice informal-imperialism|offences-and-convictions extraterritoriality|t|offences under regs
transportation|trams||proposed extensions
transportation|trams||service returns
transportation finance|trams||track maintenance payment
transportation finance|trams||track maintenance cost
"""
S['b04']="""
transportation finance|trams||track payment
transportation|trams||track areas
transportation|trams||track length
transportation finance|trams||track cost
transportation finance|trams||track cost
education finance|education-finance||institute accounts
education|schools-and-pupils school-boarding||orphanage pupils
education finance|education-finance||orphanage accounts
education finance|education-finance||school accounts
education|schools-and-pupils school-boarding||pupils fees
education government|schools-and-pupils|t|committee members
education|schools-and-pupils||roll by form
education|schools-and-pupils||roll comparison
education|schools-and-pupils||new pupils
education|schools-and-pupils||withdrawals
education health|schools-and-pupils diseases||school infections
education|teachers schools-and-pupils||staff allocation
education|teachers school-curricula|t|subjects taught
education|schools-and-pupils teachers||summary
education|secondary-education||Cambridge candidates
education|secondary-education||Cambridge entries
sport education|sports-records||football results
sport education|sports-records||cricket match
education|schools-and-pupils||average pupils
education finance|education-finance||high school transfer
education|schools-and-pupils||roll by form
education|schools-and-pupils||roll comparison
education|schools-and-pupils||new pupils
education|teachers||staff allocation
education|teachers school-curricula|t|special subjects
education|schools-and-pupils teachers||autumn term
education|teachers school-curricula|t|special subjects
education|secondary-education||Cambridge results
education|secondary-education|t|Cambridge pass list
education|secondary-education||Cambridge figures
education|schools-and-pupils||roll by form
education|schools-and-pupils||roll comparison
education|schools-and-pupils||new pupils
education|schools-and-pupils||withdrawals
education health|school-boarding diseases||boarder sickness
"""
S['b05']="""
education|teachers schools-and-pupils||forms and teachers
education|school-curricula teachers|t|subjects by teacher
education|school-boarding||boarder menu
education|schools-and-pupils religious-affiliation||religion of boys
education|schools-and-pupils age-and-sex||ages of boys
education|schools-and-pupils nationality-and-ethnicity||nationality of boys
education|schools-and-pupils||roll by form
education|schools-and-pupils||roll comparison
education|schools-and-pupils||new pupils
education|schools-and-pupils||withdrawals
education|schools-and-pupils nationality-and-ethnicity||nationality by age
education health|schools-and-pupils diseases||infectious diseases
education|teachers schools-and-pupils||mistresses by form
education|secondary-education||Cambridge results
education|secondary-education||Cambridge entries
education government|schools-and-pupils|t|committee members
education|schools-and-pupils||roll by term
education|schools-and-pupils||attendance
education|schools-and-pupils||ages admitted
education|schools-and-pupils||roll by term
education|schools-and-pupils||attendance
education|schools-and-pupils||ages admitted
education|schools-and-pupils||ages admitted
education|schools-and-pupils||roll by term
education|schools-and-pupils||attendance
education|schools-and-pupils||ages admitted
education|schools-and-pupils||roll by term
education|schools-and-pupils||attendance
education|schools-and-pupils||ages admitted
education|land-registration||school lots schedule
welfare government|charitable-institutions|t|charity committee
welfare|charitable-institutions nationality-and-ethnicity||cases by nationality
welfare|charitable-institutions||case classes
welfare finance|charitable-institutions||charity accounts
transportation finance|navigation-aids||semaphore accounts
government|government-offices|t|foreign staff personnel
utilities|construction||public works
transportation|roads-and-bridges||bridges
government|land-registration||works department activity
government|land-registration||boundary stone certificates
"""
for b,s in S.items():
    d=json.load(open(base+'runs/new-china-smc-1917/batches/'+b+'.json'))
    L=[l for l in s.strip().split('\n')]
    assert len(L)==len(d),(b,len(L),len(d))
    out=[];n=0
    for l,r in zip(L,d):
        tp,tg,fl,why=l.split('|')
        tp=tp.split();tg=tg.split()
        assert all(x in T for x in tp) and all(x in G for x in tg),(b,l)
        n+=bool(tg)
        out.append({"key":r['key'],"topics":tp,"tags":tg,"flags":["text-tables"] if fl else [],"why":why})
    json.dump(out,open(base+'runs/new-china-smc-1917/results/'+b+'.json','w'),ensure_ascii=False,indent=1)
    print(b,len(out),n)
